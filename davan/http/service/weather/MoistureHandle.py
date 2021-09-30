import logging
import os
import davan.util.helper_functions as helper 


class MoistureHandle():
    '''
    Constructor
    '''
    def __init__(self, config):
        self.logger = logging.getLogger(os.path.basename(__file__))

        self.config = config
        self.is_dry = False


    def handle_data(self, data):
        '''
        Process the recevied rain rate data
        '''
        dry_soil_list = self.check_soil_moisture_levels(data)
        if dry_soil_list :
            if not self.is_dry:
                self.is_dry = True
                msg = ""
                for id,moisture_level in dry_soil_list.items():
                    msg += id + " är torr och behöver vattnas ("+str(moisture_level)+" %), "
                self._notify_state_change( msg )
        else:
            self.is_dry = False
 
    def check_soil_moisture_levels(self,data):
        result = {}
        for x in range(1,7):
            id = 'soilmoisture'+str(x)
            if id in data.keys():

                moisture = data[id]
                name = self.config['FIBARO_VD_ECOWITT_MAPPINGS'][id][1]
                limit = self.config['FIBARO_VD_ECOWITT_MAPPINGS'][id][2]
                self.logger.info(name + " Moisture["+str(moisture)+"] Limit["+str(limit)+"]")
                if moisture < limit:
                    result[name] = moisture
                    self.logger.info(name+" behöver vattnas (" + str(moisture)+ " %)")
        return result


    def _notify_state_change(self,msg):
        '''
        Update any pool temp change
        '''
        self.logger.debug(msg)
        helper.send_telegram_message(self.config, msg)