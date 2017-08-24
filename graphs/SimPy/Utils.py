def printmessage(ID, message, time, done=True):
    doneChar = u"\u2713" if done else u"\u279C"
    print(doneChar.rjust(2), (str(time) + "us").rjust(6), ("%d)"%ID).rjust(3), str(message))
