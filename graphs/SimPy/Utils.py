def printmessage(ID, message, time, done=True):
    doneChar = u"\u2713" if done else u"\u279C"
    print(doneChar.rjust(2), (str(time) + "us").rjust(12), ("%d)"%ID).rjust(3), str(message))

class ClientRequest:
    def __init__(self, client, target_server_ID, filesize_kb):
        self.client = client
        self.target_server_ID = target_server_ID
        self.filesize_kb = filesize_kb

    def get_client(self):
        return self.client

    def get_target_ID(self):
        return self.target_server_ID

    def set_new_target_ID(self, new_target_ID):
        self.target_server_ID = new_target_ID

    def get_filesize(self):
        return self.filesize_kb


