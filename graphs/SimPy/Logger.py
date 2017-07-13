class Logger:
    def __init__(self, ID):
        self.ID = ID
        self.idleTime = 0
        self.workTime = 0
        self.totalTime = 0

    def addIdleTime(self, time):
        self.idleTime += time

    def addWorkTime(self, time):
        self.workTime += time

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

