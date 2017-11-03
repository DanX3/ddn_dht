import simpy
from Logger import Logger
from Utils import *
from Contract import Contract
from collections import deque
from Interfaces import IfForServer
from array import array
from FunctionDesigner import Function2D


class Server:
    def __init__(self, env, id: int, logger: Logger, config, misc_params, server_manager: IfForServer):
        self.env = env
        self.__id = id
        self.logger = logger
        self.config = config
        self.__mutex = simpy.Resource(env, capacity=1)
        self.__manager = server_manager
        self.receiving_files = {}  # Dict[str, Deque[CML_oid]]
        self.__parts = {}  # Dict[str, List[FileParts]

        self.__network_buffer_size = int(misc_params[Contract.M_NETWORK_BUFFER_SIZE_KB])
        self.__show_requests = bool(config[Contract.S_SHOW_REQUESTS])
        self.__disk_target_gen = round_robin_gen(config[Contract.S_HDD_DATA_COUNT])
        self.__disk_interaction = Function2D.get_bandwidth_model(
            config[Contract.S_HDD_DATA_LATENCY_US],
            config[Contract.S_HDD_DATA_WRITE_MBPS])
        self.__cached_metadata = deque()
        self.__backup_metadata = deque()
        self.__metadata_propagation_timeout = None

        # with unsigned short int a single disk can contain 8 TB of a file. This is not limiting the simulator
        # in any case. Better save some memory
        self.__cmloids_per_disk = {}  # Dict(str, int)
        self.__disk_content = []  # List(deque((parity_id: int, parity_map: int))]
        for i in range(self.config[Contract.S_HDD_DATA_COUNT]):
            self.__disk_content.append(deque())
        self.__recovery_targets = 0


    def get_id(self):
        return self.__id

    def __add_file_parts(self, parts: List[FilePart]):
        for part in parts:
            if part.get_filename() in self.__parts:
                self.__parts[part.get_filename()].append(part)
            else:
                self.__parts[part.get_filename()] = [part]

    def get_load_per_disk(self, file: File) -> List[int]:
        """
        Get how data is supposed to be distributed over the disks.
        Size is rounded up to a multiple of CML_oid size.
        :param file: file to be written
        :return: List[int] where len(return) = len(HDDs_data)
        """
        disk_count = len(self.config[Contract.S_HDD_DATA_COUNT])
        cmloid_count = ceil(file.get_size() / CML_oid.get_size())
        min_load = int(cmloid_count / disk_count) * CML_oid.get_size()
        load = [min_load for i in range(disk_count)]
        for i in range(int(cmloid_count % disk_count)):
            load[i] += CML_oid.get_size()
        return load

    def print_file_map(self, filename: str):
        # Clients knows the server that has their data but
        # the server can have received a parity instead of the actual file
        if filename in self.__cmloids_per_disk:
            print(self.__cmloids_per_disk[filename])

    def __track_cmloids(self, request: WriteRequest):
        sliceable_list = SliceablePartList()
        parts = request.get_parts()
        parity_id = request.get_parity_id()
        parity_group = request.get_parity_group()
        sliceable_list.add_parts(parts)

        current_disk = next(self.__disk_target_gen)
        while sliceable_list.has_parts():
            filenames_in_cmloid = sliceable_list.pop_buffer(CML_oid.get_size())
            for filename in filenames_in_cmloid:
                if filename not in self.__cmloids_per_disk:
                    self.__cmloids_per_disk[filename] = array('H', [0] * self.config[Contract.S_HDD_DATA_COUNT])
                self.__cmloids_per_disk[filename][current_disk] += 1
                self.__disk_content[current_disk].append((parity_id, parity_group))
            current_disk = next(self.__disk_target_gen)

    def __perform_journal_operation(self, request: WriteRequest):
        yield self.env.timeout(request.get_size())

    def receive_metadata_backup(self, packed_metadata):
        # print(self.__id, 'received metadata len', len(packed_metadata))
        self.__backup_metadata += packed_metadata
        yield self.env.timeout(self.__disk_interaction(len(packed_metadata)))

    def __send_cached_metadata(self):
        backup_target = (self.__id + 1) % self.__manager.get_server_count()
        yield self.env.process(self.__manager.perform_network_transaction(len(self.__cached_metadata)))
        yield self.env.process(self.__manager.propagate_metadata(self.__cached_metadata, backup_target))
        self.__cached_metadata.clear()

    def __metadata_timeout(self):
        try:
            yield self.env.timeout(int(1e9))
            if len(self.__cached_metadata) > 0:
                self.env.process(self.__send_cached_metadata())
        except simpy.Interrupt:
            print(self.__id, 'Prevented timeout from sending partial data')

    def __propagate_metadata(self, request: WriteRequest):
        self.__cached_metadata += request.get_parts()
        self.logger.add_task_time("cache-metadata", 10)

        # if request.is_eager_commit():
        #     print(self.__id, 'eager commit')
        #
        # if len(self.__cached_metadata) >= self.config[Contract.S_METADATA_CACHING_THRESHOLD]:
        #     print(self.__id, 'length reached')

        if request.is_eager_commit() \
                or len(self.__cached_metadata) >= self.config[Contract.S_METADATA_CACHING_THRESHOLD]:
            if self.__metadata_propagation_timeout is not None \
                    and self.__metadata_propagation_timeout.is_alive:
                self.__metadata_propagation_timeout.interrupt()
            yield self.env.process(self.__send_cached_metadata())
        else:
            pass
            # self.__metadata_propagation_timeout = self.env.process(self.__metadata_timeout())

    def __control_plane(self, request: WriteRequest):
        journal = self.env.process(self.__perform_journal_operation(request))
        metadata = self.env.process(self.__propagate_metadata(request))
        yield simpy.AllOf(self.env, [journal, metadata])

    def process_write_request(self, request: WriteRequest) -> int:
        data = self.env.process(self.__data_plane(request))
        control = self.env.process(self.__control_plane(request))
        yield simpy.AllOf(self.env, [data, control])
        self.__manager.answer_client_write(request)

    def __data_plane(self, request: WriteRequest) -> int:
        """
        Simulate the file writing
        :param request: the write request
        :return: the effective time of the writing
        """
        # max data a single disk has to write. The bottleneck of this process
        mutex_req = self.__mutex.request()
        yield mutex_req

        self.__track_cmloids(request)
        max_load = int(ceil(request.get_size() / len(self.__disk_content)))
        write_time = Function2D.disk_interaction(max_load, self.config[Contract.S_HDD_DATA_WRITE_MBPS])
        yield self.env.timeout(write_time)
        self.logger.add_task_time("disk-write", write_time)
        self.__add_file_parts(request.get_parts())
        # self.env.process(self.server_manager.answer_client(request))

        self.__mutex.release(mutex_req)
        return write_time

    def process_read_requests(self, requests):
        processes = []
        for single_request in requests:
            process = self.env.process(self.process_read_request(single_request))
            processes.append(process)
        yield simpy.AllOf(self.env, processes)

    def process_read_request(self, request: ReadRequest) -> int:
        """
        Process a read request
        :param request: the read request
        :return: the number of cmloids the server owns at the current time and the read time
        """
        if __debug__:
            assert request.get_filename() in self.__cmloids_per_disk, \
            "Server: filename not owned, Client should know who to ask for the files"

        requested_filename = request.get_filename()
        mutex_req = self.__mutex.request()
        yield mutex_req

        max_load = max(self.__cmloids_per_disk[requested_filename]) * CML_oid.get_size()
        # print("Reading at most {} cmloids per device".format(max(self.__cmloids_per_disk[requested_filename])))
        read_time = Function2D.disk_interaction(max_load, self.config[Contract.S_HDD_DATA_WRITE_MBPS])
        yield self.env.timeout(read_time)
        self.logger.add_task_time("disk-read", read_time)

        self.__mutex.release(mutex_req)
        total_cmloids = sum(self.__cmloids_per_disk[requested_filename])

        if self.__show_requests:
            print("<{:3d}> {}, read {} cmloids ({} KB)".format(self.__id, request, total_cmloids, total_cmloids * CML_oid.get_size()))
        self.__manager.answer_client_read(request)

    def process_disk_failure(self, disk_id: int = None):
        """
        Simualtes the failure of a disk, retrieving from all the network the data needed to apply
        erasure coding
        :param disk_id: the disk id that has stopped working. A random one if not specified
        """
        if disk_id is None:
            disk_id = randint(0, self.config[Contract.S_HDD_DATA_COUNT])

        ids_to_gather = set()
        self.__recovery_targets = 0
        for id, map in self.__disk_content[disk_id]:
            ids_to_gather.add(id)
            self.__recovery_targets |= map

        # print(ids_to_gather)
        self.__recovery_targets ^= 1 << self.__id
        self.logger.add_object_count('parity-groups-to-gather', len(ids_to_gather))
        self.__manager.send_recovery_request(ids_to_gather, self.__recovery_targets)
        yield self.env.timeout(0)

    def receive_recovery_data(self, from_id: int):
        self.__recovery_targets ^= 1 << from_id
        if self.__recovery_targets == 0:
            # self.env.timeout(len(self.))
            self.__manager.server_finished_restoring()

    def gather_and_send_parity_groups(self, ids_to_gather: set()):
        # computing load per disk
        load = array('H', [0]*len(self.__disk_content))
        disk_id = 0
        # print("Server", self.__id)
        for disk in self.__disk_content:
            for id, map in disk:
                if id in ids_to_gather:
                    load[disk_id] += 1
            disk_id += 1

        # read simulation
        request = self.__mutex.request()
        yield request
        read_time = Function2D.disk_interaction(max(load), self.config[Contract.S_HDD_DATA_WRITE_MBPS])
        yield self.env.timeout(read_time)
        self.logger.add_task_time("recovery-disk-read", read_time)
        self.logger.add_object_count('cmloids-read', sum(load))
        self.__mutex.release(request)

        # network simulation
        network_time = yield self.env.process(self.__manager.perform_network_transaction(sum(load) * CML_oid.get_size()))
        self.logger.add_task_time("send-same-parity-group", network_time)

        self.__manager.receive_recovery_request(self.__id)

