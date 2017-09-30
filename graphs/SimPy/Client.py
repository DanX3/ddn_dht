from Logger import Logger
from Server import Server
from Utils import *
from FunctionDesigner import Function2D
from Contract import Contract
from collections import deque


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
        # request.queue = Dict[str, deque[SendGroup]]
        self.request_queue = {}
        self.current_request = 0

        # self.pending_send_queue = {}
        for i in range(servers_manager.get_server_count()):
            # self.pending_send_queue[i] = []
            self.request_queue[i] = deque()

        self.filename_gen = File.get_filename_generator(self.ID)
        self.lookup_table = generate_lookup_table(32)
        self.log = open('client.log', 'w')

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

    def receive_answer(self, file_received):
        self.log.write(getmessage(self.ID, "written {}\n".format(file_received), self.env.now))
        # printmessage(self.ID, "Confirmed writing of {}".format(file_received), self.env.now)

    def run(self):
        yield self.env.timeout(0)
        # if self.request_queue:
            # self.current_request = self.request_queue.pop(0)
        # else:
            # print ("Client {} has finished all tasks".format(self.ID))
            # return

        # yield self.env.process(self.check_tokens())
        # yield self.env.process(self.send_request(self.chosen_server))

    def send_request(self, packed_reqs):
        # start = self.env.now
        # print("Client {} requested Server {}".format(self.ID, packed_reqs[0].get_target_ID()))
        # clientRequest = ClientRequest(self, target_server_ID, self.ID * 100)
        yield self.env.process(self.servers_manager.request_server(packed_reqs))
        # yield self.env.process(self.servers_manager.request_server(send_group))
        # self.logger.add_idle_time(self.env.now - start)

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

    def check_request_queue(self, target_id, force=False):
        # requests should be delivered also when a packed request is bigger than a treshold (1MB)
        send_treshold = int(1024 / ClientRequest.get_cmloid_size())
        while len(self.request_queue[target_id]) >= send_treshold:
            packed_reqs = [self.request_queue[target_id].popleft() for i in range(send_treshold)]
            # packed_reqs = self.request_queue[:send_treshold]
            # del(self.request_queue[0:send_treshold])
            yield self.env.process(self.send_request(packed_reqs))

        if force and len(self.request_queue[target_id]) > 0:
            packed_reqs = self.request_queue[target_id]
            yield self.env.process(self.send_request(packed_reqs))
            self.request_queue[target_id].clear()
        # self.check_send_queue(target_id)

    def add_write_request(self, req_size_kb):
        """
        Add a write request to the client.
        :param req_size_kb: int saying the size of the request to be done
        :return: the filename so generated. It chooses on his own the filename to avoid name collisions
        """
        filename = next(self.filename_gen)
        file = File(filename, req_size_kb)
        target_id = self.get_target_from_file(file)
        req = ClientRequest(self, target_id, file, read=False)
        # new_reqs = [req for req in get_requests_from_file(self, target_id, file, False)]
        # for req in get_requests_from_file(self, target_id, file, False):
        #     self.request_queue[target_id] += req
        self.request_queue[target_id] += get_requests_from_file(self, target_id, file, False)
        # self.request_queue[target_id] += new_reqs
        self.env.process(self.check_request_queue(req.get_target_ID()))
        return filename

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
            self.env.process(self.check_request_queue(target_id, force=True))

        # for target_id in range(self.servers_manager.get_server_count()):
        #     self.flush_parities(target_id)

    def get_target_from_file(self, file):
        """
        Given a file or its metadata, extract the target server ID where it is stored
        :param file: the file or metadata file we want to work on
        :return: the int id of the target server
        """
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
        return result % self.servers_manager.get_server_count()

