import simpy
from Logger import Logger
from Utils import *
from FunctionDesigner import *
from random import randint
import StorageDevice
from Contract import Contract
from StorageDevice import StorageDevice, DiskIdInconsistency, DiskIdNotation


class Server:
    def __init__(self, env, ID, config, misc_params, clients, server_manager):
        self.env = env
        self.id = ID
        self.logger = Logger(self.id, self.env)
        self.config = config
        self._mutex = simpy.Resource(env, capacity=1)
        self.clients = clients
        self.server_manager = server_manager
        self.requests = []
        self.HDDs_data = []
        self.HDDs_metadata = []

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

    def is_available(self):
        return self.is_available
        # return True if self.resource.count == 0 else False

    def set_availability(self, new_availability):
        self.is_available = new_availability

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

    def process_write_request(self, req):
        # print("Processing " + str(req))
        yield self.env.timeout(10)
        req.get_client().receive_answer(req)

    def process_single_request(self):
        req = self.requests.pop(0)
        # printmessage(self.id, "accepted req \n\n{}".format(req), self.env.now)
        if req.is_read():
            yield self.env.process(self.process_read_request(req))
        else:
            yield self.env.process(self.process_write_request(req))

    def process_requests(self):
        mutex_req = self._mutex.request()
        yield mutex_req
        if len(self.requests) == 0:
            yield self.env.timeout(0)
            self._mutex.release(mutex_req)
            return

        while len(self.requests) > 0:
            yield self.env.process(self.process_single_request())

        if len(self.requests) == 0:
            printmessage(self.id, "I'm free", self.env.now)
        self._mutex.release(mutex_req)
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
        self.env.process(self.process_requests())

    def add_single_request(self, single_request):
        self.requests.append(single_request)
        self.env.process(self.process_requests())

    def get_data_disks(self):
        return self.HDDs_data

    def get_metadata_disks(self):
        return self.HDDs_metadata
