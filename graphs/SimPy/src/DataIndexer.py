from Utils import *
import numpy as np
from collections import deque

class Indexer:
    def __init__(self, disks_count: int, cmloid_size: int):
        self.__disks_count = disks_count
        self.__cmloids_size = cmloid_size
        self.__filenames = {}  # Dict[str, array('H', disks_count)
        self.__packets = {}  # Dict[int, WriteRequest]
        self.__round_robin_gen = round_robin_gen(disks_count)
        self.__disks = []
        for i in range(disks_count):
            self.__disks.append(deque())

    def write_packet(self, request: WriteRequest):
        self.__packets[request.get_parity_id()] = request
        for part in request.get_parts():
            addition = None
            total_parts = ceil(part.get_size() / self.__cmloids_size)
            # Just a small optimization in case parts count and disks match
            if  total_parts == self.__disks_count:
                addition = np.array([1] * self.__disks_count, np.uint16)
                for queue in self.__disks:
                    queue.append(request.get_parity_id())
            else:
                addition = np.array([0] * self.__disks_count, np.uint16)
                while part.get_size() > 0:
                    idx = next(self.__round_robin_gen)
                    addition[idx] += 1
                    self.__disks[idx].append(request.get_parity_id())
                    part.pop_filename(self.__cmloids_size)
            if part.get_filename() in self.__filenames:
                self.__filenames[part.get_filename()] += addition
            else:
                self.__filenames[part.get_filename()] = addition

    def __str__(self):
        result = "Packets:\n"
        for parity_id, part in self.__packets.items():
            result += "\t" + str(part) + "\n"

        for filename, parts in self.__filenames.items():
            result += filename + ", " + str(parts) + "\n"

        result +='\n'
        for disk in self.__disks:
            for id in disk:
                result += str(id) + ', '
            result += '\n'

        return result


def write_file(name: str, size, indexer: Indexer, rr):
    file = File(name, size)
    parts = FilePart(file, 0, file.get_size())
    while parts.get_size() != 0:
        request = WriteRequest(0, 1, 97, next(rr))
        request.set_parts([parts.pop_part(1024)])
        indexer.write_packet(request)

if __name__ == "__main__":
    rr  = infinite_gen()
    indexer = Indexer(8, 128)
    write_file('x', 1, indexer, rr)
    write_file('a', 1, indexer, rr)
    write_file('b', 1, indexer, rr)
    write_file('y', 1, indexer, rr)

    print((indexer))
