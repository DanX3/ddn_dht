def printmessage(ID, message, time, done=True):
    doneChar = u"\u2713" if done else u"\u279C"
    print(doneChar.rjust(2), (str(time) + "us").rjust(12), ("%d)"%ID).rjust(3), str(message))


class ClientRequest:
    def __init__(self, client, target_server_ID, filesize_kb, read=True):
        self.client = client
        self.target_server_ID = target_server_ID
        self.filesize_kb = filesize_kb
        self.read = read

    def get_client(self):
        return self.client

    def get_target_ID(self):
        return self.target_server_ID

    def set_new_target_ID(self, new_target_ID):
        self.target_server_ID = new_target_ID

    def get_filesize(self):
        return self.filesize_kb
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


class SendGroup:
    def __init__(self):
        self.requests = []

    def add_request(self, req):
        self.requests.append(req)
        
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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


class ParityGroup(SendGroup):
    def __init__(self):
        self.requests = []

    def get_hash_time(self):
        return len(self.requests) * 20


