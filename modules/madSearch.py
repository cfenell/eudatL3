### Search an instance of Madrigal for experiments
### and create B2SHARE records
    
def B2entries(insts, byear, bmonth, bday, bhour, bmin, bsec, eyear, emonth, eday, ehour, emin, esec):
    

    from configparser import SafeConfigParser
    from B2SHAREClient import EISCATmetadata, B2SHAREClient
    import madrigalWeb.madrigalWeb as mw
    import madPlots
    import datetime
    from os import path, scandir, unlink
        
    ## Read config
    config=SafeConfigParser(inline_comment_prefixes={'#'})
    config.read('/usr/local/etc/eudatL2.conf')        
    tmpdir=config.get('Main','tempDir')
    madurl=config.get('Madrigal','URL')
    
    ## Open Madrigal connection
    try:
        madData=mw.MadrigalData(madurl)
    except:
        raise IOError("Could not open Madrigal connection")
    
    ## Set up one B2SHARE client instance 
    client=B2SHAREClient.B2SHAREClient(community_id=config.get('B2','community'), url=config.get('B2','b2share_url'),token=config.get('B2','token') )

        
    ## List experiments
    madExps=madData.getExperiments(insts, byear, bmonth, bday, bhour, bmin, bsec, eyear, emonth, eday, ehour, emin, esec, local=1)
        
    ## Main loop over Madrigal experiments
    for thisExp in madExps:

        ## Build argument list for EISCATmetadata
        args=[]
        args.append(thisExp.id) # Experiment ID
        
        args.append(thisExp.name)    # Experiment name
        
        instMap={71:"kir", 72:"uhf", 73:"sod", 74:"vhf", 75: "kir", 76: "sod",  95:"lyr" }
        antenna=instMap[thisExp.instcode]
        args.append(antenna) # Instrument
        
        args.append(None) # Resources
        
        startTime=datetime.datetime(thisExp.startyear, thisExp.startmonth, thisExp.startday, thisExp.starthour, thisExp.startmin, thisExp.startsec)
        args.append(startTime) # Start time
        
        endTime=datetime.datetime(thisExp.endyear, thisExp.endmonth, thisExp.endday, thisExp.endhour, thisExp.endmin, thisExp.endsec)
        args.append(endTime)
        
        args.append(None) #Embargo time
        args.append(None) # Info directory
        
        ## Create metadata
        metadata_json = EISCATmetadata.MetaDataJSON(args, 3, thisExp.realUrl , config.get('B2','community'), config.get('B2','community_specific'))
        
        ## Create B2SHARE draft
        draft_json=client.create_draft(metadata_json)
        
        ## get the list of NCAR files
        expFiles=madData.getExperimentFiles(thisExp.id)

        for expFile in expFiles:

            if expFile.category==1:
                outFile=path.join(tmpdir, path.splitext(path.basename(expFile.name))[0] + '.hdf5')
            
                madData.downloadFile(expFile.name, outFile, 'B2Share client', 'b2@eiscat.se', 'EISCAT Scientific Association', format='hdf5')
                client.put_draft_file(draft_json, [ outFile ])

                # Add the parameters
                expPars=madData.getExperimentFileParameters(expFile.name)
                param_json_patch=EISCATmetadata.ParamJSONpatch(expPars, config.get('B2','community_specific'))
              
                # todo: debug this patch
                client.update_draft(draft_json, param_json_patch)
                
        ## Add plots
        # Build true experiment URL
        expurl=thisExp.url
        if(expurl.find('cgi-bin/madtoc') > 0):
            expurl=expurl.replace('cgi-bin/madtoc/','')
                    
        
        plotFiles=madPlots.get_plots(expurl, tmpdir)

        
        if(len(plotFiles)>0):
            client.put_draft_file(draft_json, plotFiles)       


        ## Clean up temp dir
        for tmpfile in scandir(tmpdir):
            unlink(tmpfile.path)
    
        
