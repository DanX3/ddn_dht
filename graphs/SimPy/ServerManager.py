import simpy
from Server import Server
from Contract import Contract
from Utils import *
from FunctionDesigner import Function2D
from HUB import HUB


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
        # self.__HUB = HUB(env, int(misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8)
        self.__HUB = simpy.Resource(env)
        self.__overhead = int(self.misc_params[Contract.M_NETWORK_LATENCY_MS])
        self.__max_bandwidth = int(self.misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8
        self.__time_function = Function2D.get_bandwidth_model(self.__overhead, self.__max_bandwidth)

    def get_server_by_id(self, ID):
        for server in self.servers:
            if ID == server.get_id():
                return server

    def request_server(self, request: ClientRequest):
        """
        Send the chunk request to the servers
        It uses HUB resources. Every request is queued.
        Every request of 1MB is sent at max bandwidth
        A request smaller takes more time, based on Diagonal Limit configuration
        :param request: client request holding the chunk to send
        :return: yield the time required for the transaction to complete
        """
        size = min(1024, request.get_chunk().get_size())

        mutex_request = self.__HUB.request()
        yield mutex_request

        # I try to round to the available bandwidth, but if there is no available
        # I'll do the computation with the max bandwidth available
        time_required = int(self.__time_function(size) / 1e6)
        yield self.env.timeout(time_required)
        self.__HUB.release(mutex_request)
        # uncomment to see the plot of the situation
        # Plotter.plot_bandwidth_model(overhead, available_bw, packet_size_kB=send_group.get_size())
        self.servers[request.get_target_ID()].add_request(request)

    def single_request_server(self, req):
        # sendgroup = SendGroup()
        # paritygroup = ParityGroup()
        # paritygroup.add_request(req)
        # sendgroup.add_request(paritygroup)
        self.env.process(self.request_server(req))

    def release_server(self, server_id):
        self.server_resources.release(self.requests[server_id])
        if len(self.requests[server_id]) == 0:
            print("server {} is available".format(server_id))
            self.servers[server_id].set_availability(True)
        else:
            printmessage(0, "requests[{}].pop()".format(server_id), self.env.now)
            self.env.process(self.servers[server_id].process_request(
                self.requests[server_id].pop(0)))

    def get_users_count(self):
        return self.server_resources.count

    def get_resource_capacity(self):
        return self.server_resources.capacity

    def get_queue(self):
        return self.server_resources.queue

    def get_server_count(self):
        return len(self.servers)
