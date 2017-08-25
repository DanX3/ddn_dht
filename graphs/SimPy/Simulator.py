import simpy
from Client import Client
from Server import Server
from ServerManager import ServerManager
import random
import Parser
from  FunctionDesigner import Function2D, Plotter
from Contract import Contract
# from Tests import *


class Simulator:
    def __init__(self, args):
        self.env = simpy.Environment()
        self.args = args
        self.parseFile()
        random.seed(args.seed)

        clients = []
        self.servers_manager = ServerManager(self.env, self.server_params,
                self.misc_params, clients)
        for i in range(self.client_params[Contract.C_CLIENT_COUNT]):
            clients.append(Client(i, self.env, self.servers_manager,
                self.client_params, self.misc_params))

        # Add for example 3KB to send from every client
        for client in clients:
            for i in range(10):
                client.add_request(20)
        log = open(self.misc_params[Contract.M_CLIENT_LOGFILE_NAME], 'w')

    def parseFile(self):
        configuration = open(self.args.config, "r")
        self.client_params = {}
        self.server_params = {}
        self.misc_params = {}
        for line in configuration:
            couple = line.strip().split('=')
            try:
                field = couple[0].strip()
                value = couple[1].strip()
                if field[0] == "C":     #Client options
                    self.client_params[field] = int(value)
                elif field[0] == "S":   #Server options
                    self.server_params[field] = int(value)
                elif field[0] == "M":   #Misc Options
                    self.misc_params[field] = value
                

                # self.params[couple[0].strip()] = int(couple[1].strip())
            except Exception:
                if line[0] == '#':
                    print("Skipped line with a comment")
                    continue

    def printParams(self, verbose=False):
        if args.verbose or verbose:
            for key, value in self.client_params.iteritems():
                print('{:>30} : {:d}'.format(key, value))

            print()
            print("- - - - - - - - - - - - - - - - - - - -")
            print()

            for key, value in self.server_params.iteritems():
                print('{:>30} : {:d}'.format(key, value))

    def run(self):
        self.env.run()


if __name__ == "__main__":
    parser = Parser.createparser()
    args = parser.parse_args()
    if args.function:
        if args.function == "gauss":
            Plotter.plot_gauss(args.mu, args.sigma)
        if args.function == "uniform":
            Plotter.plot_uniform(args.value)
        if args.function == "diag":
            Plotter.plot_diag_limit(args.overhead, args.angular_coeff)
    else:
        simulator = Simulator(args)
        if args.params:
            simulator.printParams(verbose=True)
        else:
            simulator.run()


