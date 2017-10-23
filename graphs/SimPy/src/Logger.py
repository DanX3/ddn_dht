import simpy
from Utils import get_formatted_time
from collections import OrderedDict


class Logger:
    """
    Class to track wait time of a set of agents.
    Is created a single logger for all the server and another one for all the clients
    Each tracks wait time for every task.
    A task is a string that is registered inside the logger. In the end will be printed a log about
    the time spent on that action, making easier to spot bottlenecks
    """
    def __init__(self, env: simpy.Environment):
        self.__tasks_time = OrderedDict()   # OrderedDict[str:int]
        self.__exactness = {}
        self.env = env

    def add_task_time(self, task: str, time: int, exact: bool):
        if task in self.__tasks_time:
            self.__tasks_time[task] += time
        else:
            self.__tasks_time[task] = time
            self.__exactness[task] = exact

    def print_info_to_file(self, filename):
        # total_time = float(self.idle_time + self.work_time)
        log = open(filename, 'w')
        for key, value in self.__tasks_time.items():
            log.write("{} {} {}\n".format(str(value)[:-3],
                                          1 if self.__exactness[key] else 0,
                                          key))
        log.close()

    def get_fields_count(self):
        return len(self.__tasks_time)
