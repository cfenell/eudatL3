### Search an instance of Madrigal for experiments
### and create B2SHARE records
    
def B2entries(insts, byear, bmonth, bday, bhour, bmin, bsec, eyear, emonth, eday, ehour, emin, esec):
    
    from B2SHAREClient import EISCATmetadata, B2SHAREClient
    import madrigalWeb.madrigalWeb as mw
    import madPlots
    import datetime
    from os import path, scandir, unlink
    from configparser import SafeConfigParser
    import logging

    ## Hardcoded numbering, Get from madrigal metadata instead?
    instMap={71:"kir", 72:"uhf", 73:"sod", 74:"vhf", 75: "kir", 76: "sod",  95:"lyr" }
    
    ## Read config
    config=SafeConfigParser(inline_comment_prefixes={'#'})
    config.read('/usr/local/etc/eudat.conf')        
    tmpdir=config.get('Main','tempDir')
    madurl=config.get('Madrigal','URL')

    ## Open Madrigal connection
    logging.info("Opening connection to %s" % madurl)
    try:
        madData=mw.MadrigalData(madurl)
    except:
        raise IOError("Could not open Madrigal connection")
    
    ## Set up one B2SHARE client instance
    b2url=config.get('B2','b2share_url')
    logging.info("Connecting to B2SHARE instance at %s" % b2url)
    try:
        client=B2SHAREClient.B2SHAREClient(community_id=config.get('B2','community'), url=b2url, token=config.get('B2','token'))
    except:
        raise IOError("Could not open B2Share connection")
        
    ## List experiments
    try:
        logging.debug("Listing Madrigal experiments")
        madExps=madData.getExperiments(insts, byear, bmonth, bday, bhour, bmin, bsec, eyear, emonth, eday, ehour, emin, esec, local=1)
    except:
        raise IOError("Could not list Madrigal experiments")
        
    ## Main loop over Madrigal experiments
    for thisExp in madExps:
        
        ## get the list of NCAR files
        logging.debug("Working on %s" % str(thisExp.id))
        expFiles=madData.getExperimentFiles(thisExp.id)

        ## Check for realtime experiments
        if len(expFiles) == 1:
            if (expFiles[0].category == 4) or expFiles[0].name.endswith('.asc') :
                # only a realtime file, skip to next experiment
                logging.info("Skipping experiment %s: only one realtime file" % str(thisExp.id))
                continue       

        logging.debug("Continuing with experiment %s" % str(thisExp.id))
        ## Build argument list for EISCATmetadata
        args=[]
        args.append(thisExp.id) # Experiment ID
        
        args.append(thisExp.name)    # Experiment name
        

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
        logging.debug("Creating JSON object")
        metadata_json = EISCATmetadata.MetaDataJSON(args, 3, thisExp.realUrl , config.get('B2','community'), config.get('B2','community_specific'))
        
        ## Create B2SHARE draft
        logging.info("Creating B2SHARE draft record for experiment %s" % str(thisExp.id))
        try:
            draft_json=client.create_draft(metadata_json)
        except:
            raise IOError("B2share draft creation error")

        ## Upload the files
        logging.debug("Uploading experiment files")
        for expFile in expFiles:

            if expFile.category==1:
                outFile=path.join(tmpdir, path.splitext(path.basename(expFile.name))[0] + '.hdf5')

                logging.info("Getting Madrigal file as %s" % outFile)
                try:
                    madData.downloadFile(expFile.name, outFile, 'B2Share client', 'b2@eiscat.se', 'EISCAT Scientific Association', format='hdf5')
                except:
                    raise IOError("Could not download experiment file from Madrigal")

                logging.info("Uploading the file to B2share file bucket")
                try:
                    client.put_draft_file(draft_json, [ outFile ])
                except:
                    raise IOError("Could not upload file")
                    
                # Add the parameters
                logging.debug("Getting parameters in file %s" % expFile.name)
                try:
                    expPars=madData.getExperimentFileParameters(expFile.name)
                except:
                    raise IOError("Could not get parameters from Madrigal")

                logging.debug("Creating JSON Patch with parameters")
                param_json_patch=EISCATmetadata.ParamJSONpatch(expPars, config.get('B2','community_specific'))
              
                # Patch B2Share entry
                logging.info("Inserting JSON patch with parameters in B2Share entry")
                try:
                    client.update_draft(draft_json, param_json_patch)
                except:
                    raise IOError("Could not upload JSON patch")
                    
        ## Add plots
        # Build true experiment URL
        logging.debug("Searching for figures to upload")
        expurl=thisExp.url
        if(expurl.find('cgi-bin/madtoc') > 0):
            expurl=expurl.replace('cgi-bin/madtoc/','')

        try:
            plotFiles=madPlots.get_plots(expurl, tmpdir)
        except:
            raise IOError("Could not search for madrigal plots")
        
        if(len(plotFiles)>0):
            logging.info("Uploading plots to B2Share: %s" % str(plotFiles))
            try:
                client.put_draft_file(draft_json, plotFiles)       
            except:
                raise IOError("Could not upload the files")
                
        ## Clean up temp dir
        logging.debug("Cleaning up files in %s" % tmpdir)
        for tmpfile in scandir(tmpdir):
            unlink(tmpfile.path)
    
        
