#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__  = "Kadda SAHNINE"
__contact__ = "ksahnine@gmail.com"
__license__ = 'GPL v3'
__version__ = '0.1.0'

import bluetooth
import getopt
import logging
import os
import sys
import time
import yaml
from pushbullet import Listener, PushBullet, Device

sys.path.append( "%s/%s" % (os.getcwd(), 'tpp'))
from libs.velib import Velib

def usage():
    """
    Display usage
    """
    sys.stderr.write( "Usage: app.py [-c <config-file> | --config=<config-file>]\n")

def notify_velib(conf):
    """
    Envoi un CR de disponibilite des Velibs a proximite 
    """
    loc = conf["location"]
    velib = Velib()
    message = ""
    for station, nbVelib in velib.dispo(loc).items():
        message += "Station %s : %d velos\n" % (station, nbVelib)
    pb = PushBullet(conf["pushbullet"]["api"])
    phone = pb.devices[0]
    phone.push_note("Dispos Velibs", message)

def main(argv):
    """
    Main
    """
    configFile = "../conf/config.yml"
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)

    # Checks the optional parameters
    try:
        opts, args = getopt.getopt(argv, "hc:",
                     ["help","config"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-c", "--config" ):
            configFile = a

    # Loads the configuration file
    if os.path.isfile(configFile):
        with open(configFile, 'r') as f:
            conf = yaml.load(f)
    else:
        print "ERROR. The config file [%s] does not exist !" % configFile
        usage()
        sys.exit(3)
    
    # Configure the logger
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.setLevel(conf['logging_level'])
    logger.addHandler(handler)

    delay = int(conf["delay"])
    timeout = int(conf["timeout"])
    
    print "*** RUMAH v %s ***" % __version__
    print " - Devices config file : %s" % configFile
    
    lastResults = dict()
    while True:
        for device, c in conf["devices"].iteritems():
            result = bluetooth.lookup_name(c["bdaddr"], timeout=timeout)
            if (result != None):
                if not (device in lastResults) or ((device in lastResults) and result != lastResults[device]):
       	            logger.log(logging.DEBUG, "%s: in" % device)
            else:
                if not (device in lastResults) or ((device in lastResults) and result != lastResults[device]):
       	            logger.log(logging.DEBUG, "%s: out" % device)
                    if c["notify"]:
                        logger.log(logging.DEBUG, "Envoi notification nb de Velibs")
                        notify_velib(conf)
    
            lastResults[device]=result
        
        time.sleep(delay)

if __name__ == "__main__":
    main(sys.argv[1:])
