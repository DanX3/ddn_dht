import simpy
from Server import Server
from Contract import Contract
from Utils import *
from FunctionDesigner import Function2D
from Logger import Logger
from DHT import DHT
from typing import Dict, List
from Interfaces import IfForServer, IfForClient
from ParityGroupCreator import ParityGroupCreator
from math import fmod, floor


class ServerManager(IfForServer, IfForClient):
    def __init__(self, env, server_params, client_params, misc_params, clients, logpath):
        self.env = env
        self.__client_completed = 0
        self.__clients = clients
        self.__network_buffer_size = int(misc_params[Contract.M_NETWORK_BUFFER_SIZE_KB])
        self.__logpath = logpath
        self.server_logger = Logger(self.env, logpath)
        self.servers = []
        for i in range(server_params[Contract.S_SERVER_COUNT]):
            self.servers.append(
                    Server(self.env, i, self.server_logger, server_params, misc_params, self))
        # This will keep the queue for the client requests
        # self.__HUB = HUB(env, int(misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8)
        self.__HUB = simpy.Resource(env)
        self.__overhead = int(misc_params[Contract.M_NETWORK_LATENCY_nS])
        self.__max_bandwidth = int(misc_params[Contract.MAX_SWITCH_BANDWIDTH_Gbps]) * 1e6 / 8
        self.__max_same_time_transfers = int(int(misc_params[Contract.MAX_SWITCH_BANDWIDTH_Gbps]) / int(misc_params[Contract.MAX_SINGLE_LINK_BANDWIDTH]))
        self.__max_single_link_bw = int(misc_params[Contract.MAX_SINGLE_LINK_BANDWIDTH]) * 1e6 / 8
        self.__time_function = Function2D.get_bandwidth_model(self.__overhead, int(misc_params[Contract.MAX_SWITCH_BANDWIDTH_Gbps]) / 8)
        self.__dht = DHT(len(self.servers), server_params[Contract.S_HDD_DATA_COUNT])
        self.__full_speed_packet_time = int(self.__network_buffer_size / self.__max_bandwidth * 1e9)
        self.__manager_logger = Logger(self.env, logpath)
        self.__start = None
        self.__server_restoring = 0
        self.__show_counters = bool(misc_params[Contract.M_SHOW_COUNTERS])
        self.__read_pattern = None
        self.__log_runtime_data = bool(int(misc_params[Contract.M_LOG_RUNTIME_DATA]))
        if misc_params[Contract.M_READ_PATTERN] == "linear":
            self.__read_pattern = ReadPattern.LINEAR
        elif misc_params[Contract.M_READ_PATTERN] == "random":
            self.__read_pattern = ReadPattern.RANDOM
        else:
            raise Exception("No valid read pattern specified")
        self.__read_block_size = int(misc_params[Contract.M_READ_BLOCK_SIZE])
        self.__schedule_queue = []
        for operation in misc_params[Contract.M_OPERATIONS]:
            if operation == 'r':
                self.__schedule_queue.append(self.__simulate_client_read)
            if operation == 'f':
                self.__schedule_queue.append(self.__simulate_disk_failure)
        # self.__schedule_queue = [self.__simulate_client_read, self.__simulate_disk_failure]
        self.__server_same_time_write = {}
        self.__server_same_time_write_completed = {}
        self.__geometry = (client_params[Contract.C_GEOMETRY_BASE], client_params[Contract.C_GEOMETRY_PLUS])
        self.__sending_entities = set()
        self.__transfers = deque()
        self.__global_available_bandwidth = self.__max_single_link_bw
        self.__global_same_time_transfers = self.__max_same_time_transfers
        self.__global_previous_available_bw = self.__max_bandwidth
        self.__max_transfer_resource = simpy.Container(env, self.get_server_count() * 4, self.get_server_count() * 4)

    def print_entities(self):
        print("{:7d}".format(self.env.now), end=" ")
        for entity in self.__sending_entities:
            print(entity, end=', ')
        print()

    def add_sending_entity(self, id):
        self.__sending_entities.add(id)

    def remove_sending_entity(self, id):
        if __debug__:
            if id not in self.__sending_entities:
                raise Exception("Removing non existing sending entity")
        self.__sending_entities.remove(id)

    def add_requests_to_clients(self, requests: Dict[int, List[WriteRequest]]):
        self.__start = self.env.now
        for key, req_list in requests.items():
            for count, filesize in req_list:
                self.__clients[int(key)].add_write_request(filesize, files_count=count)

        for key, req_list in requests.items():
            self.__clients[key].flush()

    def __get_bandwidth_model_variable_bw(self, size, bw):
        return Function2D.get_bandwidth_model(self.__overhead, bw)(size)

    def __purge_transfers(self):
        processes_to_remove = []
        for transfer in self.__transfers:
            if not transfer.is_alive:
                processes_to_remove.append(transfer)

        # if len(processes_to_remove) != 0:
        #     print(self.env.now, "removing", len(processes_to_remove))

        for process in processes_to_remove:
            self.__transfers.remove(process)

    def __set_same_time_transfers(self, amount):
        self.__global_same_time_transfers = amount
        self.__global_previous_available_bw = self.__global_available_bandwidth
        self.__global_available_bandwidth = int(self.__max_bandwidth / amount)

    def __recursive_interruption(self, amount_of_time, size):
        start = self.env.now
        try:
            if amount_of_time != 0:
                yield self.env.timeout(amount_of_time)
        except simpy.Interrupt:
            time_passed = self.env.now - start
            new_time_required = amount_of_time - time_passed
            size_transferred = 0
            if time_passed != 0:
                size_transferred = int(time_passed / 1e9 * self.__global_previous_available_bw)
                new_time_required = self.__get_time_by_size(size - size_transferred)
            if new_time_required > 0:
                newprocess = self.env.process(self.__recursive_interruption(new_time_required, size - size_transferred))
                self.__transfers.append(newprocess)
                yield self.__transfers[len(self.__transfers)-1]

    def __throttle_transfers(self):
        transfers_to_interrupt = len(self.__transfers)
        for i in range(transfers_to_interrupt):
            self.__transfers.popleft().interrupt()

    def __get_time_by_size(self, size):
        full_speed_buffers = int(size / self.__network_buffer_size)
        time_required = full_speed_buffers * self.__network_buffer_size / self.__global_available_bandwidth
        data_left = size - full_speed_buffers * self.__network_buffer_size
        if data_left != 0:
            time_required += self.__get_bandwidth_model_variable_bw(data_left, self.__global_available_bandwidth) / 1e9
        # time_required = int(time_required * (self.__max_single_link_bw / self.__global_available_bandwidth))
        time_required = int(time_required * 1e9)
        return time_required


    def perform_network_transaction(self, size: int) -> int:
        """
        Simulates a network transaction
        Every request of <networkbuffer size> is sent at max bandwidth
        Every other request is sent as a smaller network buffer, so slower
        :param size: The size of the transaction to perform
        :return: yield the time required for the transaction to complete
        """
        mutex_request = self.__max_transfer_resource.get(1)
        yield mutex_request
        time_required = self.__get_time_by_size(size)
        self.__purge_transfers()
        if len(self.__transfers) > self.__max_same_time_transfers:
            self.__set_same_time_transfers(len(self.__transfers))
            self.__throttle_transfers()
        self.__transfers.append(self.env.process(self.__recursive_interruption(time_required, size)))
        yield self.__transfers[-1]

        yield self.__max_transfer_resource.put(1)

        return time_required

    def read_from_server(self, requests, target: int):
        self.env.process(self.servers[target].process_read_requests(requests))

    def read_from_server_blocking(self, request: ReadRequest, target: int):
        yield self.env.process(self.servers[target].process_read_request_blocking(request))

    def get_server_count(self) -> int:
        return len(self.servers)

    def write_completed(self):
        # Request to read every file sent
        self.__client_completed += 1
        if self.__client_completed == len(self.__clients):
            self.__manager_logger.add_task_time("write-operation", self.env.now - self.__start)
            printmessage(0, "Finished Writing", self.env.now)
            self.__parse_schedule()

        # log write at the same time
        if self.__log_runtime_data:
            times = open(self.__logpath + "server_concurrency", 'w')
            for i in range(len(self.__server_same_time_write)):
                if i in self.__server_same_time_write_completed:
                    times.write("{:13d} {:13d} {:6}\n".format(self.__server_same_time_write[i], self.__server_same_time_write_completed[i], i))

    def __simulate_client_read(self):
        self.__client_completed = 0
        self.__start = self.env.now
        for client in self.__clients:
            self.env.process(client.read_all_files(self.__read_pattern, self.__read_block_size))

    def read_completed(self):
        self.__client_completed += 1
        if self.__client_completed == len(self.__clients):
            printmessage(0, "Finished Reading", self.env.now)
            self.__manager_logger.add_task_time("read-operation", self.env.now - self.__start)
            self.__parse_schedule()

    def __simulate_disk_failure(self):
        self.__server_restoring = len(self.servers)
        self.__start = self.env.now
        for server in self.servers:
            self.env.process(server.process_disk_failure(sum(self.__geometry)))

    def send_recovery_request(self, crashed_server_id: int, ids: set, targets: int):
        for target in ParityGroupCreator.int_to_positions(targets):
            self.env.process(self.servers[target].gather_and_send_parity_groups(crashed_server_id, ids))

    def receive_recovery_request(self, target_server_id: int, from_id: int, data_amount: int):
        self.servers[target_server_id].receive_recovery_data(from_id, data_amount)

    def server_finished_restoring(self):
        self.__server_restoring -= 1
        if self.__server_restoring == 0:
            self.__manager_logger.add_task_time("disk-restore", self.env.now - self.__start)
            printmessage(0, "Finished Restoring", self.env.now)
            self.__parse_schedule()

    def __end_simulation(self):
        # Log times
        printmessage(0, "Finished Simulation", self.env.now)
        self.__clients[0].get_logger().print_times_to_file("client.log")
        self.server_logger.print_times_to_file("server.log")
        self.__manager_logger.print_times_to_file("manager.log")

        objects_list = [self.__clients[0].logger.get_objects(),
                        self.server_logger.get_objects(),
                        self.__manager_logger.get_objects()]
        merged_dict = Logger.merge_objects_to_dict(objects_list)
        Logger.print_objects_to_file(merged_dict, 'objects.log', logpath=self.__logpath)

    def write_to_server(self, request: WriteRequest):
        if self.__log_runtime_data:
            self.__server_same_time_write[request.get_parity_id()] = self.env.now
        self.env.process(self.servers[request.get_target_id()].process_write_request(request))

    def answer_client_write(self, request: WriteRequest):
        """
        Send answer back to the client with only metadata. Not a big request
        Let's say that these answers comes packed and don't take much bandwidth per answer
        Assume also that I can fit 1024 answers in a single answer packet
        :param request: a single client request
        :return:
        """
        if self.__log_runtime_data:
            self.__server_same_time_write_completed[request.get_parity_id()] = self.env.now
        self.__clients[request.get_client()].receive_write_answer(request)

    def answer_client_read(self, request: ReadRequest):
        self.__clients[request.get_client()].receive_read_answer(request)

    def propagate_metadata(self, packed_metadata, target_id: int):
        yield self.env.process(self.servers[target_id].receive_metadata_backup(packed_metadata))

    def __parse_schedule(self):
        self.__transfers.clear()
        if not self.__schedule_queue:
            self.__end_simulation()
        else:
            next_task = self.__schedule_queue.pop(0)
            next_task()

    def __simulate_read_pattern(self):
        for client in self.__clients:
            client.read_all_files()

    def update_recovery_progress(self, target_server_id: int, packets_gathered: int):
        self.servers[target_server_id].update_recovery_progress(packets_gathered)



