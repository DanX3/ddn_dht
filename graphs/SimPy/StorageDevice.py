from FunctionDesigner import Function2D
from Utils import printmessage
import simpy


def filename_generator():
    int_name = 0

    while True:
        int_name += 1
        yield str(int_name)


class File:
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def get_name(self):
        return self.name

    def get_size(self):
        return self.size


class StorageDevice:
    def __init__(self, env, capacity_kb, bandwidth_kB_per_sec, latency_ms):
        self.env = env
        self.capacity_kb = capacity_kb
        self.__container = simpy.Container(env, capacity_kb)
        self.__mutex = simpy.Resource(env, 1)
        self.bandwidth = bandwidth_kB_per_sec
        self.latency = latency_ms
        self.time_function = Function2D.get_bandwidth_model(latency_ms, bandwidth_kB_per_sec)
        self.stored_files = {}

        # if a file is transferred to another server, it should reported here
        # in order to ask directly to the correct server
        self.transfer_list = {}

    def write_file(self, file):
        req = self.__mutex.request()
        yield req
        if file.get_size() > self.__free_space():
            # move or flush some files
            yield self
            pass
        else:
            yield self.env.timeout(314)

        yield self.env.timeout(self.time_function(file.get_size()))
        self.stored_files[file.get_name()] = file

        self.__mutex.release(req)
        printmessage(0, "finished writing " + file.get_name(), self.env.now)

    def __free_space(self):
        return self.__container.capacity - self.__container.level

    def get_capacity(self):
        return self.capacity_kb

    def get_bandwidth(self):
        return self.bandwidth

    def get_latency(self):
        return self.latency


def just_for_yield_function(env):
    gen = filename_generator()
    yield env.process(device.write_file(File(next(gen), 100e3)))
    yield env.process(device.write_file(File(next(gen), 1e6)))


if __name__ == "__main__":
    env = simpy.Environment()
    device = StorageDevice(env, 500e6, 100e3, 50)
    env.process(just_for_yield_function(env))

    env.run()
