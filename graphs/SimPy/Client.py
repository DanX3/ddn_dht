import simpy
import random
import os
from Server import Server, printmessage
from Logger import Logger

SERVER_COUNT = 1
SERVER_NOTIFICATION_TIME_REQUIRED = 0.3


class Client(object):
    def __init__(self, ID, env, server):
        self.env = env
        self.ID = ID
        self.server = server;
        self.env.process(self.run(self.server))
        self.logger = Logger(ID)

    def hash_address(self):
        yield self.env.timeout(2)
        printmessage(self.ID, "X", self.env.now)

    def decide_which_server(self):
        yield self.env.timeout(2)
        # print "%d) decided server  -  %f" % (self.ID, self.env.now)
        printmessage(self.ID, "->", self.env.now)

    def send_request(self):
        start = env.now
        yield self.env.process(self.hash_address())
        yield self.env.process(self.decide_which_server())
        self.logger.addWorkTime(env.now - start)
        start = env.now
        yield self.env.process(Server.write_meta_to_DHT(self.env, self.ID))
        self.logger.addIdleTime(env.now - start)

    def run(self, server):
        printmessage(self.ID, "?", self.env.now)
        request = server.request()
        yield request
        printmessage(self.ID, "+", self.env.now)
        yield self.env.process(self.send_request())
        server.release(request)
        self.logger.printInfo()


# env = simpy.rt.RealtimeEnvironment(initial_time=0, factor=1.0, strict=True)
env = simpy.Environment()
random.seed(os.getpid())
server = simpy.Resource(env, 1)
for i in range(4):
    Client(i, env, server)
env.run()

