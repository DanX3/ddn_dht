import simpy
import random
import os

SERVER_COUNT = 1
SERVER_NOTIFICATION_TIME_REQUIRED = 0.3

random.seed(os.getpid())
env = simpy.Environment()
server = simpy.Resource(env, 1)

def printmessage(ID, message, time):
    print ("%d)"%ID).rjust(3), str(message).rjust(15), str(time).rjust(4)

class Server(object):
    @staticmethod
    def process_request(env, clientID):
        yield env.timeout(1)
        printmessage(clientID, "-", env.now)

class Client(object):
    def __init__(self, ID, env):
        self.env = env
        self.ID = ID
        self.env.process(self.run())

    def hash_address(self):
        yield self.env.timeout(1)
        printmessage(self.ID, "X", self.env.now)

    def decide_which_server(self):
        yield self.env.timeout(1)
        # print "%d) decided server  -  %f" % (self.ID, self.env.now)
        printmessage(self.ID, "->", self.env.now)

    def send_request(self):
        self.env.process(self.hash_address())
        self.env.process(self.decide_which_server())
        # self.env.process(Server.process_request(self.env, self.ID))

    def run(self):
        # yield self.env.timeout(random.randint(0,1))
        # if (random.random() < 0.9999):
            #The server answers
        printmessage(self.ID, "?", self.env.now)
        with server.request() as request:
            yield request
            yield self.env.timeout(2)
            printmessage(self.ID, "+(%d)" % server.count, self.env.now)
            self.env.process(self.hash_address())
            self.env.process(self.decide_which_server())
            self.env.process(Server.process_request(self.env, self.ID))
        # else:
            # #One server doesn't answer back
            # print "%d) SERVER DEAD - %f" % (self.ID, self.env.now)
            # yield self.env.timeout(SERVER_NOTIFICATION_TIME_REQUIRED)

# env = simpy.rt.RealtimeEnvironment(initial_time=0, factor=1.0, strict=True)
for i in range(4):
    Client(i, env)
env.run()

