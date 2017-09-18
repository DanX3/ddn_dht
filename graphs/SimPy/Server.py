import simpy
from Logger import Logger
from Utils import *
from FunctionDesigner import *
from random import randint
from Contract import Contract
from StorageDevice import StorageDevice


class Server:
    def __init__(self, env, ID, config, misc_params, clients, server_manager):
        self.env = env
        self.ID = ID
        self.logger = Logger(self.ID, self.env)
        self.config = config
        self.availability = True
        self.clients = clients
        self.server_manager = server_manager
        self.requests = []

        self.hdd_data = StorageDevice(config[Contract.S_HDD_DATA_CAPACITY_GB] * 2e9,
                                      config[Contract.S_HDD_DATA_BW_MB_PER_SEC] * 2e3,
                                      config[Contract.S_HDD_DATA_LATENCY_MS])
        self.hdd_metadata = StorageDevice(config[Contract.S_HDD_METADATA_CAPACITY_GB] * 2e9,
                                          config[Contract.S_HDD_METADATA_BW_MB_PER_SEC] * 2e3,
                                          config[Contract.S_HDD_METADATA_LATENCY_MS])

    def is_available(self):
        return self.availability
        # return True if self.resource.count == 0 else False

    def set_availability(self, new_availability):
        self.availability = new_availability

    def get_queue_length(self):
        if self.is_available:
            return 0
        else:
            return len(self.resource.queue)
    
    def get_id(self):
        return self.ID

    def process_read_request(self, req):
        transfer_time = req.get_filesize() / self.hdd_data.get_bandwidth()
        yield self.env.timeout(self.hdd_data.get_latency() + transfer_time)
        req.get_client().receive_answer(req)

    def process_write_request(self, req):
        transfer_time = req.get_filesize() / self.hdd_data.get_bandwidth()
        yield self.env.timeout(self.hdd_data.get_latency() + transfer_time)
        req.get_client().receive_answer(req)

    def process_single_request(self):
        req = self.requests.pop(0)
        if self.is_request_local(req):
            printmessage(self.ID, "accepted req {}".format(req.get_client().get_id()), self.env.now)
            if req.is_read():
                yield self.env.process(self.process_read_request(req))
            else:
                yield self.env.process(self.process_write_request(req))
        else:
            new_target_id = self.ID
            while new_target_id == self.ID:
                new_target_id = randint(0, len(self.server_manager.servers) - 1)
            req.set_new_target_ID(new_target_id)
            printmessage(self.ID, "({}) {} --> {}".format(req.get_client().get_id(), self.ID, new_target_id), self.env.now)
            self.env.process(self.server_manager.request_server_single_req(req))
            pass

    def process_requests(self):
        if len(self.requests) != 0 and self.availability == True:
            self.availability = False
            yield self.env.process(self.process_single_request())

            if len(self.requests) != 0:
                self.availability = True
                self.env.process(self.process_single_request())
            else:
                self.availability = True
                printmessage(self.ID, "I'm free", self.env.now)
                # Redirect to the correct server
                # self.server_manager.add_request(clientRequest)

    def is_request_local(self, clientRequest):
        if randint(0, 9) < 10:
            return True
        else:
            return False

    def get_new_target(self, clientRequest):
        return self

    def add_request(self, send_group):
        # requests unpacking
        for parityGroup in send_group.get_requests():
            for single_request in parityGroup.get_requests():
                self.requests.append(single_request)
        self.env.process(self.process_requests())

    def add_single_request(self, single_request):
        self.requests.append(single_request)
        self.env.process(self.process_requests())
