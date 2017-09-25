import simpy
from Server import Server
from Contract import Contract
from Utils import *
from FunctionDesigner import Function2D, Plotter
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
        self.HUB = HUB(env, int(misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8)

    def get_server_by_id(self, ID):
        for server in self.servers:
            if ID == server.get_id():
                return server

    def request_server(self, send_group):
        """
        sending the packed request to the servers
        it uses HUB resources. Should force a lower bandwidth in case of traffic
        :param send_group: the formed request
        :return: yield the time required for the transaction to complete
        """
        target_server = self.servers[send_group.get_target_ID()]
        overhead = int(self.misc_params[Contract.M_NETWORK_LATENCY_MS])
        # max_bandwidth = int(self.misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8
        size = send_group.get_size()

        mutex_request = self.HUB.request_mutex()
        yield mutex_request
        available_bw = self.HUB.get_available_bw()

        # I try to round to the available bandwidth, but if there is no available
        # I'll do the computation with the max bandwidth available
        if available_bw == 0:
            available_bw = int(self.misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8
        time_required = Function2D.get_bandwidth_model(overhead, available_bw)(size) / 1e6
        avg_bandwidth = int(size / time_required)
        request, bw_allowed = self.HUB.request_bandwidth(avg_bandwidth)
        self.HUB.release_mutex(mutex_request)

        yield request
        new_time = Function2D.get_bandwidth_model(overhead, bw_allowed)(size)
        yield self.env.timeout(new_time)
        self.HUB.release_bandwidth(bw_allowed)

        # uncomment to see the plot of the situation
        # Plotter.plot_bandwidth_model(overhead, available_bw, packet_size_kB=send_group.get_size())
        target_server.add_request(send_group)

    def single_request_server(self, req):
        sendgroup = SendGroup()
        paritygroup = ParityGroup()
        paritygroup.add_request(req)
        sendgroup.add_request(paritygroup)
        self.env.process(self.request_server(sendgroup))

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
