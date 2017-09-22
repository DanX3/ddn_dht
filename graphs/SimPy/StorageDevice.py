from FunctionDesigner import Function2D
from Utils import printmessage
import simpy
from Utils import File




class DiskTooSmallError(Exception):
    pass


class DiskIdInconsistency(Exception):
    pass


class DiskIdNotation:
    def __init__(self, server_id, disk_id, label):
        self.server_ID = server_id
        self.disk_ID = disk_id
        self.label = label

    def to_string(self):
        return str(self.server_ID) + ":" + str(self.disk_ID) + ":" + self.label

    def get_server_id(self):
        return self.server_ID

    def get_disk_id(self):
        return self.disk_ID

    def get_label(self):
        return self.label

    def equal(self, otherId):
        return self.server_ID == otherId.get_server_id() and \
               self.disk_ID == otherId.get_disk_id() and \
               self.label == otherId.get_label()

    @staticmethod
    def build_from_string(fromstring):
        parsed_values = fromstring.split(":")
        if len(parsed_values) != 3:
            raise ValueError("Invalid base string for disk notation: " + fromstring)
        if parsed_values[2] != 'm' and parsed_values[2] != 'd':
            raise ValueError("Invalid value for disk label: " + parsed_values[2])
        return DiskIdNotation(int(parsed_values[0]), int(parsed_values[1]), parsed_values[2])

    @staticmethod
    def get_disk_id_generator(server_id, is_data_disk):
        # set if it is a data disk or metadata one
        disk_label = 'd'
        if not is_data_disk:
            disk_label = 'm'
        counter = 0
        while True:
            yield DiskIdNotation(server_id, counter, disk_label)
            counter += 1


class StorageDevice:
    def __init__(self, env, id, capacity_kb, reading_kBps, writing_kBps, latency_ms, source_server):
        self.env = env
        self.id = id
        self.capacity_kb = capacity_kb
        self.__container = simpy.Container(env, capacity_kb)
        self.__mutex = simpy.Resource(env, 1)
        # self.bandwidth_reading = reading_kBps
        # self.bandwidth_writing = writing_kBps
        self.latency = latency_ms
        self.time_reading = Function2D.get_bandwidth_model(latency_ms, reading_kBps)
        self.time_writing = Function2D.get_bandwidth_model(latency_ms, writing_kBps)
        # self.stored_files: Dict[str, File] = {}
        self.stored_files = {}
        self.source_server = source_server

        # if a file is transferred to another server, it should reported here
        # in order to ask directly to the correct server
        self.transfer_list = {} # : Dict[str, int]

    def write_file(self, file):
        printmessage(0, "started writing file " + file.get_name(), self.env.now)
        if file.get_size() > self.__container.capacity:
            raise DiskTooSmallError

        req = self.__mutex.request()
        yield req
        if file.get_size() > self.__free_space():
            # move or flush some files
            yield self
            pass
        else:
            yield self.env.timeout(314)

        yield self.env.timeout(self.time_reading(file.get_size()))
        self.stored_files[file.get_name()] = file

        self.__mutex.release(req)
        printmessage(0, "finished writing " + file.get_name(), self.env.now)

    def tracked_file(self, file):
        filename = file.get_name()
        return filename in self.stored_files or filename in self.transfer_list

    def get_owning_disk_id(self, filename):
        """
        check that the file is present in the disk required. Mandatory before accessing the file
        :param filename: the filename required
        :return: returns the disk id where the resource has been moved to. In case of match it returns its id
        """
        if filename in self.stored_files:
            return self.id
        else:
            return self.transfer_list[filename]

    def read_file(self, filename):
        if not self.get_owning_disk_id(filename).equal(self.id):
            raise FileNotFoundError("Before resource access, check that the file is present with is_file_present")

        req = self.__mutex.request()
        yield req
        file = self.stored_files[filename]
        yield self.env.timeout(self.time_reading(file.get_size()))
        self.__mutex.release(req)
        printmessage(0, "finished reading " + file.get_name(), self.env.now)

    def move_file_to(self, file, target_disk_id):
        """
        Move a file to a different location. If inside the same server there is not network communication
        If the target server is different from the source, then it waits for network communication and resources
        to be allocated
        :param file: the file to be moved
        :param target_disk_id: the disk where the file has to be moved to
        :return: void
        """
        if target_disk_id.get_server_id() == self.id.get_server_id():
            # intra-server communication
            read_operation = self.env.process(self.read_file(file.get_name()))
            same_server_data_disks = self.source_server.get_data_disks()
            if target_disk_id not in same_server_data_disks:
                raise DiskIdInconsistency("Disk with same server ID are not in the same server")
            target_disk = same_server_data_disks[target_disk_id]
            write_operation = self.env.process(target_disk.write_file(file))
            read_operation = self.env.process(self.read_file(file.get_name()))
            yield read_operation & write_operation
            self.transfer_list[file.get_name()] = target_disk_id
            print("finished both read and write. Move completed")
        else:
            pass
            print("Requested a network movement")
            # network communication

    def __free_space(self):
        return self.__container.capacity - self.__container.level

    def get_capacity(self):
        return self.capacity_kb

    def get_latency(self):
        return self.latency

    def get_id(self):
        return self.id


if __name__ == "__main__":
    # gen = DiskIdNotation.get_disk_id_generator(0, True)
    # for i in range(10):
    #     print(next(gen).to_string())
    #
    # diskid = DiskIdNotation.build_from_string("5:12:m")
    # print(diskid.to_string())
    disk_id1 = DiskIdNotation.build_from_string("1:12:d")
    disk_id2 = DiskIdNotation.build_from_string("1:12:d")
    print(disk_id1.equal(disk_id2))
