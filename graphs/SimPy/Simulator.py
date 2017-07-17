import simpy
from Client import Client
import argparse
import random
from os import getpid


class Simulator:
    def __init__(self, args):
        env = simpy.Environment()
        self.args = args
        self.parseFile()
        self.printParams()
        random.seed(getpid())
        server = simpy.Resource(env, 1)
        clients = [Client(i, env, server) for i in range(4)];
        env.run()

    def parseFile(self):
        configuration = open(self.args.config, "r")
        self.params = {}
        for line in configuration:
            couple = line.strip().split('=')
            try:
                self.params[couple[0].strip()] = int(couple[1].strip())
            except Exception:
                if line[0] == '#':
                    print "Skipped line with a comment"
                    continue

    def printParams(self):
        if args.verbose:
            for key, value in self.params.iteritems():
                print '{:>30} | {:d}'.format(key, value)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default='config')
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    simulator = Simulator(args)

