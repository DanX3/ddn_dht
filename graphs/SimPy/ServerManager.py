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
        max_bandwidth = int(self.misc_params[Contract.M_HUB_BW_Gbps]) * 1e6 / 8
        size = send_group.get_size()
        time_required = Function2D.get_bandwidth_model(overhead, max_bandwidth)(size) / 1e6
        avg_bandwidth = send_group.get_size() / time_required
        # self.HUB.request_bandwidth(avg_bandwidth)

        if self.HUB.is_available():
            allowed_bw = self.HUB.request_bandwidth(avg_bandwidth)
            print("sending at {}/{}".format(allowed_bw, avg_bandwidth))
        else:
            printmessage(0, "HUB Filled, waiting", self.env.now, False)
            request = self.HUB.get_queue_request()
            yield request
            self.HUB.release_request(request)
            printmessage(0, "HUB freed", self.env.now, True)

        # Plotter.plot_bandwidth_model(overhead, max_bandwidth, packet_size_kB=send_group.get_size())
        yield self.env.timeout(time_required)
        target_server.add_request(send_group)

    def request_server_single_req(self, clientRequest):
        target_server = self.servers[clientRequest.get_target_ID()]
        target_server.add_single_request(clientRequest)
        yield self.env.timeout(12)

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

