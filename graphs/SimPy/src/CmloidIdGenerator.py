class CmloidIdGenerator:
    """
    CML_oid Id has validity only inside a server. So only server class should use this class
    """

    def __init__(self):
        self.__current_id = 0

    def __next__(self):
        self.__current_id += 1
        return self.__current_id

