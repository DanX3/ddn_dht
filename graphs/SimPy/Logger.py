class Logger:
    def __init__(self, ID, env):
        self.ID = ID
        self.idle_time = 0
        self.work_time = 0
        self.env = env

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
        total_time = float(self.idle_time + self.work_time)
        log = open(filename, 'a')
        if total_time > 0:
            # log.write("Idle {:.2f} - {:4.2f} %\n".format(self.idle_time, 100.0 * 
                    # self.idle_time / total_time))
            # log.write("Work {:.2f} - {:4.2f} %".format(self.work_time, 100.0 * 
                    # self.work_time / total_time))
            log.write("{} {} {} {:5.4f} {:5.4f}\n".format(
                self.ID, self.idle_time, self.work_time,
                float(self.idle_time)/total_time,  
                float(self.work_time)/total_time,  
                ))
        else:
            log.write("No data added so far for {}\n".format(self.ID))
        log.close()
