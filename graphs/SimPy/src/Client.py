import simpy
from Logger import Logger
from Server import Server
from Utils import *
from FunctionDesigner import Function2D
from Contract import Contract
from collections import deque
from ServerManager import  ServerManager
from simpy.util import start_delayed
from ParityGroupCreator import ParityGroupCreator, ParityId
from Interfaces import IfForClient

class Client:
    def __init__(self, env: simpy.Environment, id: int, logger: Logger,
                 servers_manager: IfForClient, config, misc_params,
                 pgc: ParityGroupCreator):
        self.env = env
        self.__id = id
        self.__manager = servers_manager
        self.config = config
        self.misc_params = misc_params
        self.logger = logger

        token_amount = config[Contract.C_TOKEN_COUNT]
        self.__tokens = simpy.Container(env, capacity=token_amount, init=token_amount)
        self.__server_count = servers_manager.get_server_count()
        self.__geometry = (config[Contract.C_GEOMETRY_BASE], config[Contract.C_GEOMETRY_PLUS])
        self.__parity_id_creator = ParityId()
        self.__network_buffer_size = int(misc_params[Contract.M_NETWORK_BUFFER_SIZE_KB])
        self.__send_treshold = self.__geometry[0] * self.__network_buffer_size
        self.__single_request_queue = deque()
        self.__single_request_queue_size = 0
        self.__show_requests = bool(config[Contract.C_SHOW_REQUESTS])
        self.__parity_groups_gen = pgc.get_target_generator()
        self.__main_queue = SliceablePartList()
        self.__bucket_queue = []  # List[SliceablePartList]
        self.__buffer_queue = []  # List[deque]
        for i in range(self.__server_count):
            self.__bucket_queue.append(SliceablePartList())
            self.__buffer_queue.append(deque())
        self.__bucket_size = int(misc_params[Contract.M_BUCKET_SIZE])
        self.__bucket_target_gen = round_robin_gen(self.__server_count)
        self.__file_map = {}  # Dict[str, int]
        self.__files_created = {}  # Dict[File]
        self.__data_sent = 0
        self.data_received = 0

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self.__filename_gen = File.get_filename_generator(self.__id)
        self.send_treshold = int(1024 / WriteRequest.get_cmloid_size())
        self.__ok_writing = False

    def get_id(self):
        return self.__id

    def add_write_request(self, req_size_kb, file_count=1) -> List[str]:
        # Populate the main queue
        filenames_generated = []
        for i in range(file_count):
            file = File(next(self.__filename_gen), req_size_kb)
            filenames_generated.append(file.get_name())
            self.__main_queue.add_file(file)
            self.__file_map[file.get_name()] = 0
            self.__files_created[file.get_name()] = file
        self.__populate_bucket_queue()
        return filenames_generated

    def __populate_bucket_queue(self):
        while self.__main_queue.get_size() >= self.__bucket_size:
            bucket = self.__main_queue.pop_buffer(self.__bucket_size, FilePart)
            target_id = next(self.__bucket_target_gen)
            for part in bucket:
                self.__file_map[part.get_filename()] |= 1 << target_id
            self.__bucket_queue[target_id].add_parts(bucket)
        self.__create_buffers_from_buckets()

    def __create_buffers_from_buckets(self):
        for i in range(self.__server_count):
            while self.__bucket_queue[i].get_size() >= self.__network_buffer_size:
                buffer = self.__bucket_queue[i].pop_buffer(self.__network_buffer_size, FilePart)
                self.__buffer_queue[i].append(buffer)
        self.__prepare_write_request()

    def is_parity_group_valid(self, targets: List[int]) -> bool:
        for target in targets[1:]:
            if len(self.__buffer_queue[target]) == 0:
                return False
        return True

    def __send_buffers(self, targets: List[int]):
        """
        Sends the buffers in the queues specified. These are only data targets.
        Parity is generated in this function
        So for geometry 3+1, len(targets) = 3
        :param targets: the targets to send
        """
        if len(targets) > sum(self.__geometry):
            raise Exception("Client: Too many packets")

        # Send data requests
        parity_id = self.__parity_id_creator.get_id()
        targets_int = ParityGroupCreator.positions_to_int(targets)
        max_size = 0
        for target in targets[1:]:
            request = WriteRequest(self.__id, target, targets_int, parity_id)
            request.set_parts(self.__buffer_queue[target].popleft())
            max_size = max(max_size, request.get_size())
            if self.__show_requests:
                print(request)
            self.env.process(self.__send_request(request))

        # Send parity request
        parity_request = WriteRequest(self.__id, targets[0], targets_int, parity_id)
        parity_request.set_parts([FilePart.create_parity_part(max_size)])
        if self.__show_requests:
            print(parity_request)
        self.env.process(self.__send_request(parity_request))

    def __prepare_write_request(self):
        # accessing to the queues depend on the targets extracted
        # it may happen that an extracted queue is empty but is still possible using the generator
        # instead of breaking immediatly there is a margin of error, chances before interrupting
        chances = int(self.__server_count / 4)
        while chances > 0:
            targets = ParityGroupCreator.int_to_positions(next(self.__parity_groups_gen))
            if not self.is_parity_group_valid(targets):
                chances -= 1
                continue

            self.__send_buffers(targets)

        self.__prepare_remainders()

    def __prepare_remainders(self):
        remaining_targets_list = []
        for i in range(len(self.__buffer_queue)):
            queue_len = len(self.__buffer_queue[i])
            if queue_len != 0:
                remaining_targets_list.append((i, queue_len))
        remaining_targets_list.sort(key = lambda k: k[1])
        remaining_targets = deque(remaining_targets_list)
        while len(remaining_targets) >= self.__geometry[0]:
            targets_int = 0
            for i in range(self.__geometry[0]):
                remaining_targets[i] = (remaining_targets[i][0], remaining_targets[i][1] - 1)
                targets_int |= 1 << remaining_targets[i][0]

            # Set parity target
            targets = ParityGroupCreator.int_to_positions(targets_int)
            parity_target = randint(0, self.__server_count-1)
            while parity_target in targets:
                parity_target = randint(0, self.__server_count-1)

            self.__send_buffers([parity_target] + targets)

            # Cleanup of empty packets
            while remaining_targets[0][1] <= 0:
                remaining_targets.popleft()

    def __send_request(self, request: WriteRequest):
        self.__data_sent += request.get_size()

        # simulate parity generation
        yield self.env.timeout(request.get_size())
        self.logger.add_task_time("parity-generation", request.get_size())

        # simulate token request
        token_request = self.__tokens.get(1)
        start = self.env.now
        yield token_request
        self.logger.add_task_time("token-wait", self.env.now - start)


        # simulate network transaction
        start = self.env.now
        yield self.env.process(self.__manager.perform_network_transaction(request.get_size()))
        self.logger.add_task_time("send-request", self.env.now - start)

        self.env.process(self.__manager.write_to_server(request))
        printmessage(self.__id, "Sent request to {}".format(request.get_target_id()), self.env.now)


    def flush(self):
        pass

    def receive_answer(self, request: WriteRequest):
        self.__data_sent -= request.get_size()
        if self.__data_sent == 0:
            self.__manager.write_completed()
