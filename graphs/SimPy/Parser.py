import argparse

def createparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default='config')
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser
