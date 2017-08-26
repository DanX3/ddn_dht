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
        self.servers_manager = servers_manager;
        self.config = config
        self.misc_params = misc_params
        self.env.process(self.run())
        self.logger = Logger(ID, env)
        self.tokens = 24
        self.chosen_server = -1;

        # requests sent. The ints shows the size of KB of the request
        self.request_queue = []
        self.current_request = 0

        self.pending_parity_queue = []
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
        treshold = self.config[Contract.C_PENDING_PARITY_TRESHOLD]
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


    def send_request(self, chosen_server):
        yield self.env.process(self.pending_parity_group(self.request_queue.pop(0)))
        yield self.env.process(self.forming_parity_group())
        yield self.env.process(self.pending_send_grouping())
        # yield self.env.process(self.hash_address())
        # yield self.env.process(self.decide_which_server())
        # start = self.env.now
        # yield self.env.process(chosen_server.write_meta_to_DHT(self.ID))
        # self.logger.add_idle_time(self.env.now - start)

    def check_tokens(self):
        if self.tokens > 0:
            self.tokens -= 1
        else:
            yield self.timeout(self.config[Contract.C_TOKEN_REFRESH])

    def receive_answer(self, req):
        printmessage(self.ID, "Received {}".format(req.get_filesize()), self.env.now)

    def run(self):
        if self.request_queue:
            self.current_request = self.request_queue.pop(0)
        else:
            print ("Client {} has finished all tasks".format(self.ID))
            return

        yield self.env.process(self.check_tokens())
        yield self.env.process(self.send_request(self.chosen_server))

        start = self.env.now
        target_server_ID = randint(0, len(self.servers_manager.servers)-1)
        print("Client {} requested Server {}".format(self.ID, target_server_ID))
        clientRequest = ClientRequest(self, target_server_ID, self.ID * 100)
        yield self.env.process(self.servers_manager.request_server(clientRequest))
        self.logger.add_idle_time(self.env.now - start)

    def add_request(self, request_size):
        self.request_queue.append(request_size)

    def get_id(self):
        return self.ID

# env = simpy.rt.RealtimeEnvironment(initial_time=0, factor=1.0, strict=True)

