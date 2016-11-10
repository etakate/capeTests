#!/usr/bin/env python

import os
import select
import serial
import subprocess
import sys
import time

# Open serial connection to GSM module
com = serial.Serial('/dev/ttyO4', 921600)
fd = com.fileno()

# Send to GSM module
def send(data):
    com.write(data + '\r')
    resp = []
    while select.select([fd], [], [], 1.0)[0]:
        resp.append(os.read(fd, 512))
    resp = ''.join(resp).split('\r\n')
    return [r for r in resp if r]

# Activate GPIO22
def activateGPIO22(cmd):
    open('/sys/class/gpio/gpio22/value', 'wb').write('1')
    time.sleep(50)
    gpio = subprocess.check_output(cmd, shell=True)
    return gpio

def gsmSettingsInit():
    # Check GPIO22 is active
    print 'Verifying gpio22 set...'
    cmd = 'cat /sys/class/gpio/gpio22/value'

    try:        
        gpio22 = subprocess.check_output(cmd, shell=True)
        j = 0;
        if '1' not in gpio22:
            while '1' not in gpio22 and j < 10:
                gpio = activateGPIO22(cmd)
                gpio22 = gpio
                j += 1
            if '1' not in gpio:
                # Reset stdout
                sys.stdout = stdouttemp
                print 'TEST FAILED - Could not continue script; something is wrong with GPIO22.'
                sys.exit()         
            else:
                print "GPIO22 was turned off; turned on GPIO22."
        else:
            print 'GPIO22 - OK'
    except Exception as e:
        print "TEST FAILED - Could not continue script; something is wrong with GPIO22: \n" + str(e)
        # Reset stdout
        sys.stdout = stdouttemp
        print "TEST FAILED - Could not continue script; something is wrong with GPIO22: \n" + str(e)
        sys.exit()        

    # Check baud rate
    print "Verifying 'at+ipr' set..."
    if '921600' not in send('at+ipr?')[1]:
        try:
            send('at+ipr=921600')
            print "IPR was not set correctly; it's fixed now. Current value = 921600 \n"
        except Exception as e:
            print "TEST FAILED - Attempted to set IPR - something happened: \n" + str(e)
            # Reset stdout
            sys.stdout = stdouttemp
            print "TEST FAILED - Attempted to set IPR - something happened: \n" + str(e)
            sys.exit()

    elif '921600' in send('at+ipr?')[1]:
        print 'IPR - OK'
    else:
        # FAIL LOUDLY
        print send('at+ipr?')[1]
        print 'TEST FAILED - make sure upgrade-serial.py completed successfully.'
        # Reset stdout
        sys.stdout = stdouttemp
        print 'TEST FAILED - make sure upgrade-serial.py completed successfully.'
        sys.exit()

    # Check CTS/RTS handshaking (prevents lost characters)
    print "Verifying 'at&k3' set..."
    if '&K3' not in send('at&v?')[2]:
        try:
            send('at&k3')
            print "CTS/RTS handshaking was not set correctly; it's fixed now. \nCurrent value = &K3 \n"
        except Exception as e:
            print "TEST FAILED - Attempted to set CTS/RTS handshaking ('at&k3') - something happened: \n" + str(e)
            # Reset stdout
            sys.stdout = stdouttemp
            print "TEST FAILED - Attempted to set CTS/RTS handshaking ('at&k3') - something happened: \n" + str(e)
            sys.exit()

    else:
        print 'CTS/RTS handshaking - OK'

    # Check Stored Profile 1
    #    Compare Active Profile to Stored Profile 1 values
    print "Verifying 'at&y1', 'at&w1' set..."
    if send('at&v')[3] != send('at&v')[11]:
        try:
            send('at&w1')
            print 'Stored Profile 1 settings were incorrect. Current settings saved to Stored Profile 1.'
        except Exception as e:
            # Reset stdout
            sys.stdout = stdouttemp
            print 'Attempted to set Stored Profile 1 - something happened: \n' + str(e)
            sys.exit()
    else:
        print 'Stored Profile 1 - OK'

    if send('at&v')[3] == send('at&v')[11]:
        with open('tmp_gsm.txt', 'w') as f:
            gsm_pass1 = 'Profile Saved'
            f.write('{0}\n'.format(gsm_pass1))
            f.close()
    else:
        print "GSM profile settings were not saved; it's probably a good idea to investigate."

def gsmSettingsVerify():
    # Check stored settings persisted post-reboot
    print "Verifying settings..."

    try:
        # at+ipr = Baudrate of DCE
        if '921600' in send('at+ipr?')[1] and send('at&v')[3] == send('at&v')[11]:
            gsm_pass2 = 'Profile Saved'        
        else:
            gsm_pass2 = 'Profile NOT Saved'

        pass1 = [line.rstrip('\n') for line in open('tmp_gsm.txt')]
        gsm_pass1 = pass1[0]

        if gsm_pass2 == gsm_pass1:
            print "GSM verification checks PASSED -- settings are persistent."
        else:
            print "GSM verification checks FAILED -- settings did not persist."

    except Exception as e:
        print "Issues occurred trying to communicate with the GSM; please verify sigma-controller/pppd are down before continuing: \n" + str(e)

def gsmData():
    try:
        # at+cgsn = IMEI of GSM module
        print 'IMEI: ' + send('at+cgsn')[1]
        # ati = Model of GSM module
        print 'Model: ' + send('ati')[1]
        # at+cnum  = Phone number of current SIM card
        print 'Phone number: ' + send('at+cnum')[1]
        # at+csq = Cell signal quality of GSM module
        print send('at+csq')[1]
        # at+ccid = CCID of GSM module
        print send('at+ccid?')[1]
        # at+v = Current configuration settings
        print 'Current configuration settings: \n' 
        print send('at&v')
   
    except Exception as e:
        # Reset stdout
        sys.stdout = stdouttemp        
        print "Issues occurred trying to communicate with the GSM; please verify sigma-controller/pppd are down before continuing: \n" + str(e)
