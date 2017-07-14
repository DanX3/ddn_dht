import simpy
from Logger import Logger

def printmessage(ID, message, time, done=True):
    doneChar = u"\u2713" if done else u"\u279C"
    print doneChar.rjust(2), (str(time) + "us").rjust(6), ("%d)"%ID).rjust(3), str(message)

class Server(object):
    @staticmethod
    def process_request(env, clientID, logger):
        yield env.timeout(2)
        printmessage(clientID, "-", env.now)
    
    @staticmethod
    def make_data_persistent(env, clientID, logger):
        yield env.timeout(2)
        printmessage(clientID, "make_data_persistent", env.now)

    @staticmethod
    def propagate_to_DHT(env, clientID, logger):
        yield env.process(logger.wait(10))
        printmessage(clientID, "propagate_to_DHT", env.now)

    @staticmethod
    def write_meta_to_DHT(env, clientID, logger):
        yield env.process(logger.wait(100))
        printmessage(clientID, "O<--", env.now)
        propagation = env.process(Server.propagate_to_DHT(env, clientID, logger))
        persistency = env.process(Server.make_data_persistent(env, clientID, logger))
        yield propagation | persistency
        yield propagation & persistency
        printmessage(clientID, "-", env.now)


