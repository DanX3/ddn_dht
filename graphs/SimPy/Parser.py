import argparse
from os import getpid

def createparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default='config', 
            help='Set another configuration file ')

    parser.add_argument("-v", "--verbose", action="store_true",
            help='prints more informations')

    parser.add_argument("-f", "--function", choices=["gauss", "uniform", "diag"],
            help='aborts normal behaviour and plots the following function.\
            It requires that all the values are set, otherwhise it will use \
            default values')

    parser.add_argument("--mu", default=5.0, type=float, help="set mu value")
    parser.add_argument("--sigma", default=1.0, type=float, help="set sigma value")
    parser.add_argument("--overhead", default=50000.0, type=float, help="set overhead value")
    parser.add_argument("-a", "--angular_coeff", default=1000.0, type=float,
            help="set angular_coeff value")
    parser.add_argument("--value", default=1.0, type=float, help="set uniform value")
    parser.add_argument("--seed", default=getpid(), type=int, help="set seed \
            for random values. Default is PID")
    parser.add_argument("-p", "--params", action="store_true", help="print \
            current settings from config")

    return parser
