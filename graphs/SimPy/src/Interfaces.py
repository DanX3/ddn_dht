from Utils import WriteRequest, ReadRequest
from abc import abstractmethod


class GeneralManagerIf:
    @abstractmethod
    def perform_network_transaction(self, size: int): raise NotImplementedError


class IfForServer(GeneralManagerIf):
    @abstractmethod
    def answer_client(self, request: WriteRequest): raise NotImplementedError


class IfForClient(GeneralManagerIf):
    @abstractmethod
    def write_to_server(self, request: WriteRequest): raise NotImplementedError

    @abstractmethod
    def read_from_server(self, request: ReadRequest, target_id: int): raise NotImplementedError

    @abstractmethod
    def read_completed(self): raise NotImplementedError

    @abstractmethod
    def write_completed(self): raise NotImplementedError

    @abstractmethod
    def get_server_count(self) -> int: raise NotImplementedError
