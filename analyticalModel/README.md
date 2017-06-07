# Simulator for network operations
In this project I'm going to simulate the network operations between nodes.
The network layout is configured using the `networkLayout.json` file.
A sample is already prepared, but can be extended without touching the code.


### JSON Configuration
The JSON file wants to represent a graph, paying attention on the links
between the nodes. The network layout is based on 2 sets, **nodes** and
**links**:
```
    {
        "nodes":[
            {
                "id":0,
                type:"CLIENT"
            },

            ...

            {
                "id":1,
                type:"HOME"
            },
        ],
```
    
Here I specified a **client** node, where data is sent from, and a **home**
node, where data is sent to. Even **secondary** type of nodes can exists. The
key part is that must exists at least a client and a home node.

```
        "links":[
            {
                "edges":[0,1],
                "Smax":1.0,
                "bw":10000,
                "latency":1e-1
            },

            ...

            {
                "edges":[1,2],
                "Smax":2.0,
                "bw":20000,
                "latency":1e-2
            },
        ]
    }
```
In the *links* part I specify the connection between the nodes:

  * *edges* are the nodes linked by this connection. As a general rule the lowest index node is always first. The index can be reversed to keep valid this rule
  * *Smax* is the size to reach to start communicating at full bandwidth
  specified in MB
  * *bw* is the max bandwidth in Gb/s
  * *latency* is the minimum time required to cross the link in seconds

The final aim will be to correctly simulate the network communication from the
client node to the home node, being able to try out different network layout
without touching the code. 
After having found the most suitable network layout, I can move on building the
real network based on this one.
