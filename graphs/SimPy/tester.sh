#!/bin/bash

mkdir -p logs
cd src/

for request in ../requests/* ; do
    echo "pypy3 Simulator.py --request $request"
    python3.5 Simulator.py --request $request
    for log in *.log; do
        mv $log $request-$log
        mv ../requests/*.log .
        echo "renamed $log in $request-$log"
    done
    mv *.log ../logs/
done
