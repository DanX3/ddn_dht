import simpy
from Logger import Logger
from Utils import *
from Contract import Contract
from collections import deque, OrderedDict
from ParityGroupCreator import ParityGroupCreator, ParityId
from Interfaces import IfForClient
from tqdm import tqdm

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
        self.__netbuff_size = int(misc_params[Contract.M_NETWORK_BUFFER_SIZE_KB])
        self.__send_treshold = self.__geometry[0] * self.__netbuff_size
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
        self.__remaining_targets = None
        self.__show_progress = bool(int(misc_params[Contract.M_SHOW_PROGRESS]))
        self.__progressbar = None

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self.__filename_gen = File.get_filename_generator(self.__id)
        self.send_treshold = int(1024 / WriteRequest.get_cmloid_size())
        self.__ok_writing = False

    def get_id(self):
        return self.__id

    def get_logger(self):
        return self.logger

    def add_write_request(self, req_size_kb, files_count=1) -> List[str]:
        # Populate the main queue
        if self.__show_progress:
            self.__progressbar = tqdm(total=req_size_kb * files_count, desc="Writing", mininterval=1.0)
        filenames_generated = []
        for i in range(files_count):
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
            while self.__bucket_queue[i].get_size() >= self.__netbuff_size:
                buffer = self.__bucket_queue[i].pop_buffer(self.__netbuff_size, FilePart)
                self.__buffer_queue[i].append(buffer)

        self.__prepare_write_request()

    def is_parity_group_valid(self, targets: List[int]) -> bool:
        for target in targets[1:]:
            if len(self.__buffer_queue[target]) == 0:
                return False
        return True

    def __send_buffers(self, targets: List[int]):
        if __debug__:
            assert len(targets) <= sum(self.__geometry), \
            "Client: Cannot send more packets than the geometry"


        # Send data requests
        parity_id = self.__parity_id_creator.get_id()
        targets_int = ParityGroupCreator.positions_to_int(targets)
        max_size = 0
        for target in targets[1:]:
            eagerness = False
            if self.__remaining_targets is not None:
                eagerness = False if target in self.__remaining_targets else True
            request = WriteRequest(self.__id, target, targets_int, parity_id, eagerness)
            request.set_parts(self.__buffer_queue[target].popleft())
            max_size = max(max_size, request.get_size())
            if self.__show_requests:
                print(request)
            self.env.process(self.__send_write_request(request))

        # Send parity request
        parity_request = WriteRequest(self.__id, targets[0], targets_int, parity_id, eagerness=False)
        parity_request.set_parts([FilePart.create_parity_part(max_size)])
        if self.__show_requests:
            print(parity_request)
        self.env.process(self.__send_write_request(parity_request))

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
            self.logger.add_task_time('allocation', 100000)

        self.__prepare_remainders()

    def __prepare_remainders(self, flush: bool=False):
        # Create self.__remaining_target
        if not flush:
            remaining_targets_list = []
            for i in range(len(self.__buffer_queue)):
                queue_len = len(self.__buffer_queue[i])
                if queue_len != 0:
                    remaining_targets_list.append((i, queue_len))
            remaining_targets_list.sort(key = lambda k: k[1])
            self.__remaining_targets = OrderedDict()
            for target, count in remaining_targets_list:
                self.__remaining_targets[target] = count

        while len(self.__remaining_targets) >= self.__geometry[0] \
                or (flush and len(self.__remaining_targets) != 0):
            self.logger.add_task_time('allocation', 2000)
            targets_int = 0
            countdown = self.__geometry[0]
            iterator = iter(self.__remaining_targets)
            while countdown > 0:
                try:
                    key = next(iterator)
                    self.__remaining_targets[key] -= 1
                    targets_int |= 1 << key
                    countdown -= 1
                except StopIteration:
                    break

            # Set parity target
            targets = ParityGroupCreator.int_to_positions(targets_int)
            parity_target = randint(0, self.__server_count-1)
            while parity_target in targets:
                parity_target = randint(0, self.__server_count-1)

            # Cleanup of empty packets
            while len(self.__remaining_targets) > 0:
                first_key = next(iter(self.__remaining_targets))
                if self.__remaining_targets[first_key] == 0:
                    del self.__remaining_targets[first_key]
                else:
                    break

            self.__send_buffers([parity_target] + targets)

    def __send_write_request(self, request: WriteRequest):
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
        self.logger.add_object_count('data-packets-sent', 1)

        self.__manager.write_to_server(request)

    def flush(self):
        if __debug__:
            assert len(self.__remaining_targets) < self.__geometry[0], \
            "Flush shouldn't be called when there are still full packets to send"

        self.__prepare_remainders(flush=True)

    def receive_write_answer(self, request: WriteRequest):
        if self.__show_progress:
            if request.get_parts()[0].get_filename() != "parity":
                self.__progressbar.update(request.get_size())
        self.__tokens.put(1)
        self.__data_sent -= request.get_size()
        if self.__data_sent == 0:
            if self.__show_progress:
                self.__progressbar.close()
            self.__manager.write_completed()

    def receive_read_answer(self, request: WriteRequest):
        self.__data_sent -= 1
        if self.__data_sent == 0:
            self.__manager.read_completed()

        start = self.env.now
        yield self.env.process(self.__manager.perform_network_transaction(request.get_size()))
        self.logger.add_task_time('receive-request', self.env.now - start)
        self.logger.add_object_count('data-packets-received',
                                     int(ceil(request.get_size() / self.__netbuff_size)))
        if self.__show_progress:
            self.__progressbar.update(request.get_size())

    def read_all_files(self, pattern: ReadPattern = ReadPattern.RANDOM, block_size: int = 1024):
        if __debug__:
            assert block_size <= 1024

        self.__data_sent = 0
        targets_queues = []
        for i in range(self.__server_count):
            targets_queues.append(deque())

        total_file_size = 0
        iterator = None
        if self.__show_progress:
            iterator = tqdm(self.__files_created.items(), desc="Preparing reading", mininterval=1.0)
        else:
            iterator = self.__files_created.items()
        for filename, file in iterator:
            read_request = ReadRequest(self.__id, file.get_name(), 0, file.get_size())
            total_file_size += file.get_size()
            for target in ParityGroupCreator.int_to_positions(self.__file_map[file.get_name()]):
                self.__data_sent += 1
                targets_queues[target].append(read_request)

        if pattern == ReadPattern.RANDOM:
            if self.__show_progress:
                self.__progressbar = tqdm(total=total_file_size, desc="Reading", mininterval=1.0)
            for target in range(self.__server_count):
                packed_requests = deque()
                while len(targets_queues[target]) != 0:
                    for i in range(min(len(targets_queues[target]), self.__netbuff_size)):
                        packed_requests.append(targets_queues[target].popleft())
                    self.__manager.read_from_server(packed_requests, target)
                    self.logger.add_object_count('request-read-sent', 1)

        if pattern == ReadPattern.LINEAR:
            iterator = None
            if self.__show_progress:
                iterator = tqdm(self.__files_created.items(), desc="Reading", mininterval=1.0)
            else:
                iterator = self.__files_created.items()
            for filename, file in iterator:
                read_generator = (ReadRequest(self.__id, filename, 0, file.get_size(), known_size=True))\
                    .get_generator(block_size)
                target_gen = ParityGroupCreator.get_generator_map_based(self.__file_map[filename])
                for read_request in read_generator:
                    yield self.env.process(self.__manager.read_from_server_blocking(read_request, next(target_gen)))
            print()
            self.__manager.read_completed()
            # for target in range(self.__server_count):
            #     packed_requests = deque()
            #     while len(targets_queues[target]) != 0:
            #         packed_requests.append(targets_queues[target].popleft())
            #         self.logger.add_object_count('request-read-sent', 1)

