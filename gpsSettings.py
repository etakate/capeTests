#!/usr/bin/env python

import datetime
import ntplib
import os
import re
import serial
import six
import time

# Set GPS baudrate if needed
# Generally this is bad practice & unnecessary; gpsd knows what it's doing
def gpsBaud():
    try:
        os.system('stty speed 115200 < /dev/ttyO5')
        time.sleep(1)
    except Exception as e:
        print 'Issue occurred setting the baudrate: \n' + str(e)

# Reset GPS chip via binary command(s)
def gpsReset(bbr):
    try:
        gps_com = serial.Serial('/dev/ttyO5', 115200)
        print 'Resetting GPS....'

        # bbr = 0xffff
        if bbr == 'cold':
            print 'Sending cold restart...'
            gps_com.write('\xb5\x62\x06\x04\x04\x00\xff\xff\x00\x00\x0c\x5d')

        # bbr = 0x0000
        elif bbr == 'hot':
            print 'Sending hot restart...'
            gps_com.write('\xb5\x62\x06\x04\x04\x00\x00\x00\x00\x00\x0e\x64')

        # bbr = 0x0001
        elif bbr == 'warm':
            print 'Sending warm restart...'
            gps_com.write('\xb5\x62\x06\x04\x04\x00\x00\x01\x00\x00\x0f\x67')

        time.sleep(10)
        print 'OK - GPS reset'

        gps_com.close()

    except Exception as e:
        print "Error resetting GPS chip: " + str(e)

# Modify incoming GPS strings
def gpsSettings():
    # Talker IDs
    talkers = ['$GL', '$GB', '$GA']
    # Header IDs
    headerids = ['GGA', 'RMC', 'TXT', 'GBQ', 'GLQ', 'GPQ', 'GNQ']
    try:
        os.system('timeout 30 cat /dev/ttyS5 | tee tmp_gps.txt')
        GPSset = True

        with open('tmp_gps.txt', 'r') as gps_strings:
            for line in [ line for line in gps_strings if line != '']:

                if line[0:3] in talkers:
                    GPSset = False
                    break
                    pass
                elif line[3:6] not in headerids:
                    GPSset = False
                    break
                else:
                    pass

            if GPSset == False:
                print 'GPS satellite filtering was not saved. Check configuration.'
            else:
                print 'GPS satellite filtering saved successfully. Configuration OK.'

    except Exception as e:
        print 'Something is wrong with the serial connection to the GPS module. \n' + str(e)

# Generate GPS report data
def gpsData(start, report):
    # Print report
    stop = time.time()
    print 'Latitude: ' , report['lat']
    print 'Longitude: ' , report['lon']
    print 'Time UTC: ' , report['time']
    if 'alt' not in report.keys():
        print 'Altitude (m): [not reported]'
    else:
        print 'Altitude (m): ' , report['alt']
    if 'speed' not in report.keys():
        print 'Speed (m/s): [not reported]'
    else:
        print 'Speed (m/s): ' , report['speed']
    if 'track' not in report.keys():
        print 'Track: [not reported]'
    else:
        print 'Track: ' , report['track']
    if 'mode' not in report.keys():
        print 'Mode: [not reported]'
    else:
        print 'Mode: ' , report['mode']
    if 'ept' not in report.keys():
        print 'EPT: [not reported]'
    else:
        print 'EPT: ' , report['ept']

    elapsed = stop - start
    print "Time to Positioning Lock: ", elapsed , " seconds"
    print "PASS - GPS lock successfully established"

    # Additional GPS fields available:
    # print 'EPS: ' , report['eps']
    # print 'EPV: ' , report['epv']
    # print 'EPX: ' , report['epx']
    # print 'Climb: ' , report['climb']
    # FFR - 'epx' and 'track' are normally stored in report.keys()[0]

# Calculate GPS/NTP difference
def calc_delta(td):
    try:
        tdh = td.seconds//3600
        tdm = (td.seconds//60)%60
        tds = float(str(td.seconds) + '.' + str(td.microseconds))
        if tdh != 0 or tdm != 0:
            tdelta = str(tdh) + ':' + str(tdm) + ':' + str(tds)
        else:
            tdelta = tds
    except Exception as e:
        print str(e)
    return tdelta

# Check GPS time against NTP
def gpsTime(report, iteration):
    try:
        os.system('ntpdate -u time.nist.gov')
        gps = report['time']
        cmd = datetime.datetime.now()
        gt = re.split("T|Z", str(gps))
        gpstime = '%s%s' % (gt[1], '000')
        ntptime = re.split("\s", str(cmd))
        print '\nChecking GPS time....'
        print 'GPS: ' + gpstime
        print 'NTP: ' + ntptime[1]

        g = datetime.datetime.strptime(gpstime, '%H:%M:%S.%f')
        n = datetime.datetime.strptime(ntptime[1], '%H:%M:%S.%f')

        # td = timedelta object
        td = n - g
        tdelta = calc_delta(td)

        if isinstance(tdelta, six.string_types):
            print 'GPS time differs from NTP time by minutes or hours [' + tdelta + ']. Difference is not acceptable, something needs help.'
        else:
            print 'GPS time differs from NTP time by ' + str(tdelta) + ' seconds.'

        if str(iteration) == '1':
            gpsTimeInit(tdelta)
        else:
            gpsTimeVerify(tdelta)

    except Exception as e:
        print 'Something happened during the GPS time check: ' + str(e)

# Write GPS time results (test iteration 1) for later comparison
def gpsTimeInit(tdelta):
    try:
        with open('tmp_gpst.txt', 'w') as f:
            f.write('{0}\n'.format(tdelta))
            f.close()

    except Exception as e:
        print 'Issues occurred writing iteration 1 time data to temp file: ' + str(e)

# Compare GPS time test iteration 1 to iteration 2
def gpsTimeVerify(tdelta):
        t1 = [line.rstrip('\n') for line in open('tmp_gpst.txt')]
        td_t1 = t1[0]
        td_diff = float(tdelta) - float(td_t1)
        print '\nGPS time offset difference between iteration 1 and iteration 2: ' + str(td_diff)
        if -3.0 > td_diff or td_diff > 3.0:
            print td_diff
            print "GPS time offset differs significantly from iteration 1."
        else:
            print 'GPS time offset OK.'







