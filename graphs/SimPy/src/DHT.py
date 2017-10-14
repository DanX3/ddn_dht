import simpy
from Utils import *
from typing import List
from collections import deque


class NotInDHTError(Exception):
    def __init__(self, file_requested):
        self.__file_requested = file_requested

    def __str__(self):
        return "File requested '{}' not present in DHT".format(self.__file_requested)


class DHT:
    def __init__(self, server_count: int, device_per_server: int):
        self.__server_count = server_count
        self.__devs_per_server = device_per_server
        self.__files = []  # List[(str, int)]
        self.__parities = []

    def get_cmloids(self, file: File, offset: int, length: int):
        filename = file.get_name()
        if filename not in self.__files:
            raise NotInDHTError(filename)

        starting_server = (simple_hash(filename, self.__server_count)
                           + int(ceil(offset / CML_oid.get_size()))) \
                          % self.__server_count
        cmloids_count = int(ceil(length / CML_oid.get_size()))
        starting_cmloid_id = int(offset / CML_oid.get_size())
        for i in range(starting_cmloid_id, starting_cmloid_id + cmloids_count):
            print(self.get_device_id(file, i))

    @staticmethod
    def get_device_id(self, file: File, cmloid_id: int) -> int:
        return simple_hash(file.get_name(), self.__devs_per_server, cmloid_id)

    def add_file_part(self, filename: str, part_size: int):
        self.__files.append((filename, part_size))

    def remove_file(self, file: File):
        del self.__files[file.get_name()]

    def get_file_cmloids(self, filename_requested: str) -> List[int]:
        """
        Given a filename, returns a list containing the cmloid per device.
        Use this to know how much data is needed to be gathered from every device
        :param filename: the file name
        :return: a list of int. Elsewhere is also known as 'Load'
        """
        load = [0] * self.__devs_per_server
        counter = 0
        cmloid_size = CML_oid.get_size()
        for filename, partsize in self.__files:
            if filename == filename_requested:
                start_pos = int(counter / cmloid_size)
                end_pos = start_pos + int(partsize / cmloid_size) + 1
                # print("({}, {})".format(start_pos, end_pos))
                for i in range(start_pos, end_pos):
                    load[i % self.__devs_per_server] += 1
            # print(counter)
            counter += partsize
        # print(counter)
        return load


if __name__ == "__main__":
    dht = DHT(3, 6)
    # dht.add_file_part('a', 200)
    # dht.add_file_part('b', 10)
    # dht.add_file_part('c', 128+45)
    dht.add_file_part('c', int(2**20 - 1))
    dht.add_file_part('d', 1)
    dht.add_file_part('e', 1)
    dht.add_file_part('f', 127)
    dht.add_file_part('g', 1)
    for i in "cdefg":
        print(dht.get_file_cmloids(i))
