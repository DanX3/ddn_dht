import simpy
from math import ceil

class MutexNotOwnedError(Exception):
    pass


class HUB:
    def __init__(self, env, max_bandwidth_kBps):
        self.__container = simpy.Container(env, capacity=max_bandwidth_kBps)
        self.__mutex = simpy.Resource(env, capacity=1)
        self.pending_mutex_release = None

    def request_bandwidth(self, bandwidth_required_kBps):
        """
        Make a request to fill the HUB. If the reqeust is too big but there is space, it gets adapted
        instead of blocking the request
        :param bandwidth_required_kBps: bandwidth required from the HUB
        :return: (the request done, the amount of bandwidth allowed) Remember to release the bandwidth
        once finished
        """
        if self.__mutex.count == 0:
            raise MutexNotOwnedError

        capacity = self.__container.capacity
        required_bw = bandwidth_required_kBps
        required_bw = ceil(100 * (min(required_bw, capacity) / capacity)) / 100.0 * capacity

        if not self.__is_full():
            free_bw = int(self.__container.capacity - self.__container.level)
            if bandwidth_required_kBps >= free_bw:
                self.__mutex.count = 1
                return self.__container.put(free_bw), free_bw
            else:
                return self.__container.put(required_bw), required_bw
        else:
            return self.__container.put(required_bw), required_bw

    def release_bandwidth(self, bandwidth):
        self.__container.get(bandwidth)
        if self.pending_mutex_release is not None:
            self.release_mutex(self.pending_mutex_release)

    def request_mutex(self):
        return self.__mutex.request()

    def release_mutex(self, req):
        if not self.__is_full():
            self.__mutex.release(req)
        else:
            self.pending_mutex_release = req

    def __is_full(self):
        return self.__container.level == self.__container.capacity

    def get_capacity(self):
        return self.__container.capacity

    def get_level(self):
        return self.__container.level

    def get_available_bw(self):
        return self.__container.capacity - self.__container.level

    def print_status(self):
        print("HUB")
        print("\t{} / {}".format(self.__container.level, self.__container.capacity))
        print()


def perform_request(env, myhub, amount):
    req, allowed_bw = myhub.request_bandwidth(amount)
    yield req
    print("{:4d} start {}/{}".format(env.now, myhub.get_level(), myhub.get_capacity()))
    yield env.timeout(int(1000000/allowed_bw))
    myhub.release_bandwidth(allowed_bw)
    print("{:4d} end   {}/{}".format(env.now, myhub.get_level(), myhub.get_capacity()))


if __name__ == "__main__":
    env = simpy.Environment()
    hub = HUB(env, 10000)
    env.process(perform_request(env, hub, 10))
    env.process(perform_request(env, hub, 100000))
    env.run()
