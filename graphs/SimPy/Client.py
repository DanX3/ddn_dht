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
        self.logger = Logger(ID, env)
        self.tokens = 24

    def printInfo(self):
        self.logger.printInfo()

    def hash_address(self):
        # yield self.env.timeout(2)
        yield self.env.process(self.logger.work(2))
        printmessage(self.ID, "X", self.env.now)

    def decide_which_server(self):
        yield self.env.process(self.logger.work(2))
        # print "%d) decided server  -  %f" % (self.ID, self.env.now)
        printmessage(self.ID, "->", self.env.now)

    def send_request(self):
        yield self.env.process(self.hash_address())
        yield self.env.process(self.decide_which_server())
        yield self.env.process(Server.write_meta_to_DHT(self.env, self.ID, self.logger))

    def check_tokens(self):
        if self.tokens > 1:
            self.tokens -= 1
        else:
            yield self.timeout(300)

    def run(self, server):
        printmessage(self.ID, "?", self.env.now)
        request = server.request()
        yield request
        printmessage(self.ID, "+", self.env.now)
        yield self.env.process(self.check_tokens())
        yield self.env.process(self.send_request())
        server.release(request)
        if self.ID == 3:
            self.printInfo()

# env = simpy.rt.RealtimeEnvironment(initial_time=0, factor=1.0, strict=True)
env = simpy.Environment()
random.seed(os.getpid())
server = simpy.Resource(env, 1)
clients = [Client(i, env, server) for i in range(4)];
env.run()

