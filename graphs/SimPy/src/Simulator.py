import simpy
from Client import Client
from ServerManager import ServerManager
import random
import Parser
from Contract import Contract
from Logger import Logger
from ParityGroupCreator import ParityGroupCreator


class Simulator:
    def __init__(self, args):
        self.env = simpy.Environment()
        self.args = args
        self.client_params = {}
        self.server_params = {}
        self.misc_params = {}
        self.parse_file()

        self.check_settings()
        self.print_session_summary()

        self.requests = {}
        self.__parse_requests()
        self.client_params[Contract.C_CLIENT_COUNT] = len(self.requests)

        random.seed(args.seed)
        self.__clients = []
        logpath = args.logpath
        if logpath[:-1] != '/':
            logpath += '/'
        self.servers_manager = ServerManager(self.env, self.server_params, self.client_params,
                                             self.misc_params, self.__clients, logpath)

        client_logger = Logger(self.env, logpath)
        parity_group_creator = ParityGroupCreator(self.client_params, self.server_params)
        for i in range(len(self.requests)):
            self.__clients.append(Client(self.env, i, client_logger, self.servers_manager,
                                  self.client_params, self.misc_params, parity_group_creator))

        self.servers_manager.add_requests_to_clients(self.requests)

    def print_session_summary(self):
        print("Server Count: {}".format(self.server_params[Contract.S_SERVER_COUNT]))
        print("Devices per server: {} ({} MBps Reading, {} MBps Writing)" .format(self.server_params[Contract.S_HDD_DATA_COUNT],
              self.server_params[Contract.S_HDD_DATA_READ_MBPS],
              self.server_params[Contract.S_HDD_DATA_WRITE_MBPS]))
        print("Geometry {}+{}".format(self.client_params[Contract.C_GEOMETRY_BASE], self.client_params[Contract.C_GEOMETRY_PLUS]))
        print("Request file: {}".format(self.args.request))
        print()

    def check_settings(self):
        # geometry must be less or equal than server number
        assert (self.client_params[Contract.C_GEOMETRY_BASE]
                + self.client_params[Contract.C_GEOMETRY_PLUS]) \
               <= self.server_params[Contract.S_SERVER_COUNT]

    def parse_file(self):
        configuration = open(self.args.config, "r")
        for line in configuration:
            couple = line.strip().split('=')
            try:
                field = couple[0].strip()
                value = couple[1].strip()
                if field[0] == "C":     # Client options
                    self.client_params[field] = int(value)
                elif field[0] == "S":   # Server options
                    self.server_params[field] = int(value)
                elif field[0] == "M":   # Misc Options
                    self.misc_params[field] = value
                
                # self.params[couple[0].strip()] = int(couple[1].strip())
            except Exception:
                if line[0] == '#':
                    continue

    def __from_human(self, human_number: str):
        """
        Replace human readable format with machine readable numbers.
        Used to improve request file readability
        :param human_number: the string representing the number
        :return: the integer represented
        """
        r = human_number.replace("P", "GG").replace("T", "GM").replace("G", "MM").replace("M", "000")
        return int(r)

    def __parse_requests(self):
        requests = open(self.args.request, 'r')

        # parses the file once to create an empty container of requests
        clients_count = 0
        for line in requests:
            try:
                if line == "" or line.startswith('#'):
                    continue
                if line.strip()[0] != '*':
                    clients_count += 1
            except Exception:
                pass

        for i in range(clients_count):
            self.requests[i] = []

        requests.seek(0)
        line_number = 0
        for line in requests:
            line = line.strip()
            try:
                if line == "" or line.startswith('#'):
                    continue
                words = line.split(" ")
                if words[0] == '*':
                    req = (self.__from_human(words[1]), self.__from_human(words[2]))
                    if req[0] != 0 and req[1] != 0:
                        for i in range(clients_count):
                            self.requests[i].append(req)
                else:
                    req = (self.__from_human(words[0]), self.__from_human(words[1]))
                    if req[0] != 0 and req[1] != 0:
                        self.requests[line_number].append(req)
                    line_number += 1
            except Exception:
                if line[0] == '#':
                    continue

    def print_params(self, verbose=False):
        if args.verbose or verbose:
            for key, value in self.client_params.items():
                print('{:>30} : {:d}'.format(key, value))

            print()
            print("- - - - - - - - - - - - - - - - - - - -")
            print()

            for key, value in self.server_params.items():
                print('{:>30} : {:d}'.format(key, value))

    def run(self):
        self.env.run()


if __name__ == "__main__":
    parser = Parser.createparser()
    args = parser.parse_args()

    simulator = Simulator(args)
    if args.params:
        simulator.print_params(verbose=True)
    else:
        simulator.run()




