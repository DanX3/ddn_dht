from Logger import Logger
from Server import Server
from Utils import *
from FunctionDesigner import Function2D
from Contract import Contract
from random import randint

class Client:
    def __init__(self, ID, env, servers_manager, config, misc_params):
        self.env = env
        self.ID = ID
        self.servers_manager = servers_manager
        self.config = config
        self.misc_params = misc_params
        self.env.process(self.run())
        self.logger = Logger(ID, env)
        self.tokens = 24
        self.chosen_server = -1

        # requests sent. The ints shows the size of KB of the request
        self.request_queue = []
        self.current_request = 0

        # self.pending_parity_queue = []
        self.pending_send_queue = []

    def hash_address(self):
        # yield self.env.timeout(2)
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

    def send_request(self, sendGroup):
        start = self.env.now
        target_server_id = randint(0, len(self.servers_manager.servers)-1)
        print("Client {} requested Server {}".format(self.ID, target_server_id))
        # clientRequest = ClientRequest(self, target_server_ID, self.ID * 100)
        yield self.env.process(self.servers_manager.request_server(sendGroup))
        self.logger.add_idle_time(self.env.now - start)

    def check_send_queue(self):
        while len(self.pending_send_queue) >= self.config[Contract.C_PENDING_SEND_GROUP]:
            sendGroup = SendGroup()
            printmessage(self.ID, ">SendGroup", self.env.now)
            for i in range(self.config[Contract.C_PENDING_SEND_GROUP]):
                send_req = self.pending_send_queue.pop(0)
                print(send_req)
                sendGroup.add_request(send_req)
            self.env.process(self.send_request(sendGroup))

    def check_request_queue(self):
        while len(self.request_queue) >= self.config[Contract.C_PENDING_PARITY_GROUP]:
            parity_group = ParityGroup()
            printmessage(self.ID, "+SendGroup", self.env.now)
            for i in range(self.config[Contract.C_PENDING_PARITY_GROUP]):
                parity_group.add_request(self.request_queue.pop(0))
            self.pending_send_queue.append(parity_group)
            # yield self.env.timeout(1)
        self.check_send_queue()

    def add_request(self, request_size):
        client_request = ClientRequest(self, 0, request_size)
        self.request_queue.append(client_request)
        self.check_request_queue()

    def print_status(self):
        print("Client {}".format(self.ID))
        print("\tRequest queue: {}".format(len(self.request_queue)))
        print("\tSend queue: {}".format(len(self.pending_send_queue)))
        print()


    def get_id(self):
        return self.ID

# env = simpy.rt.RealtimeEnvironment(initial_time=0, factor=1.0, strict=True)

