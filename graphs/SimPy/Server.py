import simpy
from Logger import Logger
from Utils import *
from random import randint
import StorageDevice
from Contract import Contract
from StorageDevice import StorageDevice, DiskIdInconsistency, DiskIdNotation
from collections import deque


class Server:
    def __init__(self, env, ID, config, misc_params, clients, server_manager):
        self.env = env
        self.id = ID
        self.logger = Logger(self.id, self.env)
        self.config = config
        self.__mutex = simpy.Resource(env, capacity=1)
        self.clients = clients
        self.server_manager = server_manager
        self.requests = deque()
        self.HDDs_data = []
        self.HDDs_metadata = []
        self.receiving_files = {}  # Dict[str, Deque[CML_oid]]

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

    def process_read_request(self, req):
        req.get_client().receive_answer(req)
        raise MethodNotImplemented("Server")

    def __write_file(self, file):
        """
        Writes files to the disks, exploiting the RAID configuration
        For performance purposes, instead of creating and writing all the CML_oid,
        it pre-computes the amount that each disk will write and request a single big file write
        From outside the result is the same but is much more lightweight
        :param file: The file to be written
        :return: None
        """
        write_requests = []
        load_per_disk = self.get_load_per_disk(file)
        for i in range(len(self.HDDs_data)):
            req = self.env.process(self.HDDs_data[i].simulate_write(File('', load_per_disk[i])))
            write_requests.append(req)
        yield simpy.events.AllOf(self.env, write_requests)

    def __process_write_request(self, req):
        cmloid = req.get_cmloid()
        filename = cmloid.get_file().get_name()

        # adds the file to the queue collection
        if filename not in self.receiving_files:
            self.receiving_files[filename] = [cmloid.get_id()]
        else:
            self.receiving_files[filename].append(cmloid.get_id())

        # send confirmation if file has been completely collected
        if len(self.receiving_files[filename]) == cmloid.get_total_parts():
            yield self.env.process(self.__write_file(cmloid.get_file()))
            del(self.receiving_files[filename])
            req.get_client().receive_answer(cmloid.get_file())

    def __process_single_request(self):
        req = self.requests.popleft()
        # printmessage(self.id, "accepted req \n\n{}".format(req), self.env.now)
        if req.is_read():
            yield self.env.process(self.process_read_request(req))
        else:
            yield self.env.process(self.__process_write_request(req))

    def process_requests(self):
        mutex_req = self.__mutex.request()
        yield mutex_req
        if len(self.requests) == 0:
            yield self.env.timeout(0)
            self.__mutex.release(mutex_req)
            return

        while len(self.requests) > 0:
            yield self.env.process(self.__process_single_request())

        # if len(self.requests) == 0:
        #     printmessage(self.id, "I'm free", self.env.now)
        self.__mutex.release(mutex_req)
        # Redirect to the correct server
        # self.server_manager.add_request(clientRequest)

    def is_request_local(self, clientRequest):
        return True

    def get_new_target(self, clientRequest):
        return self

    def add_request(self, send_group):
        # requests unpacking
        # for parityGroup in send_group.get_requests():
        #     for single_request in parityGroup.get_requests():
        #         self.requests.append(single_request)

        if len(send_group) > 8:
            raise Exception("Server {}: Arrived more than 1MB in a single request".format(self.id))

        for req in send_group:
            self.requests.append(req)
        if len(self.requests) > 0:
            self.env.process(self.process_requests())

    def add_single_request(self, single_request):
        self.requests.append(single_request)
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

    def get_load_per_disk(self, file):
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
