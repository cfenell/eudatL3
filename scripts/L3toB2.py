#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""L3toB2.py

Search Madrigal server instance for data and create B2SHARE entries.

(C) Carl-Fredrik Enell 2018
carl-fredrik.enell@eiscat.se
"""

import sys, getopt
from time import strptime
from madSearch import B2entries


if __name__ == '__main__':
    
    ### Define help string
    usage = """[--inst=<comma-separated-kinsts>] <start-time> <end-time>

    --inst - to specify what instruments to include (comma separated kinsts). Default is all Eiscat instruments.
    """

    ### Default instruments: all EISCAT radars
    instrumentList = [70,71,72,73,74,75,76,95]
        
    ### Parse command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["inst="])
    except getopt.GetoptError as err:
        print(str(err))
        print(usage)
        sys.exit(2)
        
    if len(args) != 2:
        print(usage)
        sys.exit(-1)
            

    for o, a in opts:

        if o == "--inst":
            instList = a.split(',')
            instrumentList = []
            for item in instList:
                try:
                    instrumentList.append(int(item))
                except NameError:
                    raise ValueError("Unable to parse %s - should be comma separated kinst values (int)' % (a)")

    try:
        startTime=strptime(args[0],'%Y-%m-%dT%H:%M:%S')
    except:
        raise ValueError("Wrong start time format")

    try:
        endTime=strptime(args[1],'%Y-%m-%dT%H:%M:%S')
    except:
        raise ValueError("Wrong start time format")
    
    # Todo: change me to logging                                
    print("Creating B2SHARE records for instruments :" + str(instrumentList)),
    
    ### Call Madrigal-B2SHARE routine
    b2create=B2entries(instrumentList, startTime.tm_year, startTime.tm_mon, startTime.tm_mday, startTime.tm_hour, startTime.tm_min, startTime.tm_sec, endTime.tm_year, endTime.tm_mon, endTime.tm_mday, endTime.tm_hour, endTime.tm_min, endTime.tm_sec)

    
    



    
