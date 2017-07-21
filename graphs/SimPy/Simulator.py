import simpy
from Client import Client
from Server import Server
import random
import Parser
from  FunctionDesigner import Function2D


class Simulator:
    def __init__(self, args):
        self.env = simpy.Environment()
        self.args = args
        self.parseFile()
        self.printParams()
        random.seed(args.seed)
        self.client_params = {}
        self.server_params = {}
        servers = []
        for i in range(2):
            servers.append(Server(self.env, i, self.server_params))
        clients = [Client(i, self.env, servers, self.client_params) for i in range(4)];

    def parseFile(self):
        configuration = open(self.args.config, "r")
        self.client_params = {}
        self.server_params = {}
        for line in configuration:
            couple = line.strip().split('=')
            try:
                field = couple[0].strip()
                value = couple[1].strip()
                if field[0] == "C":
                    self.client_params[field] = int(value)
                if field[0] == "S":
                    self.server_params[field] = int(value)

                # self.params[couple[0].strip()] = int(couple[1].strip())
            except Exception:
                if line[0] == '#':
                    print "Skipped line with a comment"
                    continue

    def printParams(self):
        if args.verbose:
            for key, value in self.client_params.iteritems():
                print '{:>30} | {:d}'.format(key, value)

            print
            print "--------------------"
            print

            for key, value in self.server_params.iteritems():
                print '{:>30} | {:d}'.format(key, value)

    def run(self):
        self.env.run()


if __name__ == "__main__":
    parser = Parser.createparser()
    args = parser.parse_args()
    if args.function:
        if args.function == "gauss":
            Function2D.plot_gauss(args.mu, args.sigma)
        if args.function == "uniform":
            Function2D.plot_uniform(args.value)
    else:
        simulator = Simulator(args)
        simulator.run()


