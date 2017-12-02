data = open('results.dat.reduced', 'r')
for line in data:
    words = line.split(' ')
    print(int(words[4]) / int(words[1]))
    print(int(words[5]) / int(words[2]))
    print(int(words[6]) / int(words[3]))
data.close()
