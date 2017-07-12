import simpy
import random
import os

SERVER_COUNT = 1
SERVER_NOTIFICATION_TIME_REQUIRED = 0.3


def printmessage(ID, message, time):
    print ("%d)"%ID).rjust(3), str(message).rjust(15), str(time).rjust(4)

class Server(object):
    @staticmethod
    def process_request(env, clientID):
        yield env.timeout(2)
        printmessage(clientID, "-", env.now)

class Client(object):
    def __init__(self, ID, env, server):
        self.env = env
        self.ID = ID
        self.server = server;
        self.env.process(self.run(self.server))

    def hash_address(self):
        yield self.env.timeout(2)
        printmessage(self.ID, "X", self.env.now)

    def decide_which_server(self):
        yield self.env.timeout(2)
        # print "%d) decided server  -  %f" % (self.ID, self.env.now)
        printmessage(self.ID, "->", self.env.now)

    def send_request(self):
        yield self.env.process(self.hash_address())
        yield self.env.process(self.decide_which_server())
        yield self.env.process(Server.process_request(self.env, self.ID))

    def run(self, server):
        printmessage(self.ID, "?", self.env.now)
        request = server.request()
        yield request
        yield env.process(self.send_request())
        server.release(request)

# env = simpy.rt.RealtimeEnvironment(initial_time=0, factor=1.0, strict=True)
random.seed(os.getpid())
env = simpy.Environment()
server = simpy.Resource(env, 1)
for i in range(4):
    Client(i, env, server)
env.run()

