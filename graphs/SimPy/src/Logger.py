import simpy
from Utils import get_formatted_time
from collections import OrderedDict
from typing import List, Dict


class Logger:
    """
    Class to track wait time of a set of agents.
    Is created a single logger for all the server and another one for all the clients
    Each tracks wait time for every task.
    A task is a string that is registered inside the logger. In the end will be printed a log about
    the time spent on that action, making easier to spot bottlenecks
    """
    def __init__(self, env: simpy.Environment):
        self.__tasks_time = OrderedDict()   # OrderedDict[str, int]
        self.__object_counter = {}  # Dict[str, int]
        self.env = env

    def add_task_time(self, task: str, time: int):
        if task in self.__tasks_time:
            self.__tasks_time[task] += time
        else:
            self.__tasks_time[task] = time

    def add_object_count(self, name: str, count: int):
        if name in self.__object_counter:
            self.__object_counter[name] += count
        else:
            self.__object_counter[name] = count

    def print_times_to_file(self, filename, print_to_screen: bool = False):
        log = open(filename, 'w')
        for key, value in self.__tasks_time.items():
            log.write("{} {}\n".format(str(value), key))
            if print_to_screen:
                print("{} {}".format(str(value), key))
        if print_to_screen:
            print()
        log.close()

    def get_objects(self) -> Dict[str, int]:
        return self.__object_counter

    @staticmethod
    def merge_objects_to_dict(dicts: List[Dict[str, int]]) -> Dict[str, int]:
        result = {}
        for current_dict in dicts:
            for key, value in current_dict.items():
                if key in result:
                    result[key] += value
                else:
                    result[key] = value
        return result

    @staticmethod
    def print_objects_to_file(objects: Dict[str, int], filename: str, print_to_screen: bool=False):
        output = open(filename, 'w')
        keys = list(objects.keys())
        keys.sort()
        for key in keys:
            output.write("{} {}\n".format(str(objects[key]), key))
            if print_to_screen:
                print(key, objects[key])
        output.close()

    def get_fields_count(self):
        return len(self.__tasks_time)
