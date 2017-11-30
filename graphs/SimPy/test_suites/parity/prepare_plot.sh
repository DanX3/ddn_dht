#!/bin/bash
cat ?/client.log | grep parity | cut -d ' ' -f 1 > /tmp/first_dataset
cat ?/manager.log | grep restore | cut -d ' ' -f 1 > /tmp/second_dataset
paste dataset /tmp/first_dataset /tmp/second_dataset > results/results.dat
cd results/
gnuplot plot.plt
firefox plot.png
