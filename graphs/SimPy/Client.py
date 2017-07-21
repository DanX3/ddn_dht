from Logger import Logger
from Server import Server
from Utils import *
from FunctionDesigner import Function2D

class Client:
    def __init__(self, ID, env, servers, config):
        self.env = env
        self.ID = ID
        self.servers = servers;
        self.config = config
        self.env.process(self.run())
        self.logger = Logger(ID, env)
        self.tokens = 24

    def hash_address(self):
        # yield self.env.timeout(2)
        yield self.env.process(self.logger.work(Function2D.gauss(30, 10)))
        printmessage(self.ID, "X", self.env.now)

    def get_server_by_id(self, ID):
        for server in self.servers:
            if ID == server.get_id():
                return server

    def find_most_free_server(self):
        most_free_server_id = -1
        max_queue_length = 2e31
        for server in self.servers:
            if server.is_available():
                return server.get_id()
            elif server.get_queue_length() < max_queue_length:
                max_queue_length = server.get_queue_length()
                most_free_server_id = server.get_id()
        return most_free_server_id

    def decide_which_server(self):
        yield self.env.process(self.logger.work(Function2D.gauss(6, 3)))
        # print "%d) decided server  -  %f" % (self.ID, self.env.now)
        printmessage(self.ID, "->", self.env.now)
    
    def actually_decide_which_server(self):
        return self.get_server_by_id(self.find_most_free_server())

    def send_request(self, server_chosen):
        yield self.env.process(self.hash_address())
        yield self.env.process(self.decide_which_server())
        yield self.env.process(server_chosen.write_meta_to_DHT(self.ID))

    def check_tokens(self):
        if self.tokens > 1:
            self.tokens -= 1
        else:
            yield self.timeout(self.config["C_TOKEN_REFRESH"])

    def run(self):
        printmessage(self.ID, "?", self.env.now)

        server_chosen = self.actually_decide_which_server()
        request = server_chosen.resource.request()
        yield request
        printmessage(self.ID, "+", self.env.now)
        yield self.env.process(self.check_tokens())
        yield self.env.process(self.send_request(server_chosen))
        server_chosen.resource.release(request)
        if self.ID == 3:
            self.logger.print_info()
            self.logger.print_info_to_file("Client_{:d}".format(self.ID))

# env = simpy.rt.RealtimeEnvironment(initial_time=0, factor=1.0, strict=True)

