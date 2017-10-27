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
from ParityGroupCreator import ParityGroupCreator


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
        self.__server_restoring = 0
        self.__show_counters = bool(misc_params[Contract.M_SHOW_COUNTERS])

    def add_requests_to_clients(self, requests: Dict[int, List[WriteRequest]]):
        self.__start = self.env.now
        # Send a write request first
        for key, req_list in requests.items():
            for count, filesize in req_list:
                self.__clients[int(key)].add_write_request(filesize, file_count=count)

        for key, req_list in requests.items():
            self.__clients[key].flush()

        # for i in range(0, 1025, 16):
        #     print(i, self.__time_function(i))
        # print(1024, self.__full_speed_packet_time)

    def perform_network_transaction(self, size: int) -> int:
        """
        Simulates a network transaction
        Every request of <networkbuffer size> is sent at max bandwidth
        Every other request is sent as a smaller network buffer, so slower
        :param size: The size of the transaction to perform
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
            # for client in self.__clients:
                # self.env.process(client.read_all_files())
            self.__simulate_disk_failure(randint(0, len(self.servers)-1))

    def __simulate_disk_failure(self, server_id: int):
        self.__server_restoring = server_id
        self.__start = self.env.now
        self.env.process(self.servers[server_id].process_disk_failure())

    def send_recovery_request(self, ids: set, targets: int):
        print('targets', targets)
        for target in ParityGroupCreator.int_to_positions(targets):
            self.env.process(self.servers[target].gather_and_send_parity_groups(ids))

    def receive_recovery_request(self, from_id: int):
        self.servers[self.__server_restoring].receive_recovery_data(from_id)

    def server_finished_restoring(self):
        self.__manager_logger.add_task_time("disk-restore", self.env.now - self.__start)
        printmessage(0, "Finished Restoring", self.env.now)
        self.__end_simulation()

    def read_completed(self):
        self.__client_completed += 1
        if self.__client_completed == len(self.__clients):
            self.__manager_logger.add_task_time("read-operation", self.env.now - self.__start)
            self.__end_simulation()

    def __end_simulation(self):
        # Log times
        printmessage(0, "Finished Simulation", self.env.now)
        self.__clients[0].logger.print_times_to_file("client.log")
        self.server_logger.print_times_to_file("server.log")
        self.__manager_logger.print_times_to_file("manager.log")

        objects_list = [self.__clients[0].logger.get_objects(),
                        self.server_logger.get_objects(),
                        self.__manager_logger.get_objects()]
        merged_dict = Logger.merge_objects_to_dict(objects_list)
        print()
        Logger.print_objects_to_file(merged_dict, 'objects.log', print_to_screen=self.__show_counters)


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
