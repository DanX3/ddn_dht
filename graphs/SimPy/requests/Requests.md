### Requests

These are the requests the system are tested against.
Every Entry will have its own space in the final diagram: is fine having many tests
but will produce a lot of noise quickly: choose which tests are the most important.
The parameters are:

* Number of clients
* Number of requests per clients
* Requests size

Can be followed this naming convention to better classify the requests:

**clients-count** \_ **requests-per-client** \_ **request-size**

So for example:

* 1_2_3 has *1* client asking for *2* files of size *3* bytes 
* 20_1_500 has *20* clients with *1* request of size *500*

So far are available:

* Many Clients, few requests, average size
* Single Client, many requests, small size
* Single client, single request, big size
