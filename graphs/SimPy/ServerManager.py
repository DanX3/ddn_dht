import simpy
from Server import Server
from Contract import Contract
from Utils import *

class ServerManager:
    def __init__(self, env, server_params, misc_params, clients):
        self.env = env
        self.server_params = server_params
        self.misc_params = misc_params
        self.servers = []
        for i in range(self.server_params[Contract.S_SERVER_COUNT]):
            self.servers.append(
                    Server(self.env, i, self.server_params, self.misc_params, clients, self))
        self.server_resources = simpy.Resource(self.env, len(self.servers))

        # This will keep the queue for the client requests
        self.requests = {}

    def get_server_by_id(self, ID):
        for server in self.servers:
            if ID == server.get_id():
                return server

    def request_server(self, clientRequest):
        target_server = self.servers[clientRequest.get_target_ID()]
        target_server.add_request(clientRequest)
        print("Client {} requested Server {}".format(clientRequest.get_client().get_id(), target_server.get_id()))
        yield self.env.timeout(12)

    def release_server(self, server_ID):
        self.server_resources.release(self.requests[server_ID])
        if len(self.requests[server_ID]) == 0:
            print("server {} is available".format(server_ID))
            self.servers[server_ID].set_availability(True)
        else:
            printmessage(0, "requests[{}].pop()".format(server_ID), self.env.now)
            self.env.process(self.servers[server_ID].process_request(
                self.requests[server_ID].pop(0)))


    def get_users_count(self):
        return self.server_resources.count

    def get_resource_capacity(self):
        return self.server_resources.capacity

    def get_queue(self):
        return self.server_resources.queue

    def get_server_count(self):
        return len(self.servers)
