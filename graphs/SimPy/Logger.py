class Logger:
    def __init__(self, ID, env):
        self.ID = ID
        self.idleTime = 0
        self.workTime = 0
        self.totalTime = 0
        self.env = env

    def addIdleTime(self, time):
        self.idleTime += time

    def addWorkTime(self, time):
        self.workTime += time

    def work(self, duration):
        start = self.env.now
        yield self.env.timeout(duration)
        self.addWorkTime(self.env.now - start)

    def wait(self, duration):
        start = self.env.now
        yield self.env.timeout(duration)
        self.addIdleTime(self.env.now - start)

    def printInfo(self):
        self.totalTime = self.idleTime + self.workTime
        if self.totalTime > 0:
            print "Information for ", self.ID
            print
            print "Idle Time: %6d (%4.2f%%)" % (self.idleTime, 100.0 *
                    self.idleTime / self.totalTime)
            print "Work Time: %6d (%4.2f%%)" % (self.workTime, 100.0 *
                    self.workTime / self.totalTime)
        else:
            print "No data added so far"

