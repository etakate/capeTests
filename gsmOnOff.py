#!/usr/bin/env python

import time
import os

proc1 = 'sigma-controller.py' 
proc2 = 'sigma-messenger.py'
proc3 = 'pppd'

def gsmShutdown():
    # Shut down sigma-controller.py
    print 'Shutting down sigma-controller...'
    try:
        os.system(proc1 + ' stop')
        time.sleep(5)
        tmp = os.popen('ps -Af').read() 
        if proc1 not in tmp[:]: 
            print 'OK'
        else:
            print 'sigma-controller.py still up'
    except Exception as e:
        print 'Issues occurred shutting down sigma-controller: \n' + str(e) 

    # Shut down sigma-messenger.py
    print 'Shutting down sigma-messenger...'
    try:
        os.system(proc2 + ' stop')
        time.sleep(4)
        tmp = os.popen('ps -Af').read() 
        if proc2 not in tmp[:]: 
            print 'OK'
        else:
            print 'sigma-messenger.py still up'
    except Exception as e:
        print 'Issues occurred shutting down sigma-messenger: \n' + str(e) 

    # Shut down pppd
    print 'Shutting off pppd...'
    try:
        os.system("poff att")
        time.sleep(3)
        tmp = os.popen("ps -Af").read() 
        if proc3 not in tmp[:]: 
            print 'OK'
        else:
            print 'pppd still up'
    except Exception as e:
        print 'Issues occurred shutting down pppd: \n' + str(e)


def gsmStartup():
    # Restart sigma-controller.py
    print 'Turning on sigma-controller...'
    try:
        os.system(proc1 + ' --provider att start')
        tmp = os.popen('ps -Af').read() 
        if proc1 not in tmp[:]: 
            newprocess = "nohup python %s &" % (proc1)
            os.system(proc1 + ' start')  
            time.sleep(3)
        else:
            print 'sigma-controller.py is back up'
    except Exception as e:
        print 'Issues occurred during sigma-controller startup: \n' + str(e) 

    # Restart sigma-messenger.py
    print 'Turning on sigma-messenger...'
    try:
        os.system(proc2 + ' start')
        tmp = os.popen('ps -Af').read() 
        if proc2 not in tmp[:]: 
            newprocess = "nohup python %s &" % (proc2)
            os.system(proc2 + ' start')
        else:
            print 'sigma-messenger.py is back up'
    except Exception as e:
        print 'Issues occurred during sigma-messenger startup: \n' + str(e) 

    # Restart pppd
    print 'Turning on pppd...'
    try:
        os.system('pon att')
        tmp = os.popen('ps -Af').read() 
        if proc3 not in tmp[:]: 
            while True:
                newprocess = "nohup python %s &" % (proc3)
                os.system(proc3 + '-dns start')
        else:
            print 'pppd is back up'
    except Exception as e:
        print 'Issues occurred during pppd startup: \n' + str(e) 