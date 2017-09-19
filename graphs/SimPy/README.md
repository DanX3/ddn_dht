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
