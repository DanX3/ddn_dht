from Utils import WriteRequest, ReadRequest
from abc import abstractmethod


class GeneralManagerIf:
    @abstractmethod
    def perform_network_transaction(self, size: int): raise NotImplementedError

    @abstractmethod
    def get_server_count(self) -> int: raise NotImplementedError

    @abstractmethod
    def add_sending_entity(self, id): raise NotImplementedError

    @abstractmethod
    def remove_sending_entity(self, id): raise NotImplementedError


class IfForServer(GeneralManagerIf):
    @abstractmethod
    def answer_client_write(self, request: WriteRequest): raise NotImplementedError

    @abstractmethod
    def answer_client_read(self, request: ReadRequest): raise NotImplementedError

    @abstractmethod
    def server_finished_restoring(self): raise NotImplementedError

    @abstractmethod
    def receive_recovery_request(self, target_server_id: int, from_id: int): raise NotImplementedError

    @abstractmethod
    def send_recovery_request(self, crashed_server_id: int, ids: set, targets: int): raise NotImplementedError

    @abstractmethod
    def propagate_metadata(self, packed_metadata, target_id: int): raise NotImplementedError

    @abstractmethod
    def update_recovery_progress(self, target_server_id: int, packets_gathered: int): raise NotImplementedError

class IfForClient(GeneralManagerIf):
    @abstractmethod
    def write_to_server(self, request: WriteRequest) -> int: raise NotImplementedError

    @abstractmethod
    def read_from_server(self, requests, target_id: int): raise NotImplementedError

    @abstractmethod
    def read_from_server_blocking(self, requests, target_id: int): raise NotImplementedError

    @abstractmethod
    def read_completed(self): raise NotImplementedError

    @abstractmethod
    def write_completed(self): raise NotImplementedError

    @abstractmethod
    def get_server_count(self) -> int: raise NotImplementedError
