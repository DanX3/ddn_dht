from FunctionDesigner import Function2D

class StorageDevice():
    def __init__(self, capacity_kb, bandwidth_kb_per_sec, latency_ms):
        self.capacity_kb = capacity_kb
        self.used_memory = 0
        self.bandwidth = bandwidth_kb_per_sec
        self.latency = latency_ms

    def process_transfer(self, filesize_kb):
        """

        :param filesize_kb: the file size in Kb
        :return: the ms required to complete the transaction. -1 if full
        """
        if self.used_memory + filesize_kb > self.capacity_kb:
            return -1

        self.used_memory += filesize_kb
        return Function2D.get_diag_limit(self.latency*1000.0, 1e6/self.bandwidth)(float(filesize_kb))

    def get_capacity(self):
        return self.capacity_kb

    def get_used_memory(self):
        return self.used_memory

    def get_bandwidth(self):
        return self.bandwidth

    def get_latency(self):
        return self.latency


if __name__ == "__main__":
    device = StorageDevice(100.0*2e6, 1*2e3, 50)
    print(device.process_transfer(1*2e3))