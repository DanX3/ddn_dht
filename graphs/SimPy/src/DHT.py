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
        self.__files = {}  # Dict[File]
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

    def add_file(self, file: File):
        self.__files[file.get_name()] = file

    def remove_file(self, file: File):
        del self.__files[file.get_name()]


if __name__ == "__main__":
    set = CMLoidSet(2, 20, 4)
    print(set)
    otherSet = set.pop(8)
    print(set)
    print(otherSet)
