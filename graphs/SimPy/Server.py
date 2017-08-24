import simpy
from Logger import Logger
from Utils import *


class Server:
    def __init__(self, env, ID, config, misc_params):
        self.env = env
        self.ID = ID
        self.logger = Logger(self.ID, self.env)
        self.config = config
        self.availability = True

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

    def process_request(self, env, clientID, logger):
        yield env.timeout(2)
        printmessage(clientID, "-", env.now)

    def make_data_persistent(self, clientID):
        yield self.env.timeout(2)
        printmessage(clientID, "make_data_persistent", self.env.now)

    def propagate_to_DHT(self, clientID):
        yield self.env.process(self.logger.wait(10))
        printmessage(clientID, "propagate_to_DHT", self.env.now)

    def write_small_disk(self, datasize):
        yield self.env.process()

    def write_meta_to_DHT(self, clientID):
        yield self.env.process(self.logger.work(100))
        printmessage(clientID, "O<--", self.env.now)
        propagation = self.env.process(self.propagate_to_DHT(clientID))
        persistency = self.env.process(self.make_data_persistent(clientID))
        yield propagation & persistency
        printmessage(clientID, "-", self.env.now)


