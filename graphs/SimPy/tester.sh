#!/bin/bash

mkdir -p logs
cd src/

for request in ../requests/* ; do
    echo $request
    echo "pypy3 Simulator.py --request $request"
    pypy3 Simulator.py --request $request
    for log in *.log; do
        mv $log $request-$log
        mv ../requests/*.log .
        echo "renamed $log in $request-$log"
    done
    mv *.log ../logs/
done
