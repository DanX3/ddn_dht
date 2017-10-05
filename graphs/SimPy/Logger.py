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
        self.idle_time = 0
        self.work_time = 0
        self.__tasks = OrderedDict()   # OrderedDict[str:int]
        self.env = env

    def add_task_time(self, task: str, time: int):
        if task in self.__tasks:
            self.__tasks[task] += time
        else:
            self.__tasks[task] = time

    def add_idle_time(self, time):
        self.idle_time += time

    def add_work_time(self, time):
        self.work_time += time

    def work(self, duration):
        start = self.env.now
        yield self.env.timeout(duration)
        self.add_work_time(self.env.now - start)

    def wait(self, duration):
        start = self.env.now
        yield self.env.timeout(duration)
        self.add_idle_time(self.env.now - start)

    def print_info(self):
        total_time = self.idle_time + self.work_time
        if total_time > 0:
            print("Information for ", self.ID)
            print()
            print("Idle time: %6d (%4.2f%%)" % (self.idle_time, 100.0 *
                    self.idle_time / total_time))
            print("Work time: %6d (%4.2f%%)" % (self.work_time, 100.0 *
                    self.work_time / total_time))
        else:
            print("No data added so far")
    
    def print_info_to_file(self, filename):
        # total_time = float(self.idle_time + self.work_time)
        log = open(filename, 'w')
        for key, value in self.__tasks.items():
            log.write("{} {}\n".format(str(value)[:-3], key))
        log.close()
