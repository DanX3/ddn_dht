# Simpy Model

This model should give directions to solve the transactional traffic that the servers must maintain.
Using python OOP every object inside the system that need to keep a status should be declared.
Right now the objects represented are:

*	**Client**
*	**Server**
*	**HUB**
*	**Hard Drives** (the differences between an HDD and a SSD are just in their configuration parameters)

There are also some more classes used for utilities purposes:

* **FunctionDesigner**: in order to reuse a predefined function, I created a collection of them in order to call them later in the code, reusing correct code 
* **ServerManager**: this component handles the connection between clients and servers. The client has this object, sending to it the request to the server. This object simulate an async behaviour, not blocking the client and making every request waiting on his own. The server can later answer back through the request itself: there is a reference to the sending client in the request
* **Logger**: designed to collect data about the work and idle time. Every time step should be registered through this object
* **Simulator**: the "main" source file. It parses the configuration file and creates the environment.
* **Parser**: argument parser using the python module argparse
* **Contract**: design pattern component that make an association between a variable name and its name in the configuration file. If later you want to change a name in the configuration file, you don't have to check all your code base to fix the edi

### Conventions
*	Bandwidth measure are in kBps (kiloBytes per sec). These are always specified anyway in the variable name to avoid mistakes
*	File sizes are in kB by default
*	Time steps are in us and are integer. Every double data type should be removed as considered an error

### Request File
Configurator to make requests
Every line is in the format. The target client is implicit in the line number
```
	[*] <number_of_files: int> <size_of_files: int>
```


#### Example
```
	1 100
	100 1
```

1 request  of a file of 100 KB from client 0
100 requests of a file of 1 KB from client 1

If is needed to add a request from all the client write a * in front of the requests. This will be **forwarded to all the clients**. This line is not counted in the implicit line number.
Also, the order matters: if a global request is sent before the others, the program will ship the global before. The program pre-parse the file to know ahead how many clients are there.

#### Example
```
	* 1 1000
	0 0
	1 1000
```

1 request  of a file of 1000 KB from every client
0 request  of a file of 0 KB from client 0 (meaning **no request**)
1 request  of a file of 100 KB from client 1

If a request has 0 size or times, it is automatically ignored. The number count is anyway increased, so can be used to skip quiet clients

Even if Client 0 make an empty request is important to be counted as line number and address the 100 KB request to the second client

