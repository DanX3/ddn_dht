#!/bin/bash

mkdir -p logs svgs
cd src/

for request in ../requests/* ; do
    echo "`which pypy3` Simulator.py --request $request"
    pypy3 Simulator.py --request $request
    if [ $? -eq 0 ] ; then
        for log in *.log ; do
            mv $log $request-$log
            mv ../requests/*.log .
            #echo "renamed $log in $request-$log"
        done
        mv *.log ../logs/
    fi
done

cd ../
gnuplot plot.plt
mv *.svg svgs/
