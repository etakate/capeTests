#!/usr/bin/env python

from gsmTest import *
from gpsTest import *
from cellTest import *
from bwTest import *


def fullTest1(iteration, deviceID, fwVer):
    print "\nStarting GSM test...."
    gsmTest(iteration, deviceID, fwVer)
    print "\nStarting GPS test...."
    gpsTest(iteration, deviceID)

def fullTest2(iteration, deviceID, fwVer):
    print "\nStarting GSM test...."
    gsmTest(iteration, deviceID, fwVer)
    print "\nStarting GPS test...."
    gpsTest(iteration, deviceID)
    print "\nStarting cell network test...."
    cellTest(deviceID)
    print "\nStarting bandwidth test...."
    bwTest(deviceID)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--iteration', '-it', choices=['1', '2'], help='Specify which iteration of the test you will be running (enter 1 or 2).')
    parser.add_argument('--id', help='Specify the cape ID, which should be the GSM IMEI.')
    parser.add_argument('--firmware', '-fw',  help='Specify the firmware version (enter 4.1 or 4.4.')
    args = parser.parse_args()

    if args.id is None:
        print("Missing arguments; cannot proceed.")
    else:
        iteration = args.iteration
        deviceID = args.id
        fwVer = args.firmware
        if args.iteration == "1":
            print("Beginning full test battery, round 1...")
            fullTest1(iteration, deviceID, fwVer)
        else:
            print("Beginning full test battery, round 2...")
            fullTest2(iteration, deviceID, fwVer)


