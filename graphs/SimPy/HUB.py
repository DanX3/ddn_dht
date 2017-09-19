import simpy

class HUB:
    def __init__(self, env, max_bandwidth_kBps):
        self.__container = simpy.Container(env, capacity=max_bandwidth_kBps)

    def request_bandwidth(self, bandwidth_required_kBps):
        """
        Make a request to fill the HUB. If the reqeust is too big but there is space, it gets adapted
        instead of blocking the request
        :param bandwidth_required_kBps: bandwidth required from the HUB
        :return: the request done. Remember to release it after usage
        """
        required_bw = bandwidth_required_kBps
        if self.__container.level < self.__container.capacity:
            free_bw = self.__container.capacity - self.__container.level
            if bandwidth_required_kBps >= free_bw:
                return self.__container.put(free_bw), free_bw
            else:
                return self.__container.put(required_bw), required_bw
        else:
            return self.__container.put(required_bw), required_bw

    def release_bandwidth(self, bandwidth):
        self.__container.get(bandwidth)

    def get_capacity(self):
        return self.__container.capacity

    def get_level(self):
        return self.__container.level


def perform_request(env, myhub, amount):
    req, allowed_bw = myhub.request_bandwidth(amount)
    yield req
    print("{:4d} start {}/{}".format(env.now, myhub.get_level(), myhub.get_capacity()))
    yield env.timeout(int(1000/allowed_bw))
    myhub.release_bandwidth(allowed_bw)
    print("{:4d} end   {}/{}".format(env.now, myhub.get_level(), myhub.get_capacity()))


if __name__ == "__main__":
    env = simpy.Environment()
    hub = HUB(env, 100)
    env.process(perform_request(env, hub, 1000))
    env.process(perform_request(env, hub, 10))
    env.run()
