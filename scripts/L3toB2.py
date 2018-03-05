#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""L3toB2.py

Search Madrigal server instance for data and create B2SHARE entries.

(C) Carl-Fredrik Enell 2018
carl-fredrik.enell@eiscat.se
"""

import os,  sys
import traceback
import getopt
import madrigal.metadata
from time import strptime, struct_time, sleep


if __name__ == '__main__':
    
    
    
    
### Define help string
usage = """[--inst=<comma-separated-kinsts>] [--newer=<yyyy-mm-ddTHH:MM:SS>]

--inst - to specify what instruments to include (comma separated kinsts). Default is all Eiscat instruments.
--newer=<yyyy-mm-ddTHH:MM:SS>: to create output only for experiments newer than specified time.
"""


### Set default arguments
# Instruments: all EISCAT instruments.
# Modify this for your site
instrumentList = [70,71,72,73,74,75,76,95,2950,2951]

# Default start time: 1970-01-01
fromTime=strptime('1970-01-01T00:00:00','%Y-%m-%dT%H:%M:%S')


### Parse command line

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["inst=","newer="])
except getopt.GetoptError, err:
    print str(err) 
    print(usage)
    sys.exit(2)

if len(args) != 1:
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
                raise ValueError, 'Unable to parse %s - should be comma separated kinst values (int)' % (a)

    if o == "--newer":
        try:
            fromTime=strptime(a,'%Y-%m-%dT%H:%M:%S')
        except ValueError:
            print("newer: Wrong date format: specify date as yyyy-mm-ddTHH:MM:SS")
            sys.exit(1)

            
    if o == "--delete":
        delXML=1
        try:
            xmlDir=a
        except ValueError:
            raise ValueError, "Give directory where existing Observation XML files can be found, --delete=<dir>"

print 'Creating B2SHARE records for instrument id :',
for inst in instrumentList:
          print '%d' %inst,
print


### Set up needed Madrigal metadata objects
madDB = madrigal.metadata.MadrigalDB()
siteID = madDB.getSiteID()
madExp = madrigal.metadata.MadrigalExperiment(madDB)
madInst = madrigal.metadata.MadrigalInstrument(madDB)


### Main loop over Madrigal experiments
for i in range(madExp.getExpCount()):

    # Ignore experiments with start time older than or equal to fromTime.
    if struct_time(madExp.getExpStartDateTimeByPosition(i))[0:6] <= fromTime[0:6]:
        continue
    
    thisSiteID = madExp.getExpSiteIdByPosition(i)    

    # Ignore non-local experiments
    if thisSiteID != siteID:
        continue

    kinst = madExp.getKinstByPosition(i)

    # Ignore instruments not in list
    if instrumentList:
        if kinst not in instrumentList:
            continue

    # Ignore non-ISR data
    # Comment out if not @EISCAT
    #if madInst.getCategoryId(kinst) != 1:
    #    continue 
       
    expId = madExp.getExpIdByPosition(i)
    expDir = madExp.getExpDirByPosition(i)
  
    # Ignore test experiments
    if madDB.isTestExperiment(expDir):
        continue
    
    
    # Conditions are passed -  Create record
    print('Working on exp no: %d id: %d path: %s' % (i,expId,expDir))
    
    # Deletion entry
    if(delXML):
        print('Creating Deletion entry from exp no %d in %s' % (expId,xmlDir))
        obj=delObs(expId,xmlDir,outputDir)
        del(obj)

    # New Observation entry
    obj=Observation(outputDir,expId)
    del(obj)
    sleep(.25)

### EOF
