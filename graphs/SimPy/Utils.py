from math import ceil


class MethodNotImplemented(Exception):
    def __init__(self, raising_class):
        self.raising_class = raising_class

    def __str__(self):
        return "{}: method still not implemented"


def printmessage(ID, message, time, done=True):
    doneChar = u"\u2713" if done else u"\u279C"
    print(doneChar.rjust(2), (str(time) + "us").rjust(12), ("%d)"%ID).rjust(3), str(message))


class CML_oid:
    def __init__(self, original_file, part_number):
        self.original_file = original_file
        self.part_number = part_number

    def get_file(self):
        return self.original_file

    def get_id(self):
        return self.part_number

    def get_id_tuple(self):
        return self.part_number, self.original_file.get_parts()

    def to_string(self):
        id = self.get_id_tuple()
        return "CML_oid({}/{} of '{}')".format(id[0]+1, id[1], self.original_file.get_name())

    def to_id(self):
        return "{}:{}".format(self.original_file.get_name(), self.part_number)

    @staticmethod
    def get_size():
        return 128


class File:
    def __init__(self, name, size_kB):
        self.name = name
        self.size = size_kB
        self.parts = ceil(size_kB / 128)

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

    @staticmethod
    def get_filename_generator(client_id):
        int_name = 0
        prepended_number = str(client_id)

        while True:
            yield prepended_number + str(int_name)
            int_name += 1


class ClientRequest:
    def __init__(self, client, file, read=True):
        self.client = client
        self.target_server_ID = target_server_id
        self.file = file
        self.read = read

    def get_client(self):
        return self.client

    def get_target_ID(self):
        return self.target_server_ID

    def set_new_target_ID(self, new_target_ID):
        self.target_server_ID = new_target_ID

    def get_file(self):
        return self.file

    def is_read(self):
        return self.read

    def to_string(self):
        result = "ClientRequest {}:\n".format("READ" if self.read else "WRITE")
        result += "\tfrom {} to {}\n".format(self.client.get_id(), self.target_server_ID)
        result += "\t{}\n".format(self.file)
        return result

    @staticmethod
    def get_cmloid_size():
        return 128


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


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
    file = File("mklmklmkl", 300)
    for part in file.get_cmloid_generator():
        print(part.to_id())
