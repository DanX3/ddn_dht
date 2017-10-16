import simpy
from Logger import Logger
from Server import Server
from Utils import *
from FunctionDesigner import Function2D
from Contract import Contract
from collections import deque
from ServerManager import  ServerManager
from simpy.util import start_delayed
from ParityGroupCreator import ParityGroupCreator


class Client:
    def __init__(self, env: simpy.Environment, id: int, logger: Logger,
                 servers_manager: ServerManager, config, misc_params,
                 pgc: ParityGroupCreator):
        self.env = env
        self.id = id
        self.servers_manager = servers_manager
        self.config = config
        self.misc_params = misc_params
        self.logger = logger

        token_amount = config[Contract.C_TOKEN_COUNT]
        self.tokens = simpy.Container(env, capacity=token_amount, init=token_amount)
        self.env.process(self.refresh_tokens())
        self.__token_refresh_delay = config[Contract.C_TOKEN_REFRESH_INTERVAL_ms] * int(1e6)
        self.__geometry = (config[Contract.C_GEOMETRY_BASE], config[Contract.C_GEOMETRY_PLUS])
        self.request_queue = {}  # Dict[int, deque]
        self.__single_request_queue = deque()
        self.__single_request_queue_size = 0
        # TODO: find a balanced value to the length of the parity targets list
        self.__parity_targets = pgc.get_targets_list(int(servers_manager.get_server_count() / 2))
        self.__parity_index = 0

        for i in range(servers_manager.get_server_count()):
            self.request_queue[i] = deque()

        seed(0)
        self.filename_gen = File.get_filename_generator(self.id)
        self.send_treshold = int(1024 / ClientRequest.get_cmloid_size())
        self.data_sent = 0
        self.data_received = 0

    def refresh_tokens(self):
        tokens_missing = self.tokens.capacity - self.tokens.level
        if tokens_missing != 0:
            self.tokens.put(tokens_missing)

        # trigger sending processes
        for target_id in range(self.servers_manager.get_server_count()):
            if len(self.request_queue[target_id]) > self.send_treshold:
                self.env.process(self.check_request_queue(target_id))

        yield self.env.timeout(self.__token_refresh_delay)
        if self.data_received < self.data_sent:
            self.env.process(self.refresh_tokens())

    def receive_answer(self, chunk_received: Chunk):
        self.data_received += chunk_received.get_size()
        if self.data_received >= self.data_sent:
            printmessage(self.id, "Finished all the transactions", self.env.now)
            self.servers_manager.client_confirm_completed()

    def send_request(self, requests: List[ClientRequest]):
        start = self.env.now
        yield self.tokens.get(ceil(get_requests_size(requests) / NetworkBuffer.get_size()))
        self.logger.add_task_time("token_wait", self.env.now - start)

        start = self.env.now
        yield self.env.process(self.servers_manager.request_server(requests))
        self.logger.add_task_time("send_request", self.env.now - start)

    def check_request_queue(self, target_id, flush: bool=False):
        while self.enough_requests(self.request_queue[target_id]) or\
                (flush and self.request_queue[target_id]):
            packed_requests = []
            size = 0
            while size <= NetworkBuffer.get_size() and self.request_queue[target_id]:
                size += self.request_queue[target_id][0].get_chunk().get_size()
                packed_requests.append(self.request_queue[target_id].popleft())
            yield self.env.process(self.send_request(packed_requests))

    def add_write_request(self, req_size_kb, file_count=1) -> List[str]:
        """
        Add a write request to the client.
        :param req_size_kb: int saying the size of the request to be done
        :return: the filename so generated. It chooses on his own the filename to avoid name collisions
        """
        filenames = []
        for i in range(file_count):
            filename = next(self.filename_gen)
            file = File(filename, int(req_size_kb * sum(self.__geometry) / self.__geometry[0]))
            filenames.append(filename)
            print("Added request for file of size " + str(file.get_size()))
            # self.data_sent += file.get_size()
            self.__single_request_queue.append(FilePart(file, 0, file.get_size()))
        self.__single_request_queue_size += int(req_size_kb * sum(self.__geometry) / self.__geometry[0]) * file_count
        self.__scatter_files_in_queues()
        return filenames

    def __scatter_files_in_queues(self):
        """
        Divides the files in the queue in network buffers and append the in the correct queue
        """
        send_treshold = sum(self.__geometry) * NetworkBuffer.get_size()
        print(self.__single_request_queue_size)
        while self.__single_request_queue_size >= send_treshold:
            self.__single_request_queue_size -= send_treshold
            # TODO write a class in which remember the targets and the current index
            targets = ParityGroupCreator.int_to_positions(self.__parity_targets[self.__parity_index])
            self.__parity_index = (self.__parity_index + 1) % len(self.__parity_targets)
            for target_id in targets:
                request = ClientRequest(self, target_id, False)
                request.set_parts(self.pop_netbuffer_from_queue())
                self.request_queue[target_id].append(request)
                print(request)
            del targets

    def pop_netbuffer_from_queue(self) -> List[FilePart]:
        result = []
        free_space = self.config[Contract.C_NETWORK_BUFFER_SIZE_KB]
        while free_space > 0 and len(self.__single_request_queue) > 0:
            if self.__single_request_queue[0].get_size() <= free_space:
                free_space -= self.__single_request_queue[0].get_size()
                result.append(self.__single_request_queue.popleft())
            else:
                result.append(self.__single_request_queue[0].pop_part(free_space))
                free_space = 0
        return result

    def get_id(self):
        return self.id

    def flush(self):
        pass
        # for target_id in range(self.servers_manager.get_server_count()):
        #     self.env.process(self.check_request_queue(target_id, flush=True))

    def get_target_from_chunk(self, chunk: Chunk):
        return simple_hash(chunk.get_filename(), self.servers_manager.get_server_count(), chunk.get_id())

    def enough_requests(self, requests: List[ClientRequest]) -> bool:
        size = 0
        for req in requests:
            size += req.get_chunk().get_size()
            if size >= NetworkBuffer.get_size():
                return True
        return False
