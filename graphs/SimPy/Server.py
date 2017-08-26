import simpy
from Logger import Logger
from Utils import *
from FunctionDesigner import *
from random import randint


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

    def process_single_request(self):
        req = self.requests.pop(0)
        if (self.is_request_valid(req)):
            printmessage(self.ID, "accepted req {}".format(req.get_client().get_id()), self.env.now)
            yield self.env.process(self.logger.work(Function2D.get_diag_limit(50000, 1000)(req.get_filesize())))
            req.get_client().receive_answer(req)
            # printmessage(req.get_client().get_id(), "-", env.now)
        else:
            new_target_ID = self.ID
            while new_target_ID == self.ID:
                new_target_ID = randint(0, len(self.server_manager.servers) - 1)
            req.set_new_target_ID(new_target_ID)
            printmessage(self.ID, "({}) {} --> {}".format(req.get_client().get_id(), self.ID, new_target_ID), self.env.now)
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

    def is_request_valid(self, clientRequest):
        if randint(0, 9) < 7:
            return True
        else:
            return False

    def get_new_target(self, clientRequest):
        return self

    def add_request(self, sendGroup):
        for parityGroup in sendGroup.get_requests():
            for single_request in parityGroup.get_requests():
                self.requests.append(single_request)
        self.env.process(self.process_requests())

    def add_single_request(self, single_request):
        self.requests.append(single_request)
        self.env.process(self.process_requests())
