import simpy
from Server import Server
from Contract import Contract
from Utils import *
from FunctionDesigner import Function2D
from Logger import Logger
from HUB import HUB
from DHT import DHT
from Interfaces import IfForServer


class ServerManager(IfForServer):
    def __init__(self, env, server_params, client_params, misc_params, clients):
        self.env = env
        self.__client_completed = 0
        self.__clients = clients
        self.__network_buffer_size = misc_params[Contract.M_NETWORK_BUFFER_SIZE_KB]
        self.__server_logger = Logger(self.env)
        self.servers = []
        for i in range(server_params[Contract.S_SERVER_COUNT]):
            self.servers.append(
                    Server(self.env, i, self.__server_logger, server_params, misc_params, self))

        # This will keep the queue for the client requests
        # self.__HUB = HUB(env, int(misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8)
        self.__HUB = simpy.Resource(env)
        self.__overhead = int(misc_params[Contract.M_NETWORK_LATENCY_nS])
        self.__max_bandwidth = int(misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8
        self.__time_function = Function2D.get_bandwidth_model(self.__overhead, self.__max_bandwidth / 1e6)
        self.__dht = DHT(len(self.servers), server_params[Contract.S_HDD_DATA_COUNT])

    def get_server_by_id(self, ID):
        for server in self.servers:
            if ID == server.get_id():
                return server

    def request_server(self, request: ClientRequest, test_net: bool=False):
        """
        Sends the request to the servers
        Every request is queued.
        Every request of <networkbuffer size> is sent at max bandwidth
        A request smaller takes more time, based on Diagonal Limit configuration
        :param requests: list of client request holding the chunk to send
        :param test_net: boolean type, False by default. If True, forward an answer right to the client, skipping data writing to server. Used to test the network capabilities
        :return: yield the time required for the transaction to complete
        """
        mutex_request = self.__HUB.request()
        yield mutex_request
        size = request.get_size()
        if request.get_size() == self.__network_buffer_size:
            # <networkbuffer size> packets at full speed
            time_required = int(self.__network_buffer_size / self.__max_bandwidth * 1e9)
        else:
            # smaller packets with overhead introduced
            time_required = self.__time_function(request.get_size())
        yield self.env.timeout(time_required)
        self.__HUB.release(mutex_request)
        if test_net:
            self.answer_client(request)
        else:
            self.servers[request.get_target_id()].add_request(request)


    def single_request_server(self, req):
        # sendgroup = SendGroup()
        # paritygroup = ParityGroup()
        # paritygroup.add_request(req)
        # sendgroup.add_request(paritygroup)
        self.env.process(self.request_server(req))

    def get_server_count(self):
        return len(self.servers)

    def client_confirm_completed(self):
        self.__client_completed += 1
        if self.__client_completed == len(self.__clients):
            self.__clients[0].logger.print_info_to_file("client.log")
            self.__server_logger.print_info_to_file("server.log")

    def answer_client(self, request: ClientRequest):
        self.__clients[request.get_client()].receive_answer(request)
