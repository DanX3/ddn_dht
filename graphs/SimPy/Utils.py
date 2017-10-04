from math import ceil, floor
from random import randint, seed
from typing import List
from collections import deque
from enum import Enum


class MethodNotImplemented(Exception):
    def __init__(self, raising_class):
        self.raising_class = raising_class

    def __str__(self):
        return "{}: method still not implemented"


def printmessage(id: int, message: str, time, done: bool=True):
    print(getmessage(id, message, time, done))


def getmessage(id, message, time, done=True):
    doneChar = u"\u2713" if done else u"\u279C"
    time = str(time)[:-3]
    dottedtime = (time[-12:-9] + " " + time[-9:-6] + " " + time[-6:-3] + " " + time[-3:]).strip()
    return "{:3s} {:15s} us <{}> {}".format(doneChar, dottedtime.rjust(15), id, message)


class CML_oid:
    def __init__(self, original_file, part_number):
        self.original_file = original_file
        self.part_number = part_number

    def get_file(self):
        """
        :return: the original file that this CML_oid has been extracted from
        """
        return self.original_file

    def get_id(self):
        return self.part_number

    def get_total_parts(self):
        return self.original_file.get_parts()

    def get_id_tuple(self):
        return self.part_number, self.original_file.get_parts()

    def __str__(self):
        id = self.get_id_tuple()
        return "CML_oid({:3d}/{:3d} of '{}')".format(id[0]+1, id[1], self.original_file.get_name())

    def to_id(self):
        """
        Returns a string in the format of an id for the current CML_oid
        Example: CML_oid(12/32 of 'Hello') --> 'Hello:12'
        :rtype: str
        """
        return "{}:{}".format(self.original_file.get_name(), self.part_number)

    @staticmethod
    def get_size():
        """Returns the size of the elementary component CML_oid. Set to 128"""
        return 128


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
        self.parts = ceil(size_kB / ClientRequest.get_cmloid_size())

    def get_name(self):
        return self.name

    def get_size(self):
        return self.size

    def get_parts(self):
        return self.parts

    def get_cmloid_generator(self):
        for part in range(self.parts):
            yield CML_oid(self, part)

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


class MetaFile(File):
    def get_cmloid_generator(self):
        raise Exception("Not an actual file. Only metadata")

    def __str__(self):
        return "MetaFile({}, {} kB)".format(self.name, self.size)


class NetworkBuffer:
    def __init__(self, payload: List[CML_oid], read: bool=True):
        self.__payload = payload
        self.__read = read

    def get_payload(self) -> List[CML_oid]:
        return self.__payload


class ClientRequest:
    def __init__(self, client, target_server_id: int, chunk: Chunk, read: bool=True):
        self.__client = client
        self.__target_server_id = target_server_id
        self.__chunk = chunk
        self.__read = read

    def get_client(self):
        return self.__client

    def get_target_ID(self) -> int:
        return self.__target_server_id

    # def get_cmloid(self):
    #     return self.cmloid
    #

    def get_chunk(self) -> Chunk:
        return self.__chunk

    def is_read(self):
        return self.__read

    def __str__(self):
        result = "ClientRequest {}:\n".format("READ" if self.__read else "WRITE")
        result += "\tfrom Client {} to Server {}\n".format(self.__client.get_id(), self.__target_server_id)
        result += "\t{}\n".format(self.__chunk)
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


def generate_lookup_table(length):
    table = [i for i in range(length)]
    # important that the seed is fixed. I want always the same pseudo-random sequence
    seed(17)
    for i in range(length):
        idx1 = randint(0, length-1)
        idx2 = randint(0, length-1)
        table[idx1], table[idx2] = table[idx2], table[idx1]
    return table


class SendGroup:
    def __init__(self):
        self.requests = []
        self.size = 0

    def add_request(self, parity_req):
        self.requests.append(parity_req)
        for req in parity_req.get_requests():
            if not req.is_read():
                self.size += ClientRequest.get_cmloid_size()
        
    def get_target_ID(self):
        if self.requests:
            return self.requests[0].get_target_ID()
        else:
            return -1

    def get_client(self):
        if self.requests:
            return self.requests[0].get_client()
        else:
            return -1

    def get_requests(self):
        return self.requests

    def get_size(self):
        size = self.size
        if size == 0:
            size = max(len(self.requests) / 5, 1)
        return size


class ParityGroup(SendGroup):
    def __init__(self):
        self.requests = []
        self.is_read = None
        self.size = 0

    def get_hash_time(self):
        return len(self.requests) * 20

    def get_size(self):
        return self.size

    def add_request(self, client_req):
        self.requests.append(client_req)
        if client_req.is_read():
            self.size += client_req.get_filesize()
            self.is_read = True
        else:
            self.is_read = False

    def is_read(self):
        return self.is_read

    def get_requests(self):
        return self.requests


if __name__ == "__main__":
    file = File("mklmklmkl", 257)
