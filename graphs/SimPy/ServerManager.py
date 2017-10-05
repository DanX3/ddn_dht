import simpy
from Server import Server
from Contract import Contract
from Utils import *
from FunctionDesigner import Function2D
from Logger import Logger
from HUB import HUB


class ServerManager:
    def __init__(self, env, server_params, misc_params, clients):
        self.env = env
        self.server_params = server_params
        self.misc_params = misc_params
        self.__client_completed = 0
        self.__clients = clients
        self.__server_logger = Logger(self.env)
        self.servers = []
        for i in range(self.server_params[Contract.S_SERVER_COUNT]):
            self.servers.append(
                    Server(self.env, i, self.__server_logger, self.server_params, self.misc_params, clients, self))

        # This will keep the queue for the client requests
        self.requests = {}
        # self.__HUB = HUB(env, int(misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8)
        self.__HUB = simpy.Resource(env)
        self.__overhead = int(self.misc_params[Contract.M_NETWORK_LATENCY_nS])
        self.__max_bandwidth = int(self.misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8
        self.__time_function = Function2D.get_bandwidth_model(self.__overhead, self.__max_bandwidth / 1e6)

    def get_server_by_id(self, ID):
        for server in self.servers:
            if ID == server.get_id():
                return server

    def request_server(self, request: ClientRequest, test_net: bool=False):
        """
        Send the chunk request to the servers
        It uses HUB resources. Every request is queued.
        Every request of 1MB is sent at max bandwidth
        A request smaller takes more time, based on Diagonal Limit configuration
        :param request: client request holding the chunk to send
        :return: yield the time required for the transaction to complete
        """
        mutex_request = self.__HUB.request()
        yield mutex_request
        size = request.get_chunk().get_size()
        # 1 MB packets at full speed
        time_required = int((size / 1024) * (1024 / self.__max_bandwidth * 1e9))
        # smaller packages based on time function
        if size % 1024 != 0:
            time_required += int((size % 1024) * self.__time_function(size))
        yield self.env.timeout(time_required)
        self.__HUB.release(mutex_request)
        if test_net:
            request.get_client().receive_answer(request.get_chunk())
        else:
            self.servers[request.get_target_ID()].add_request(request)

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
