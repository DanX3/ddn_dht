import simpy
import random
import os

SERVER_COUNT = 2

class Client(object):
    def __init__(self, ID, env, servers):
        self.env = env
        self.ID = ID
        self.servers = servers
        self.action = self.env.process(self.run())

    def run(self):
        yield self.env.timeout(random.randint(0,5))
        print "Client %d) write request  -  %d" % (self.ID, self.env.now)
        with self.servers.request() as request:
            yield request
            print "Client %d) write accepted -  %d" % (self.ID, self.env.now)
            yield self.env.timeout(random.randint(0,5))
            print "Client %d) write finished -  %d" % (self.ID, self.env.now)

env = simpy.Environment()
servers = simpy.Resource(env, SERVER_COUNT)
random.seed(os.getpid())
for i in range(4):
    Client(i, env, servers)
env.run()

