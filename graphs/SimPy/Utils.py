def printmessage(ID, message, time, done=True):
    doneChar = u"\u2713" if done else u"\u279C"
    print(doneChar.rjust(2), (str(time) + "us").rjust(12), ("%d)"%ID).rjust(3), str(message))


class File:
    def __init__(self, name, size_kB):
        self.name = name
        self.size = size_kB

    def get_name(self):
        return self.name

    def get_size(self):
        return self.size

    def to_string(self):
        return "File({}, {} kB)".format(self.name, self.size)

    @staticmethod
    def get_filename_generator(client_id):
        int_name = 0
        prepended_number = str(client_id)

        while True:
            yield prepended_number + str(int_name)
            int_name += 1


class ClientRequest:
    def __init__(self, client, target_server_id, file, read=True):
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

    def get_size(self):
        if self.read:
            return 1
        else:
            return self.file.get_size()

    def is_read(self):
        return self.read

    def to_string(self):
        result = "ClientRequest {}:\n".format("READ" if self.read else "WRITE")
        result += "\tfrom {} to {}\n".format(self.client.get_id(), self.target_server_ID)
        result += "\tfile {}\n".format(self.file.to_string())
        return result


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class SendGroup:
    def __init__(self):
        self.requests = []
        self.size = 0

    def add_request(self, parity_req):
        self.requests.append(parity_req)
        for req in parity_req.get_requests():
            if not req.is_read():
                self.size += req.get_filesize()
        
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




