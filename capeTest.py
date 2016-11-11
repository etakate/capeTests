#!/usr/bin/env python

from gsmTest import *
from gpsTest import *
from cellTest import *
from bwTest import *


def fullTest1(iteration, deviceID):
    gsmTest(iteration, deviceID)
    gpsTest(iteration, deviceID)

def fullTest2(iteration, deviceID):
    gsmTest(iteration, deviceID)
    gpsTest(iteration, deviceID)
    cellTest(deviceID)
    bwTest(deviceID)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--iteration', '-it', choices=['1', '2'], help='Specify which iteration of the test you will be running (enter 1 or 2).')
    parser.add_argument('--id', help='Specify the cape ID, which should be the GSM IMEI.')
    args = parser.parse_args()

    if args.id is None:
        print("Missing arguments; cannot proceed.")
    else:
        iteration = args.iteration
        deviceID = args.id
        if args.iteration == "1":
            print("Beginning full test battery, round 1...")
            fullTest1(iteration, deviceID)
        else:
            print("Beginning full test battery, round 2...")
            fullTest2(iteration, deviceID)


