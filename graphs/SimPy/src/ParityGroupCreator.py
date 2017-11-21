import simpy
from Utils import *
from Contract import Contract
from typing import Dict
from random import sample, randint, seed


class ParityGroupCreator:
    """
    Given the parity geometry, returns each time a different parity group
    """
    def __init__(self, client_params: Dict[str, int], server_params: Dict[str, int]):
        self.__geometry_base = client_params[Contract.C_GEOMETRY_BASE]
        self.__geometry_plus = client_params[Contract.C_GEOMETRY_PLUS]
        self.__server_count = server_params[Contract.S_SERVER_COUNT]
        seed(0)
        self.__targets_generator = self.__create_target_generator()

    def __str__(self):
        return "ParityGroupCreator({}+{})".format(self.__geometry_base, self.__geometry_plus)

    def __create_target_generator(self):
        targets = self.get_targets_list(self.__server_count * 2)
        list_length = len(targets)
        i = 0
        while True:
            yield targets[i]
            i = (i + 1) % list_length

    @staticmethod
    def int_to_positions(int_target: int) -> List[int]:
        """
        Reads a single int representing the targets
        :param int_target: the int representation of the targets
        :return: a list of int with the target's ids
        """
        result = []
        counter = 0
        while True:
            current_step = 1 << counter
            if (current_step & int_target) == current_step:
                result.append(counter)
            counter += 1
            if current_step > int_target:
                break

        # shuffled_idx = randint(0, len(result) - 1)
        # result[0], result[shuffled_idx] = result[shuffled_idx], result[0]
        return result

    @staticmethod
    def positions_to_int(targets: List[int]) -> int:
        result = 0
        for target in targets:
            result |= 1 << target
        return result

    @staticmethod
    def get_generator_map_based(file_map: int):
        targets = ParityGroupCreator.int_to_positions(file_map)
        i = 0
        while True:
            yield targets[i]
            i = (i + 1) % len(targets)

    def get_targets(self) -> int:
        """
        Get an integer representing the targets of the packet to send.
        Its binary representation shows the targets of the current parity group
        In a case where server_count = 4
        0011 0110 -> targets are server 5, 4, 2, 1
        :return: the integer representation of the targets
        """
        bits = sample(range(self.__server_count), self.__geometry_base + self.__geometry_plus)
        result = 0
        for bit_shift in bits:
            result |= 1 << bit_shift
        del bits
        return result

    def get_targets_list(self, length: int) -> List[int]:
        """
        Same as get_targets but returns a list of targets.
        :param length:
        :return:
        """
        result = []
        for i in range(length):
            result.append(self.get_targets())
        return result

    def get_target_generator(self):
        """
        Instead of giving every client a fixed target list, generates by itself a big target list
        including possibly every combination. Then every client will access this single big instance
        :return:
        """
        return self.__targets_generator


class ParityId:
    class __ParityId:
        def __init__(self):
            self.__id = 0
            self.__targets = []

        def get_id(self):
            result = self.__id
            self.__id += 1
            return result

    instance = None

    def __init__(self):
        if not ParityId.instance:
            ParityId.instance = ParityId.__ParityId()

    def __getattr__(self, item):
        return getattr(self.instance, item)



if __name__ == "__main__":
    # client_params = {}
    # server_params = {}
    # client_params[Contract.C_GEOMETRY_BASE] = 3
    # client_params[Contract.C_GEOMETRY_PLUS] = 1
    # server_params[Contract.S_SERVER_COUNT] = 20
    # pgc = ParityGroupCreator(client_params, server_params)
    # gen = pgc.get_target_generator()
    g = get_generator_map_based(177)
    for i in range(10):
        print(next(g))

