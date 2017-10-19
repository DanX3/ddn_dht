from math import ceil, floor
from random import randint, seed
from typing import List, NewType, TypeVar
from collections import deque
from enum import Enum
from CmloidIdGenerator import CmloidIdGenerator


class MethodNotImplemented(Exception):
    def __init__(self, raising_class):
        self.raising_class = raising_class

    def __str__(self):
        return "{}: method still not implemented"


def get_formatted_time(time: int):
    time = str(time)[:-3]
    return (time[-12:-9] + " " + time[-9:-6] + " " + time[-6:-3] + " " + time[-3:]).strip()


def printmessage(id: int, message: str, time, done: bool=True):
    print(getmessage(id, message, time, done))


def getmessage(id, message, time, done=True):
    doneChar = u"\u2713" if done else u"\u279C"
    return "{:3s} {:15s} us <{}> {}".format(doneChar, get_formatted_time(time).rjust(15), id, message)


class CML_oid:
    def __init__(self, original_file, part_number):
        self.original_file = original_file
        self.part_number = part_number

    # def get_file(self):
    #     """
    #     :return: the original file that this CML_oid has been extracted from
    #     """
    #     return self.original_file
    #
    # def get_id(self):
    #     return self.part_number
    #
    # def get_total_parts(self):
    #     return self.original_file.get_parts()
    #
    # def get_id_tuple(self):
    #     return self.part_number, self.original_file.get_parts()
    #
    # def __str__(self):
    #     id = self.get_id_tuple()
    #     return "CML_oid({:3d}/{:3d} of '{}')".format(id[0]+1, id[1], self.original_file.get_name())
    #
    # def to_id(self):
    #     """
    #     Returns a string in the format of an id for the current CML_oid
    #     Example: CML_oid(12/32 of 'Hello') --> 'Hello:12'
    #     :rtype: str
    #     """
    #     return "{}:{}".format(self.original_file.get_name(), self.part_number)

    @staticmethod
    def get_size():
        """Returns the size of the elementary component CML_oid. Set to 128"""
        return 128


# class NetworkBuffer:
#     def __init__(self, file_parts, parity_group_id):


class Cmloid_struct:
    def __init__(self, device_id: int, cmloid_id_gen: CmloidIdGenerator):
        self.__device_id = device_id
        self.id = next(cmloid_id_gen)

    def get_device_id(self):
        return self.__device_id


class CMLoidSet:
    """
    Utility class to record a set of CML_oid instead of one by one, that turns out
    to be extremely inefficient
    """
    def __init__(self, start_idx: int, count: int, interval: int):
        self.__start_idx = start_idx
        self.__count = count
        self.__interval = interval
        self.__max_printed_vals = 5

    def get_count(self) -> int:
        return self.__count

    def __str__(self):
        result = "[ "
        for i in range(min(self.__count, self.__max_printed_vals)):
            result += str(self.__start_idx + i * self.__interval) + " "
        if self.__count > self.__max_printed_vals:
            result += "... "
            for i in range(max(self.__max_printed_vals, self.__count-self.__max_printed_vals), self.__count):
                result += str(self.__start_idx + i * self.__interval) + " "
        return "CMLoidSet(len {})({}])".format(self.__count, result)

    def pop(self, count: int):
        if count > self.__count:
            raise ValueError("Requested {}/{} elements for CMLoidSet".format(count, self.__count))
        result = CMLoidSet(self.__start_idx, count, self.__interval)
        self.__start_idx += count * self.__interval
        self.__count -= count
        return result


class Chunk:
    def __init__(self, filename: str, id: int, totparts: int, size: int):
        self.__filename = filename
        self.__id = id
        self.__totparts = totparts
        self.__size = size

    def get_filename(self):
        return self.__filename

    def get_id(self):
        return self.__id

    def get_size(self):
        return self.__size

    def get_tot_parts(self):
        return self.__totparts

    def __str__(self):
        return "Chunk('{}', {}, {} kB)".format(self.__filename, self.__id, self.__size)


class File:
    def __init__(self, name, size_kB):
        self.name = name
        self.size = size_kB

    def get_name(self):
        return self.name

    def get_size(self):
        return self.size

    def __str__(self):
        return "File({}, {} kB)".format(self.name, self.size)

    def get_chunks(self) -> List[Chunk]:
        """
        A chunk is nothing more than a List[filename:str, id:int, size:int]
        This function creates the chunks given a file
        :return: a list of parts from the given file
        """
        parts_count = int(ceil(self.size / 8192))
        s = self.size
        result = []
        for i in range(parts_count):
            result.append(Chunk(self.name, i, parts_count, min(s, 8192)))
            s -= 8192
        return result

    @staticmethod
    def get_filename_generator(client_id):
        int_name = 0
        prepended_number = str(client_id)

        while True:
            yield prepended_number + ":" + str(int_name)
            int_name += 1


class NetworkBuffer:
    def __init__(self, payload: List[CML_oid], read: bool=True):
        self.__payload = payload
        self.__read = read

    def get_payload(self) -> List[CML_oid]:
        return self.__payload

class FilePart:
    def __init__(self, file: File, start: int, end: int):
        self.__file = file
        if start > file.get_size():
            raise Exception("FilePart: requested start of part from %d with filesize %d"
                            .format(start, file.get_size()))
        self.__start = start
        self.__end = min(file.get_size(), end)
        if self.__end != end:
            print("WARNING Filepart: end of file has been corrected from {} to {}".format(end, self.__end))

    def pop_part(self, amount: int):
        amount_given = min(amount, self.__end - self.__start)
        self.__start += amount_given
        return FilePart(self.__file, self.__start - amount_given, self.__start)

    def get_size(self) -> int:
        return self.__end - self.__start

    def get_bound(self) -> (int, int):
        return self.__start, self.__end

    def get_filename(self) -> str:
        return self.__file.get_name()

    @staticmethod
    def get_parity_part(size: int):
        return FilePart(File('parity', size), 0, size)

    def __str__(self):
        return "FilePart('{}' ({}, {}) {} kB)".format(self.__file.get_name(), self.__start, self.__end, self.get_size())


class FileAggregator:
    """
    Class used by Client to collect parts or files received by servers
    It does not track actual missing parts, counting only the valid amount received
    """
    def __init__(self, filename: str, start: int, length: int):
        self.__filename = filename
        self.__start = start
        self.__end = start + length
        self.__len = length
        self.__amount_received = 0

    def add_part(self, part: FilePart) -> bool:
        part_bound = part.get_bound()
        amount_valid = max(0, min(part_bound[1], self.__end) - max(part_bound[0], self.__start))
        self.__amount_received += amount_valid
        return self.__amount_received == self.__len

class ClientRequest:
    def __init__(self, client_id: int, target_server_id: int, parity_group: int,
                 parity_id: int, read: bool=True):
        self.__client_id = client_id
        self.__target_server_id = target_server_id
        self.__read = read
        self.__file_parts = []
        self.__parity_id = parity_id
        self.__parity_group = parity_group

    def add_file_part(self, part: FilePart):
        self.__file_parts.append(part)

    def get_parts(self) -> List[FilePart]:
        return self.__file_parts

    def set_parts(self, parts: List[FilePart]):
        del self.__file_parts
        self.__file_parts = parts

    def get_client(self) -> int:
        return self.__client_id

    def get_target_id(self) -> int:
        return self.__target_server_id

    def is_read(self) -> bool:
        return self.__read

    def get_size(self):
        result = 0
        for part in self.__file_parts:
            result += part.get_size()
        return result

    def get_parity_group(self):
        return self.__parity_group

    def set_parity_group(self, parity_group: int):
        self.__parity_group = parity_group

    def __str__(self):
        rw = "<-" if self.__read else "->"
        result = "ClientRequest(id {}, parity map {}, {} {} {}):\n"\
            .format(self.__parity_id, self.__parity_group, self.__client_id, rw, self.__target_server_id)
        if self.__file_parts:
            for part in self.__file_parts:
                result += "\t{}\n".format(part)
        return result

    @staticmethod
    def get_cmloid_size() -> int:
        return 128


def get_requests_from_file(client, target, file, read=True):
    """
    Get the list of ClientRequest from a file
    :param client: the client instance
    :type client: Client
    :param target: id of the server, target of the file
    :type target: int
    :param file: the file that needs to be written
    :type file: File
    :param read: bool=True
    :return:deque[ClientRequest]
    """
    parts_num = int(ceil(file.get_size() / ClientRequest.get_cmloid_size()))
    return [ClientRequest(client, target, CML_oid(file, id), read) for id in range(parts_num)]


def simple_hash(filename: str, mod: int, offset: int=0) -> int:
    result = 0
    for letter in filename:
        result += ord(letter)
    return (result + offset) % mod


def generate_lookup_table(length):
    table = [i for i in range(length)]
    # important that the seed is fixed. I want always the same pseudo-random sequence
    seed(17)
    for i in range(length):
        idx1 = randint(0, length-1)
        idx2 = randint(0, length-1)
        table[idx1], table[idx2] = table[idx2], table[idx1]
    return table


if __name__ == "__main__":
    original = File('a', 2048)
    part = FilePart(original, 1024, 2048)
    print(part)
    # while part.get_size() != 0:
    #     print(aggregator.add_part(part.pop_part(2048)))

