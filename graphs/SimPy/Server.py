import simpy
from Logger import Logger
from Utils import *


class Server:

    def __init__(self, env, ID, config):
        self.env = env
        self.ID = ID
        self.resource = simpy.Resource(self.env, 1)
        self.logger = Logger(self.ID, self.env)
        self.config = config

    def is_available(self):
        return True if self.resource.count == 0 else False
    
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

    def make_data_persistent(self, env, clientID, logger):
        yield env.timeout(2)
        printmessage(clientID, "make_data_persistent", env.now)

    def propagate_to_DHT(self, env, clientID, logger):
        yield env.process(logger.wait(10))
        printmessage(clientID, "propagate_to_DHT", env.now)

    def write_meta_to_DHT(self, env, clientID, logger):
        yield env.process(logger.wait(100))
        printmessage(clientID, "O<--", env.now)
        propagation = env.process(self.propagate_to_DHT(env, clientID, logger))
        persistency = env.process(self.make_data_persistent(env, clientID, logger))
        yield propagation | persistency
        yield propagation & persistency
        printmessage(clientID, "-", env.now)


