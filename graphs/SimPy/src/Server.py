import simpy
from Logger import Logger
from Utils import *
import StorageDevice
from Contract import Contract
from StorageDevice import StorageDevice, DiskIdNotation
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
        self.server_manager = server_manager
        self.HDDs_data = []
        self.HDDs_metadata = []
        self.receiving_files = {}  # Dict[str, Deque[CML_oid]]
        self.__parts = {}  # Dict[str, List[FileParts]

        self.__network_buffer_size = int(misc_params[Contract.M_NETWORK_BUFFER_SIZE_KB])
        self.__show_requests = bool(config[Contract.S_SHOW_REQUESTS])
        self.__disk_target_gen = self.target_disk_generator()
        data_disk_gen = DiskIdNotation.get_disk_id_generator(self.__id, True)
        for i in range(config[Contract.S_HDD_DATA_COUNT]):
            self.HDDs_data.append(StorageDevice(
                env, next(data_disk_gen),
                config[Contract.S_HDD_DATA_CAPACITY_GB] * 1e6,
                config[Contract.S_HDD_DATA_READ_MBPS] * 1e3,
                config[Contract.S_HDD_DATA_WRITE_MBPS] * 1e3,
                config[Contract.S_HDD_DATA_LATENCY_MS],
                self
            ))

        # with unsigned short int a single disk can contain 8 TB of a file. This is not limiting the simulator
        # in any case. Better save some memory
        self.__cmloids_per_disk = {}  # Dict(str, int)
        self.__disk_content = []  # List(deque((parity_id: int, parity_map: int))]
        for i in range(self.config[Contract.S_HDD_DATA_COUNT]):
            self.__disk_content.append(deque())
        self.__recovery_targets = 0
        # self.hdd_data = StorageDevice(config[Contract.S_HDD_DATA_CAPACITY_GB] * 2e9,
        #                               config[Contract.S_HDD_DATA_BW_MB_PER_SEC] * 2e3,
        #                               config[Contract.S_HDD_DATA_LATENCY_MS])
        # self.hdd_metadata = StorageDevice(config[Contract.S_HDD_METADATA_CAPACITY_GB] * 2e9,
        #                                   config[Contract.S_HDD_METADATA_BW_MB_PER_SEC] * 2e3,
        #                                   config[Contract.S_HDD_METADATA_LATENCY_MS])

    def get_id(self):
        return self.__id

    def __add_file_parts(self, parts: List[FilePart]):
        for part in parts:
            if part.get_filename() in self.__parts:
                self.__parts[part.get_filename()].append(part)
            else:
                self.__parts[part.get_filename()] = [part]

    def get_data_disks(self):
        return self.HDDs_data

    def get_metadata_disks(self):
        return self.HDDs_metadata

    def get_load_per_disk(self, file: File) -> List[int]:
        """
        Get how data is supposed to be distributed over the disks.
        Size is rounded up to a multiple of CML_oid size.
        :param file: file to be written
        :return: List[int] where len(return) = len(HDDs_data)
        """
        disk_count = len(self.HDDs_data)
        cmloid_count = ceil(file.get_size() / CML_oid.get_size())
        min_load = int(cmloid_count / disk_count) * CML_oid.get_size()
        load = [min_load for i in range(disk_count)]
        for i in range(int(cmloid_count % disk_count)):
            load[i] += CML_oid.get_size()
        return load

    def get_load_from_chunk(self, chunk: Chunk) -> List[int]:
        cmloid_size = WriteRequest.get_cmloid_size()
        cmloid_count = int(ceil(chunk.get_size() / cmloid_size))
        min_load = int(floor(cmloid_count / len(self.HDDs_data)) * cmloid_size)
        load = [min_load] * len(self.HDDs_data)
        for i in range(cmloid_count % len(self.HDDs_data)):
            load[i] += cmloid_size
        return load

    def print_file_map(self, filename: str):
        # Clients knows the server that has their data but
        # the server can have received a parity instead of the actual file
        if filename in self.__cmloids_per_disk:
            print(self.__cmloids_per_disk[filename])

    def __track_cmloids(self, request: WriteRequest):
        # parts = deepcopy(parts_original)
        sliceable_list = SliceablePartList()
        parts = request.get_parts()
        parity_id = request.get_parity_id()
        parity_group = request.get_parity_group()
        for part in parts:
            sliceable_list.add_part(part)

        current_disk = next(self.__disk_target_gen)
        while sliceable_list.has_parts():
            filenames_in_cmloid = sliceable_list.pop_buffer(CML_oid.get_size())
            for filename in filenames_in_cmloid:
                if filename not in self.__cmloids_per_disk:
                    self.__cmloids_per_disk[filename] = array('H', [0] * self.config[Contract.S_HDD_DATA_COUNT])
                self.__cmloids_per_disk[filename][current_disk] += 1
                self.__disk_content[current_disk].append((parity_id, parity_group))
            current_disk = next(self.__disk_target_gen)

    def process_write_request(self, request: WriteRequest) -> int:
        """
        Simulate the file writing
        :param request: the write request
        :return: the effective time of the writing
        """
        # max data a single disk has to write. The bottleneck of this process
        mutex_req = self.__mutex.request()
        start = self.env.now
        yield mutex_req
        self.logger.add_task_time("wait-to-write", self.env.now - start)

        self.__track_cmloids(request)
        max_load = int(ceil(request.get_size() / len(self.HDDs_data)))
        write_time = Function2D.disk_interaction(max_load, self.HDDs_data[0].get_writing_bandwidth())
        yield self.env.timeout(write_time)
        self.logger.add_task_time("disk-write", write_time)
        self.__add_file_parts(request.get_parts())
        # self.env.process(self.server_manager.answer_client(request))

        self.__mutex.release(mutex_req)
        return write_time

    def process_read_request(self, request: ReadRequest) -> int:
        """
        Process a read request
        :param request: the read request
        :return: the number of cmloids the server owns at the current time and the read time
        """
        requested_filename = request.get_filename()
        if requested_filename not in self.__cmloids_per_disk:
            yield self.env.timeout(0)
            return 0

        mutex_req = self.__mutex.request()
        start = self.env.now
        yield mutex_req
        self.logger.add_task_time("wait-to-read", self.env.now - start)

        max_load = max(self.__cmloids_per_disk[requested_filename]) * CML_oid.get_size()
        # print("Reading at most {} cmloids per device".format(max(self.__cmloids_per_disk[requested_filename])))
        read_time = Function2D.disk_interaction(max_load, self.HDDs_data[0].get_reading_bandwidth())
        yield self.env.timeout(read_time)
        self.logger.add_task_time("disk-read", read_time)

        self.__mutex.release(mutex_req)
        total_cmloids = sum(self.__cmloids_per_disk[requested_filename])

        if self.__show_requests:
            print("<{:3d}> {}, read {} cmloids ({} KB)".format(self.__id, request, total_cmloids, total_cmloids * CML_oid.get_size()))
        return total_cmloids

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

        print(ids_to_gather)
        self.__recovery_targets ^= 1 << self.__id
        self.logger.add_object_count('parity-groups-to-gather', len(ids_to_gather))
        self.server_manager.send_recovery_request(ids_to_gather, self.__recovery_targets)
        yield self.env.timeout(0)

    def receive_recovery_data(self, from_id: int):
        self.__recovery_targets ^= 1 << from_id
        if self.__recovery_targets == 0:
            # self.env.timeout(len(self.))
            self.server_manager.server_finished_restoring()

    def gather_and_send_parity_groups(self, ids_to_gather: set()):
        # computing load per disk
        load = array('H', [0]*len(self.__disk_content))
        disk_id = 0
        print("Server", self.__id)
        for disk in self.__disk_content:
            print(disk)
            for id, map in disk:
                if id in ids_to_gather:
                    load[disk_id] += 1
                else:
                    print("skipped", id)
            disk_id += 1
        print()

        # read simulation
        request = self.__mutex.request()
        yield request
        read_time = Function2D.disk_interaction(max(load), self.HDDs_data[0].get_reading_bandwidth())
        yield self.env.timeout(read_time)
        self.logger.add_task_time("recovery-disk-read", read_time)
        print("Server {} read {} cmloids".format(self.__id, sum(load)))
        self.logger.add_object_count('cmloids-read', sum(load))
        self.__mutex.release(request)

        # network simulation
        network_time = yield self.env.process(self.server_manager.perform_network_transaction(sum(load) * CML_oid.get_size()))
        self.logger.add_task_time("send-same-parity-group", network_time)

        self.server_manager.receive_recovery_request(self.__id)


    def target_disk_generator(self):
        lookup_table = generate_lookup_table(len(self.__disk_content))
        index = 0
        while True:
            yield lookup_table[index]
            index = (index + 1) % len(lookup_table)



