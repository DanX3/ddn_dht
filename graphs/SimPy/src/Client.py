import simpy
from Logger import Logger
from Server import Server
from Utils import *
from FunctionDesigner import Function2D
from Contract import Contract
from collections import deque
from ServerManager import  ServerManager
from simpy.util import start_delayed
from ParityGroupCreator import ParityGroupCreator, ParityId


class Client:
    def __init__(self, env: simpy.Environment, id: int, logger: Logger,
                 servers_manager: ServerManager, config, misc_params,
                 pgc: ParityGroupCreator):
        self.env = env
        self.id = id
        self.__servers_manager = servers_manager
        self.config = config
        self.misc_params = misc_params
        self.logger = logger

        token_amount = config[Contract.C_TOKEN_COUNT]
        self.tokens = simpy.Container(env, capacity=token_amount, init=token_amount)
        self.env.process(self.refresh_tokens())
        self.__token_refresh_delay = config[Contract.C_TOKEN_REFRESH_INTERVAL_ms] * int(1e6)
        self.__geometry = (config[Contract.C_GEOMETRY_BASE], config[Contract.C_GEOMETRY_PLUS])
        self.__parity_id_creator = ParityId()
        self.__network_buffer_size = int(misc_params[Contract.M_NETWORK_BUFFER_SIZE_KB])
        self.__send_treshold = self.__geometry[0] * self.__network_buffer_size
        self.__request_queue = {}  # Dict[int, deque]
        self.__single_request_queue = deque()
        self.__single_request_queue_size = 0
        # TODO: find a balanced value to the length of the parity targets list
        self.__parity_groups = pgc.get_targets_list(int(servers_manager.get_server_count() * 2))
        self.__parity_index = 0
        self.__file_map = {}  # Dict[str, int]
        self.__files_created = []  # List[File]

        for i in range(servers_manager.get_server_count()):
            self.__request_queue[i] = deque()

        seed(0)
        self.filename_gen = File.get_filename_generator(self.id)
        self.send_treshold = int(1024 / WriteRequest.get_cmloid_size())
        self.__data_sent = 0
        self.data_received = 0

    def refresh_tokens(self):
        tokens_missing = self.tokens.capacity - self.tokens.level
        if tokens_missing != 0:
            self.tokens.put(tokens_missing)

        # trigger sending processes
        sent_something = True
        while sent_something:
            sent_something = False
            for queue_index in range(self.__servers_manager.get_server_count()):
                if self.__request_queue[queue_index] and self.tokens.level > 0:
                    sent_something = True
                    self.env.process(self.__send_request(self.__request_queue[queue_index].popleft()))

        yield self.env.timeout(self.__token_refresh_delay)
        if self.data_received < self.__data_sent:
            self.env.process(self.refresh_tokens())

    def receive_answer(self, request: WriteRequest):
        for part in request.get_parts():
            if part.get_filename() != 'parity':
                self.data_received += part.get_size()
        if self.data_received >= self.__data_sent:
            printmessage(self.id, "Finished all the transactions ({}/{})"
                         .format(self.data_received,self.__data_sent), self.env.now)
            self.__servers_manager.client_confirmed_write_completed()

    def __send_request(self, request: WriteRequest):
        start = self.env.now
        yield self.tokens.get(1)
        self.logger.add_task_time("token_wait", self.env.now - start)

        start = self.env.now
        yield self.env.process(self.__servers_manager.request_server(request))
        self.logger.add_task_time("send_request", self.env.now - start)

    def add_write_request(self, req_size_kb, file_count=1) -> List[str]:
        """
        Add a write request to the client.
        :param req_size_kb: int saying the size of the request to be done
        :return: the filename so generated. It chooses on his own the filename to avoid name collisions
        """
        filenames = []
        # add all the files to the single queue
        for i in range(file_count):
            filename = next(self.filename_gen)
            file = File(filename, int(req_size_kb))
            self.__file_map[filename] = 0
            filenames.append(filename)
            self.__files_created.append(file)
            self.__single_request_queue.append(FilePart(file, 0, file.get_size()))
        self.__data_sent += req_size_kb * file_count
        self.__single_request_queue_size += req_size_kb * file_count
        self.__scatter_files_in_queues()
        print(self.__file_map)
        return filenames

    def __scatter_files_in_queues(self):
        """
        Divides the files in the queue in network buffers and append the in the correct queue
        """
        # print(self.__single_request_queue_size)
        while self.__single_request_queue_size >= self.__send_treshold:
            self.__single_request_queue_size -= self.__send_treshold
            # TODO write a class in which remember the targets and the current index
            parity_group = self.__parity_groups[self.__parity_index]
            targets = ParityGroupCreator.int_to_positions(parity_group)
            parity_id = self.__parity_id_creator.get_id()

            # The first target of the group stores parity
            parity_request = WriteRequest(self.id, targets[0], parity_group, parity_id)
            parity_request.set_parts([FilePart.get_parity_part(self.__network_buffer_size)])
            self.__request_queue[targets[0]].append(parity_request)
            # print(parity_request)

            for target_id in targets[1:]:
                request = WriteRequest(self.id, target_id, parity_group, parity_id)
                request.set_parts(self.__pop_netbuffer_from_queue(target_id))
                self.__request_queue[target_id].append(request)
                # print(request)
            self.__parity_index = (self.__parity_index + 1) % len(self.__parity_groups)
            del targets

    def __pop_netbuffer_from_queue(self, target_id: int) -> List[FilePart]:
        """
        Pop a stream of <netbuffer size> from the queue if possible.
        It truncates the file parts to match the <netbuffer size>
        It returns a smaller amount of data if there is no data,
        popping the empty file part from the queue
        :return: the List of fileparts of total size <netbuffer size>
        """
        result = []
        free_space = self.__network_buffer_size
        while free_space > 0 and len(self.__single_request_queue) > 0:
            self.__file_map[self.__single_request_queue[0].get_filename()] |= target_id
            # if file fits in buffer
            if self.__single_request_queue[0].get_size() <= free_space:
                free_space -= self.__single_request_queue[0].get_size()
                result.append(self.__single_request_queue.popleft())
            else:
                result.append(self.__single_request_queue[0].pop_part(free_space))
                free_space = 0
        return result

    def get_id(self):
        return self.id

    def flush(self):
        # terminate if there is nothing to send
        if self.__single_request_queue_size == 0:
            return

        # if I need to flush, is because something is left behind because was lower than
        # the send treshold
        assert self.__single_request_queue_size < self.__send_treshold

        parity_group = self.__parity_groups[self.__parity_index]
        targets = ParityGroupCreator.int_to_positions(parity_group)

        # Creating the requests. Before filling the next target request, I want to complete the current
        #     * I don't have division problems, in case I have to write 2KB to 3 targets
        #     * The size of the first request is always the greater or equal
        #     * Based on the first request I create the parity request
        #     * Since I could not send data to every target, the parity group could be different
        new_parity_group = 0
        parity_id = self.__parity_id_creator.get_id()
        requests = []
        for target_id in targets[1:]:
            request = WriteRequest(self.id, target_id, 0, parity_id)
            request.set_parts(self.__pop_netbuffer_from_queue(target_id))
            self.__single_request_queue_size -= request.get_size()
            requests.append(request)
            new_parity_group |= 1 << target_id
            if self.__single_request_queue_size == 0:
                break

        # creating the parity request
        parity_request = WriteRequest(self.id, targets[0], 0, parity_id)
        parity_request.set_parts([FilePart.get_parity_part(requests[0].get_size())])
        new_parity_group |= targets[0]
        parity_request.set_parity_group(new_parity_group)
        self.__request_queue[targets[0]].append(parity_request)
        # print(parity_request)

        # appending the created requests with adjusted parity group
        for request in requests:
            request.set_parity_group(new_parity_group)
            # print(request)
            self.__request_queue[request.get_target_id()].append(request)
        self.__parity_index = (self.__parity_index + 1) % len(self.__parity_groups)

    def __print_files_created(self):
        for file in self.__files_created:
            print(file)

    def read_all_files(self):
        printmessage(0, "Asked to read every file", self.env.now)
        for filename, targets in self.__file_map.items():
            request = ReadRequest(filename, 0, self.__files_created[filename].get_size())
            for target in ParityGroupCreator.int_to_positions(targets):
                self.env.process(self.__servers_manager.read_from_server(request, target))
