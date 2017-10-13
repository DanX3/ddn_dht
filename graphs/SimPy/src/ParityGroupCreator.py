import simpy
from Utils import *
from Contract import Contract
from typing import Dict
from random import sample, randint, seed


"""
ParityGroupCreator is a singleton that, given the parity geometry, returns each time a different parity
group
"""
class ParityGroupCreator:
    class __ParityGroupCreator:
        def __init__(self, geometry_base, geometry_plus, server_count):
            self.__geometry_base = geometry_base
            self.__geometry_plus = geometry_plus
            self.__server_count = server_count
            seed(10)

        def __str__(self):
            return "ParityGroupCreator({}+{})".format(self.__geometry_base, self.__geometry_plus)

        def int_to_positions(self):
            pass

        def get_int(self):
            """
            Get an integer representing the targets of the packet to send.
            Its binary representation shows the targets of the current parity group
            0011 0110 -> targets are server 1, 2, 4, 5
            :return: the integer representation of the target
            """
            bits = sample(range(self.__server_count), self.__geometry_base + self.__geometry_plus)
            result = 0
            for bit_shift in bits:
                result |= 1 << bit_shift
            del bits
            return result

    instance = None

    def __init__(self, client_params: Dict[str, int], server_params: Dict[str, int]):
        if not ParityGroupCreator.instance:
            geometry_base = client_params[Contract.C_GEOMETRY_BASE]
            geometry_plus = client_params[Contract.C_GEOMETRY_PLUS]
            server_count = server_params[Contract.S_SERVER_COUNT]
            ParityGroupCreator.instance = ParityGroupCreator.__ParityGroupCreator(geometry_base, geometry_plus, server_count)

    def __getattr__(self, item):
        return getattr(self.instance, item)


if __name__ == "__main__":
    client_params = {Contract.C_GEOMETRY_BASE: 3, Contract.C_GEOMETRY_PLUS: 1}
    server_params = {Contract.S_SERVER_COUNT: 6}
    creator = ParityGroupCreator(client_params, server_params)
    print(creator.get_int())
