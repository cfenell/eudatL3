### Import configuration


### Search an instance of Madrigal for experiments
### and create B2SHARE records
class madSearch:

    def __init__(self):

        from configparser import SafeConfigParser
        from B2SHAREClient import B2SHAREClient,EISCATmetadata
        import madrigalWeb.madrigalWeb as mw

        ## Read config
        config=SafeConfigParser()
        config.read('/usr/local/etc/eudatL2.conf')        
        madurl=self.config.get('Madrigal','URL')

        ## Open Madrigal connection
        try:
            self.madData=mw.MadrigalData(madurl)
        except:
            raise IOError("Could not open Madrigal connection")

        ## Set up one B2SHARE client instance 
        client=B2SHAREClient.B2SHAREClient(community_id=self.config.get('B2','community'), url=self.config.get('B2','b2share_url'),token=self.config.get('B2','token') )

    
    
    def B2entries(self, insts, byear, bmonth, bday, bhour, bmin, bsec, eyear, emonth, eday, ehour, emin, esec):
        
        import datetime
        
        ## List experiments
        madExps=self.madData.getExperiments(insts, byear, bmonth, bday, bhour, bmin, bsec, eyear, emonth, eday, ehour, emin, esec, local=1)
        
        ## Main loop over Madrigal experiments
        for thisExp in madExps:

            ## Build argument list for EISCATmetadata
            args=[]
            args.append(thisExp.id) # Experiment ID
            args.append(thisExp.name))    # Experiment name

            instMap={71:"kir", 72:"uhf", 73:"sod", 74:"vhf", 75: "kir", 76: "sod",  95:"lyr" }
            antenna=instMap(thisExp.instcode)
            args.append(antenna) # Instrument

            args.append(None) # Resources

            startTime=datetime.datetime(thisExp.startyear, thisExp.startmonth, thisExp.startday, thisExp.starthour, thisExp.startmin, thisExp.startsec)
            args.append(startTime) # Start time
            
            endTime=datetime.datetime(thisExp.endyear, thisExp.endmonth, thisExp.endday, thisExp.endhour, thisExp.endmin, thisExp.endsec)
            args.append(endTime)

            args.append(None) #Embargo time
            args.append(None) # Info directory

            ## Create metadata
            metadata_json = self.EISCATmetadata.MetaDataJSON(args, thisExp.realUrl , self.config.get('B2','community'), self.config.get('B2','community_specific'))

            ## Create B2SHARE draft
            draft_json=self.client.create_draft(metadata_json)

            ## get the files: plots, hdf5
            ## ... todo
            
            ## Upload file(s) to draft
            bucketID=draft_json['links']['files']
            # client.put_draft_file(bucketID, [ outFile ])
            
            
