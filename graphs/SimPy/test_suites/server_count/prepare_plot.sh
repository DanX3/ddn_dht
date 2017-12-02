#!/bin/bash

cat ?/manager.log | grep write | cut -d ' ' -f 1 > /tmp/dataset_1
cat ?/manager.log | grep read | cut -d ' ' -f 1 > /tmp/dataset_2
cat ?/manager.log | grep restore | cut -d ' ' -f 1 > /tmp/dataset_3
paste dataset /tmp/dataset_1 /tmp/dataset_2 /tmp/dataset_3 > results/results.dat
#cd results/
#gnuplot plot.plt
#cat results.dat
#firefox plot.png
