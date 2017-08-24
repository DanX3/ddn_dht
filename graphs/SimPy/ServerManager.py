import simpy
from Server import Server
from Contract import Contract

class ServerManager:
    def __init__(self, env, server_params, misc_params):
        self.env = env
        self.server_params = server_params
        self.misc_params = misc_params
        self.servers = []
        for i in range(self.server_params[Contract.S_SERVER_COUNT]):
            self.servers.append(
                    Server(self.env, i, self.server_params, self.misc_params))
        self.server_resources = simpy.Resource(self.env, len(self.servers))
        self.requests = {}

    def get_server_by_id(self, ID):
        for server in self.servers:
            if ID == server.get_id():
                return server

    def request_server(self, client_ID):
        # get access to a server
        self.requests[client_ID] = self.server_resources.request()
        yield self.requests[client_ID]

        #now choose which server
        most_free_server_id = -1
        min_queue_length = 2e31
        for server in self.servers:
            if server.is_available():
                most_free_server_id = server.get_id()
                break

        self.chosen_server = self.get_server_by_id(most_free_server_id)

    def release_server(self, client_ID):
        self.server_resources.release(self.requests[client_ID])

    def get_users_count(self):
        return self.server_resources.count

    def get_resource_capacity(self):
        return self.server_resources.capacity
