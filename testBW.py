#!/usr/bin/env python

import datetime
import os
import sys
from timeit import default_timer as timer
import time
import urllib
import urllib2

save_path = '/home/sigma/controller/bin/logfiles/'
download_path = '/home/sigma/controller/bin/download/'
name_of_file = raw_input("Enter cape ID [Format: CAxxx] : ")

hash = '\043'
urls = ['http://nexus.dtect.net/service/local/artifact/maven/content?r=snapshots&g=sigma&a=messages&v=0.9.5-SNAPSHOT&c=py&e=zip%ssigma' % hash,
	'http://nexus.dtect.net/service/local/artifact/maven/content?r=snapshots&g=sigma&a=sensor&v=LATEST&c=py&e=zip%ssigma' % hash,
	'http://nexus.dtect.net/service/local/artifact/maven/content?r=snapshots&g=sigma&a=data&v=LATEST&c=py&e=zip%ssigma' % hash,
	'http://nexus.dtect.net/service/local/artifact/maven/content?r=snapshots&g=sigma&a=device&v=LATEST&c=py&e=zip%ssigma' % hash]



capeBWLogFile = os.path.join(save_path, name_of_file+'_test_results.txt')         
with open(capeBWLogFile, 'a') as results:

    sys.stdout = results
    start = timer()
    
    print "********************** BEGIN BANDWIDTH DATA COLLECT FOR " + name_of_file + " **********************"
    print "********************** " + datetime.datetime.now().isoformat() + " ***************************\n"
    i = 0;
    for url in urls:
        try:
            i += 1
            urllib.urlretrieve(url, os.path.join(download_path, 'url%d.zip' % i))
            print 'Downloaded url%d.zip' % i
	except Exception as e:
            print str(e)

    stop = timer()

    print 'Download of 1.1M completed in ' + str(stop - start) + ' seconds'
    print "\n********************** END BANDWIDTH DATA COLLECT  **********************"
