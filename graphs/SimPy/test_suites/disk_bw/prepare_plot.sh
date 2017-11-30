#!/bin/bash

cat ?/manager.log | grep write | cut -d ' ' -f 1 > /tmp/dataset_1
cat ?/manager.log | grep read | cut -d ' ' -f 1 > /tmp/dataset_2
paste dataset /tmp/dataset_1 /tmp/dataset_2 > results/results.dat
cd results/
gnuplot plot.plt
firefox plot.png
