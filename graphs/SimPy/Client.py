import simpy
from Logger import Logger
from Server import Server
from Utils import *
from FunctionDesigner import Function2D
from Contract import Contract
from collections import deque
from ServerManager import  ServerManager
from simpy.util import start_delayed


class Client:
    def __init__(self, env: simpy.Environment, id: int, logger: Logger,
                 servers_manager: ServerManager, config, misc_params):
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

        self.request_queue = {}
        self.current_request = 0

        for i in range(servers_manager.get_server_count()):
            self.request_queue[i] = deque()

        seed(0)
        self.filename_gen = File.get_filename_generator(self.id)
        self.lookup_table = generate_lookup_table(32)
        self.send_treshold = int(1024 / ClientRequest.get_cmloid_size())
        self.data_sent = 0
        self.data_received = 0

    def refresh_tokens(self):
        tokens_missing = self.tokens.capacity - self.tokens.level
        if tokens_missing != 0:
            self.tokens.put(tokens_missing)
        yield self.env.timeout(self.__token_refresh_delay)
        if self.data_received < self.data_sent:
            self.env.process(self.refresh_tokens())

    def get_pending_parity_size(self):
        size = 0
        for request in self.pending_parity_queue:
            size += request
        return size

    def forming_parity_group(self):
        treshold = self.config[Contract.C_PENDING_PARITY_GROUP]
        if self.get_pending_parity_size() < treshold:
            yield self.env.timeout(0)
        else:
            send_size = 0
            while send_size <= treshold:
                send_size += self.request_queue.pop(0)
            self.pending_send_queue.append(send_size)
            yield self.env.process(self.logger.work(self.config[Contract.C_FORMING_PARITY_GROUP]))

    def pending_parity_group(self, request_size):
        # probably this time is negligible
        self.pending_parity_queue.append(request_size)
        yield self.env.process(self.logger.work(
            self.config[Contract.C_ENQUEUE_PARITY_GROUP]))

    def pending_send_grouping(self):
        yield self.env.process(self.logger.work(self.config[Contract.C_PENDING_SEND_GROUP]))

    def receive_answer(self, chunk_received: Chunk):
        self.data_received += chunk_received.get_size()
        if self.data_received >= self.data_sent:
            printmessage(self.id, "Finished all the transactions", self.env.now)
            self.servers_manager.client_confirm_completed()
        # if chunk_received.get_id() == chunk_received.get_tot_parts() - 1:
        # printmessage(self.ID, "Confirmed writing of {}".format(chunk_received), self.env.now)

    def run(self):
        yield self.env.timeout(0)
        # if self.request_queue:
            # self.current_request = self.request_queue.pop(0)
        # else:
            # print ("Client {} has finished all tasks".format(self.ID))
            # return

        # yield self.env.process(self.check_tokens())
        # yield self.env.process(self.send_request(self.chosen_server))

    def send_request(self, requests: List[ClientRequest]):
        start = self.env.now
        yield self.tokens.get(ceil(get_requests_size(requests) / NetworkBuffer.get_size()))
        self.logger.add_task_time("token_wait", self.env.now - start)

        start = self.env.now
        yield self.env.process(self.servers_manager.request_server(requests))
        self.logger.add_task_time("send_request", self.env.now - start)

    def flush_parities(self, target_id):
        pass

        # send_group = SendGroup()
        # reqs_to_send_count = min(self.config[Contract.C_PENDING_SEND_GROUP], len(self.pending_send_queue[target_id]))
        # for i in range(reqs_to_send_count):
        #     send_req = self.pending_send_queue[target_id].pop(0)
        #     send_group.add_request(send_req)
        # if reqs_to_send_count != 0:
        #     printmessage(self.ID, ">[{}]SendGroup".format(target_id), self.env.now)
        #     self.env.process(self.send_request(send_group))

    def flush_requests(self, target_id):
        # parity_group = ParityGroup()
        # reqs_to_send_count = min(self.config[Contract.C_PENDING_PARITY_GROUP], len(self.request_queue[target_id]))
        # for i in range(reqs_to_send_count):
        #     parity_group.add_request(self.request_queue[target_id].pop(0))
        # if reqs_to_send_count != 0:
        #     printmessage(self.ID, "+[{}]SendGroup".format(target_id), self.env.now)
        #     self.pending_send_queue[target_id].append(parity_group)
        self.send_request(target_id)

    def check_send_queue(self, target_id):
        pass
        # while len(self.pending_send_queue[target_id]) >= self.config[Contract.C_PENDING_SEND_GROUP]:
        #     self.flush_parities(target_id)

    def _get_request_queue_size(self, target_id):
        size = 0
        for req in self.request_queue[target_id]:
            size += req.get

    def check_request_queue(self, target_id, flush: bool=False):
        while self.enough_requests(self.request_queue[target_id]) or\
                (flush and self.request_queue[target_id]):
            packed_requests = []
            size = 0
            while size <= NetworkBuffer.get_size() and self.request_queue[target_id]:
                size += self.request_queue[target_id][0].get_chunk().get_size()
                packed_requests.append(self.request_queue[target_id].popleft())
            yield self.env.process(self.send_request(packed_requests))

    def add_write_request(self, req_size_kb):
        """
        Add a write request to the client.
        :param req_size_kb: int saying the size of the request to be done
        :return: the filename so generated. It chooses on his own the filename to avoid name collisions
        """
        filename = next(self.filename_gen)
        file = File(filename, req_size_kb)
        self.data_sent += req_size_kb
        for chunk in file.get_chunks():
            target_id = self.get_target_from_chunk(chunk)
            self.request_queue[target_id].append(ClientRequest(self, target_id, chunk, read=False))

        # trigger sending processes
        for target_id in range(self.servers_manager.get_server_count()):
            if len(self.request_queue[target_id]) > self.send_treshold:
                self.env.process(self.check_request_queue(target_id))
        return filename

    def print_status(self):
        print("Client {}".format(self.id))
        print("\tReqs queue:")
        for target_id in self.request_queue:
            print("\t\t[{}] : {}".format(target_id, len(self.request_queue[target_id])))

        print("\tSend queue:")
        for target_id in self.pending_send_queue:
            print("\t\t[{}] : {}".format(target_id, len(self.pending_send_queue[target_id])))
        print()

    def get_id(self):
        return self.id

    def flush(self):
        for target_id in range(self.servers_manager.get_server_count()):
            self.env.process(self.check_request_queue(target_id, flush=True))

    def get_target_from_file(self, file):
        """
        Given a file or its metadata, extract the target server ID where it is stored
        :param file: the file or metadata file we want to work on
        :return: the int id of the target server
        """

        table = self.lookup_table
        for i in range(32):
            idx1 = randint(0, 31)
            idx2 = randint(0, 31)
            table[idx1], table[idx2] = table[idx2], table[idx1]
        result = file.get_size() * table[file.get_size() % 32]
        str_size = str(file.get_size())
        for letter in str_size:
            result += table[ord(letter) % 32]
        return result % self.servers_manager.get_server_count()

    def get_target_from_chunk(self, chunk: Chunk):
        target = 0
        for letter in chunk.get_filename():
            target += ord(letter)
        return (target + chunk.get_id()) % self.servers_manager.get_server_count()

    def enough_requests(self, requests: List[ClientRequest]) -> bool:
        size = 0
        for req in requests:
            size += req.get_chunk().get_size()
            if size >= NetworkBuffer.get_size():
                return True
        return False
