import simpy
from Server import Server
from Contract import Contract
from Utils import *
from FunctionDesigner import Function2D
from Logger import Logger
from HUB import HUB
from DHT import DHT
from typing import Dict, List
from Interfaces import IfForServer, IfForClient


class ServerManager(IfForServer, IfForClient):
    def __init__(self, env, server_params, client_params, misc_params, clients):
        self.env = env
        self.__client_completed = 0
        self.__clients = clients
        self.__network_buffer_size = int(misc_params[Contract.M_NETWORK_BUFFER_SIZE_KB])
        self.server_logger = Logger(self.env)
        self.servers = []
        for i in range(server_params[Contract.S_SERVER_COUNT]):
            self.servers.append(
                    Server(self.env, i, self.server_logger, server_params, misc_params, self))
        # This will keep the queue for the client requests
        # self.__HUB = HUB(env, int(misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8)
        self.__HUB = simpy.Resource(env)
        self.__overhead = int(misc_params[Contract.M_NETWORK_LATENCY_nS])
        self.__max_bandwidth = int(misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8
        self.__time_function = Function2D.get_bandwidth_model(self.__overhead, self.__max_bandwidth / 1e6)
        self.__dht = DHT(len(self.servers), server_params[Contract.S_HDD_DATA_COUNT])
        self.__full_speed_packet_time = int(self.__network_buffer_size / self.__max_bandwidth * 1e9)
        self.__manager_logger = Logger(self.env)
        self.__start = None

    def add_requests_to_clients(self, requests: Dict[int, List[WriteRequest]]):
        self.__start = self.env.now
        # Send a write request first
        for key, req_list in requests.items():
            for count, filesize in req_list:
                self.__clients[int(key)].add_write_request(filesize, file_count=count)

        for key, req_list in requests.items():
            self.__clients[key].flush()

    def perform_network_transaction(self, size: int) -> int:
        """
        Simulates a network transaction
        Every request is queued.
        Every request of <networkbuffer size> is sent at max bandwidth
        A request smaller takes more time, based on Diagonal Limit configuration
        :param requests: list of client request holding the chunk to send
        :param test_net: boolean type, False by default. If True, forward an answer right to the client, skipping data writing to server. Used to test the network capabilities
        :return: yield the time required for the transaction to complete
        """
        mutex_request = self.__HUB.request()
        yield mutex_request

        time_required = int(size / self.__network_buffer_size) * self.__full_speed_packet_time
        if size % self.__network_buffer_size != 0:
                time_required += self.__time_function(size % self.__network_buffer_size)
        yield self.env.timeout(time_required)

        self.__HUB.release(mutex_request)
        return time_required

    def read_from_server(self, request: ReadRequest, target: int) -> (int, int):
        cmloid_count = yield self.env.process(self.servers[target].process_read_request(request))
        return cmloid_count

    def get_server_count(self):
        return len(self.servers)

    def write_completed(self):
        # Request to read every file sent
        self.__client_completed += 1
        if self.__client_completed == len(self.__clients):
            self.__manager_logger.add_task_time("write-operation", self.env.now - self.__start)
            self.__start = self.env.now
            self.__client_completed = 0
            for client in self.__clients:
                self.env.process(client.read_all_files())

    def read_completed(self):
        self.__client_completed += 1
        if self.__client_completed == len(self.__clients):
            self.__manager_logger.add_task_time("read-operation", self.env.now - self.__start)
            self.__clients[0].logger.print_info_to_file("client.log")
            self.server_logger.print_info_to_file("server.log")
            self.__manager_logger.print_info_to_file("manager.log")
            printmessage(0, "Finished Simulation", self.env.now)

    def write_to_server(self, request: WriteRequest) -> int:
        write_time = yield self.env.process(self.servers[request.get_target_id()].process_write_request(request))
        return write_time

    def answer_client(self, request: WriteRequest):
        """
        Send answer back to the client with only metadata. Not a big request
        Let's say that these answers comes packed and don't take much bandwidth per answer
        Assume also that I can fit 1024 answers in a single answer packet
        :param request: a single client request
        :return:
        """
        time_to_wait = int(1 / self.__max_bandwidth * 1e9)
        yield self.env.timeout(time_to_wait)
        self.__clients[request.get_client()].receive_answer(request)
