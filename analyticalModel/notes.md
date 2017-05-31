# First model

For this first first I setup a C++ code that aim to simulate the behaviour of the network behaviour of the network applied in the IME technology.
The following is the time required for a data write over the network to be completed. It involves:

  * Pings
  * Data write to a single server
  * Metadata write to the whole network
  * Checksum to recover data in case of corruption
  
![](/home/optimans/projects/mhpc/DDN/analyticalModel/walltime.png) 
This means that even for small data write, there is a small overhead that can cause network traffic. The causes can  be disk access for logging, ack sent and checksum addded for data recovery.
This data are based on dummy variable, still to be set but the idea holds. The following plot show the efficiency of the network based on the data size

![](/home/optimans/projects/mhpc/DDN/analyticalModel/efficiency.png  "Efficiency")

The efficiency is *packetSize / totalTime* and since in the first steps the total time is affected only by network latency, the efficiency is very low. In the later parts, the total time is affected mainly by packet communication so the network is used at its best. We are still we unable to reach full bandwith because of the checksum bits. 
So the aim to the project is to pack data togheter, not wasting small data communication and instead using at its best the network, without much overhead.