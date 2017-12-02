#!/bin/bash

for size in 8 256; do
    echo "" > request
    for i in `seq 1 $size`; do
        cat sample_request >> request
    done
    make run
    cp results/results.dat results/results.dat.$size
done

cd results
for size in 8 256; do
    cut -f 1 results.dat > coords
    cut -f 2,3,4 results.dat.$size > $size
done
paste coords 8 256 > results.dat
gnuplot plot.plt
firefox plot.png
