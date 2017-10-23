import simpy
from Logger import Logger
from Utils import *
import StorageDevice
from Contract import Contract
from StorageDevice import StorageDevice, DiskIdNotation
from collections import deque
from Interfaces import IfForServer
from array import array


class Server:
    def __init__(self, env, id: int, logger: Logger, config, misc_params, server_manager: IfForServer):
        self.env = env
        self.id = id
        self.logger = logger
        self.config = config
        self.__mutex = simpy.Resource(env, capacity=1)
        self.server_manager = server_manager
        self.__requests = deque()
        self.HDDs_data = []
        self.HDDs_metadata = []
        self.receiving_files = {}  # Dict[str, Deque[CML_oid]]
        self.__parts = {}  # Dict[str, List[FileParts]

        self.__network_buffer_size = int(misc_params[Contract.M_NETWORK_BUFFER_SIZE_KB])
        self.lookup_table = generate_lookup_table(32)
        data_disk_gen = DiskIdNotation.get_disk_id_generator(self.id, True)
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
        self.__cmloids_per_disk = {}  # dict[str, array[unsigned short]]
        # self.hdd_data = StorageDevice(config[Contract.S_HDD_DATA_CAPACITY_GB] * 2e9,
        #                               config[Contract.S_HDD_DATA_BW_MB_PER_SEC] * 2e3,
        #                               config[Contract.S_HDD_DATA_LATENCY_MS])
        # self.hdd_metadata = StorageDevice(config[Contract.S_HDD_METADATA_CAPACITY_GB] * 2e9,
        #                                   config[Contract.S_HDD_METADATA_BW_MB_PER_SEC] * 2e3,
        #                                   config[Contract.S_HDD_METADATA_LATENCY_MS])

    def get_queue_length(self):
        if self.is_available:
            return 0
        else:
            return len(self.resource.queue)

    def get_id(self):
        return self.id

    def __process_read_request(self, req):
        req.get_client().receive_answer(req)
        raise MethodNotImplemented("Server")

    def __track_cmloids(self, parts: List[FilePart]):
        sliceable_list = SliceablePartList()
        for part in parts:
            sliceable_list.add_part(part)

        current_disk = 0
        while sliceable_list.has_parts():

            parts_in_cmloid = sliceable_list.pop_buffer(CML_oid.get_size())
            for part in parts_in_cmloid:
                if part.get_filename() not in self.__cmloids_per_disk:
                    self.__cmloids_per_disk[part.get_filename()] = array('H', [0] * self.config[Contract.S_HDD_DATA_COUNT])
                self.__cmloids_per_disk[part.get_filename()][current_disk] += 1
            current_disk = (current_disk + 1) % len(self.HDDs_data)

    def __process_write_request(self, request: WriteRequest):
        # max data a single disk has to write. The bottleneck of this process
        mutex_req = self.__mutex.request()
        yield mutex_req
        self.__track_cmloids(request.get_parts())
        max_load = ceil(request.get_size() / len(self.HDDs_data))
        start = self.env.now
        yield self.env.timeout(max_load * self.HDDs_data[0].get_writing_bandwidth())
        self.logger.add_task_time("disk_write", self.env.now - start)
        self.__add_file_parts(request.get_parts())
        self.env.process(self.server_manager.answer_client(request))
        self.__mutex.release(mutex_req)

    def __add_file_parts(self, parts: List[FilePart]):
        for part in parts:
            if part.get_filename() in self.__parts:
                self.__parts[part.get_filename()].append(part)
            else:
                self.__parts[part.get_filename()] = [part]

    def add_request(self, request: WriteRequest):
        self.__requests.append(request)
        self.env.process(self.__process_write_request(request))

    def add_requests(self, requests: List[WriteRequest]):
        self.__requests += requests
        for request in requests:
            self.env.process(self.__process_write_request(request))

    def add_single_request(self, single_request):
        self.__requests.append(single_request)
        self.env.process(self.process_requests())

    def get_data_disks(self):
        return self.HDDs_data

    def get_metadata_disks(self):
        return self.HDDs_metadata

    def get_disk_from_cmloid(self, cmloid):
        """
        Hash function to assign a determined disk to a cmloid, based on its number id and its filename
        :param cmloid: the cmloid to interact with
        :type cmloid: CML_oid
        :return: the disk id valid in the current server
        :rtype: int
        """
        result = 0
        for letter in cmloid.get_file().get_name():
            result += self.lookup_table[ord(letter) % 32]
        result += self.lookup_table[cmloid.get_id_tuple()[0] % 32]
        return result % len(self.HDDs_data)

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

    def add_read_request(self, request: ReadRequest):
        print(self.__cmloids_per_disk[request.get_filename()])
        yield self.env.timeout(0)
