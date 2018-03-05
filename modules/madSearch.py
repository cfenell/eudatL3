### Import configuration
from configparser import SafeConfigParser

configuration=SafeConfigParser()
configuration.read('/usr/local/etc/eudatL2.conf')

### Search an instance of Madrigal for experiments
### and create B2SHARE records
class madSearch:

        
    def __init__(self):

        import madrigalWeb.madrigalWeb as mw
        madurl=self.configuration.get('Madrigal','URL')

        try:
            self.madData=mw.MadrigalData(madurl)
        except:
            raise IOError("Could not open Madrigal connection")

        
    def B2entries(self, insts, byear, bmonth, bday, bhour, bmin, bsec, eyear, emonth, eday, ehour, emin, esec):

        
        madExps=self.madData.getExperiments(insts, byear, bmonth, bday, bhour, bmin, bsec, eyear, emonth, eday, ehour, emin, esec, local=1)
        
        ### Main loop over Madrigal experiments
        for thisExp in madExps:

            # New Observation entry
            # TODO...
                
                
