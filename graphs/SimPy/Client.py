from Logger import Logger
from Server import Server
from Utils import *
from FunctionDesigner import Function2D
from Contract import Contract
from random import randint, seed


class Client:
    def __init__(self, ID, env, servers_manager, config, misc_params):
        self.env = env
        self.ID = ID
        self.servers_manager = servers_manager
        self.config = config
        self.misc_params = misc_params
        # self.env.process(self.run())
        self.logger = Logger(ID, env)
        self.tokens = 24
        self.chosen_server = -1

        # requests sent. The ints shows the size of KB of the request
        # request.queue = Dict[str, List[SendGroup]]
        self.request_queue = {}
        self.current_request = 0

        # self.pending_parity_queue = []
        self.pending_send_queue = {}
        for i in range(servers_manager.get_server_count()):
            self.pending_send_queue[i] = []
            self.request_queue[i] = []

        self.filename_gen = File.get_filename_generator(self.ID)

        self.lookup_table = []
        self._generate_primes()

    def _generate_primes(self):
        # for candidate in range(11, 1000):
        #     is_prime = True
        #     for divider in range(2, int(candidate/2)):
        #         if candidate % divider == 0:
        #             is_prime = False
        #             break
        #     if is_prime:
        #         self.lookup_table.append(candidate)
        #     if len(self.lookup_table) == 32:
        #         break

        self.lookup_table = [i for i in range(32)]
        # important that the seed is fixed. I want always the same pseudo-random sequence
        seed(17)
        for i in range(32):
            idx1 = randint(0, 31)
            idx2 = randint(0, 31)
            self.lookup_table[idx1], self.lookup_table[idx2] = self.lookup_table[idx2], self.lookup_table[idx1]

    def hash_address(self):
        yield self.env.process(self.logger.work(Function2D.gauss(30, 10)))
        printmessage(self.ID, "X", self.env.now)


    # def find_most_free_server(self):
        # most_free_server_id = -1
        # max_queue_length = 2e31
        # for server in self.servers:
            # if server.is_available():
                # most_free_server_id = server.get_id()
            # elif server.get_queue_length() < max_queue_length:
                # max_queue_length = server.get_queue_length()
                # most_free_server_id = server.get_id()
        # self.chosen_server = self.get_server_by_id(most_free_server_id)

    def decide_which_server(self):
        printmessage(self.ID, "->", self.env.now)
        # self.chosen_server = self.find_most_free_server()
        yield self.env.process(self.logger.work(Function2D.gauss(10, 2)))
    
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

    def check_tokens(self):
        if self.tokens > 0:
            self.tokens -= 1
        else:
            yield self.timeout(self.config[Contract.C_TOKEN_REFRESH])

    def receive_answer(self, req):
        printmessage(self.ID, "Received {}".format(req.get_filesize()), self.env.now)

    def run(self):
        yield self.env.timeout(0)
        # if self.request_queue:
            # self.current_request = self.request_queue.pop(0)
        # else:
            # print ("Client {} has finished all tasks".format(self.ID))
            # return

        # yield self.env.process(self.check_tokens())
        # yield self.env.process(self.send_request(self.chosen_server))

    def send_request(self, send_group):
        start = self.env.now
        print("Client {} requested Server {}".format(self.ID, send_group.get_target_ID()))
        # clientRequest = ClientRequest(self, target_server_ID, self.ID * 100)
        yield self.env.process(self.servers_manager.request_server(send_group))
        self.logger.add_idle_time(self.env.now - start)

    def flush_parities(self, target_id):
        send_group = SendGroup()
        reqs_to_send_count = min(self.config[Contract.C_PENDING_SEND_GROUP], len(self.pending_send_queue[target_id]))
        for i in range(reqs_to_send_count):
            send_req = self.pending_send_queue[target_id].pop(0)
            send_group.add_request(send_req)
        if reqs_to_send_count != 0:
            printmessage(self.ID, ">[{}]SendGroup".format(target_id), self.env.now)
            self.env.process(self.send_request(send_group))

    def flush_requests(self, target_id):
        parity_group = ParityGroup()
        reqs_to_send_count = min(self.config[Contract.C_PENDING_PARITY_GROUP], len(self.request_queue[target_id]))
        for i in range(reqs_to_send_count):
            parity_group.add_request(self.request_queue[target_id].pop(0))
        if reqs_to_send_count != 0:
            printmessage(self.ID, "+[{}]SendGroup".format(target_id), self.env.now)
            self.pending_send_queue[target_id].append(parity_group)

    def check_send_queue(self, target_id):
        while len(self.pending_send_queue[target_id]) >= self.config[Contract.C_PENDING_SEND_GROUP]:
            self.flush_parities(target_id)

    def check_request_queue(self, target_id):
        # requests_size = 0
        # for req in self.request_queue[target_id]:
        #     requests_size += req.get_size()

        # requests should be delivered also when a packed request is bigger than a treshold (~1MB)

        while len(self.request_queue[target_id]) >= self.config[Contract.C_PENDING_PARITY_GROUP]:
            self.flush_requests(target_id)
        self.check_send_queue(target_id)

    def add_request(self, req_size_kb, read):
        client_request = ClientRequest(self, File(next(self.filename_gen), req_size_kb), read=read)
        self.request_queue[client_request.get_target_ID()].append(client_request)
        self.check_request_queue(client_request.get_target_ID())

    def print_status(self):
        print("Client {}".format(self.ID))
        print("\tReqs queue:")
        for target_id in self.request_queue:
            print("\t\t[{}] : {}".format(target_id, len(self.request_queue[target_id])))

        print("\tSend queue:")
        for target_id in self.pending_send_queue:
            print("\t\t[{}] : {}".format(target_id, len(self.pending_send_queue[target_id])))
        print()

    def get_id(self):
        return self.ID

    def flush(self):
        for target_id in range(self.servers_manager.get_server_count()):
            self.flush_requests(target_id)

        for target_id in range(self.servers_manager.get_server_count()):
            self.flush_parities(target_id)

    def get_target_from_file(self, file):
        seed(0)
        table = self.lookup_table
        for i in range(32):
            idx1 = randint(0, 31)
            idx2 = randint(0, 31)
            table[idx1], table[idx2] = table[idx2], table[idx1]
        result = file.get_size() * table[file.get_size() % 32]
        str_size = str(file.get_size())
        for letter in str_size:
            result += table[ord(letter) % 32]
        return result % 2
