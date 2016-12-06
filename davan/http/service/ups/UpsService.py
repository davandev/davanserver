'''
@author: davandev
'''
import logging
import os
import traceback
import sys
import urllib

import davan.config.config_creator as configuration
from davan.util import cmd_executor as cmd_executor
from davan.http.service.base_service import BaseService
import davan.util.constants as constants
import json

class UpsService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.UPS_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))

        # Apc access command
        self.command = "apcaccess"
        self.payload = "/Ups?text="
                    
    def parse_request(self, msg):
        self.logger.info("Parsing: " + msg ) 
        msg = msg.replace(self.payload, "")
        return msg
             
    def handle_request(self, msg):
        '''
        Invoked from UPS or Fibaro system.
        UPS invokes script when status of UPS changes
        Fibaro invokes script to refresh status
        '''
        try:
            self.increment_invoked()
            result =""
            service = self.parse_request(msg)
            if (constants.UPS_BATTERY_MODE in service or 
                constants.UPS_POWER_MODE in service):
                self._update_changed_status_on_fibaro()
            
            if constants.UPS_STATUS_REQ in service:
                result = self._handle_status_request()
            
            return constants.RESPONSE_OK, result
  
        except:
            self.logger.info("Failed to carry out ups request")
            self.increment_errors()
            traceback.print_exc(sys.exc_info())
 
    def _update_changed_status_on_fibaro(self):
        """
        Status changed on UPS, update virtual device on Fibaro system.
        """
        self.logger.info("UPS status changed")
        # Build URL to Fibaro virtual device
        pressButton_url = self.config["VD_PRESS_BUTTON_URL"].replace("<ID>", self.config['UPS_VD_ID'])
        pressButton_url = pressButton_url.replace("<BUTTONID>", self.config["UPS_BUTTON_ID"]) 
        self.logger.debug(pressButton_url)
        
        # Send HTTP request to notify status change
        urllib.urlopen(pressButton_url)

    def _handle_status_request(self):
        '''
        Fetch status from UPS, 
        @return result json formatted
        '''
        self.logger.info("Ups status request")
        response = cmd_executor.execute_block(self.command, self.command, True)
        parsedResponse = response.rstrip().split('\n')
        jsonResult = "{"
        for line in parsedResponse:
            if "STATUS" in line:
                status = line.split(":")
                jsonResult += '"Status":"'+status[1].replace(" ","")+'",'
            if "LOADPCT" in line:
                load = line.split(":")
                loadRes = load[1].replace("Percent Load Capacity","%")
                jsonResult += '"Load":"'+loadRes.lstrip()+'",'
            if "BCHARGE" in line:
                battery = line.split(":")
                battery = battery[1].replace("Percent","%")
                jsonResult += '"Battery":"'+battery.lstrip()+'",'
            if "TIMELEFT" in line:
                time = line.split(":")
                jsonResult += '"Time":"'+time[1].lstrip()+'"'
        jsonResult += "}"
        self.logger.info("Result: "+ jsonResult)
        return jsonResult
    
    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, id):
        """
        Override and provide gui
        """
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        _, result = self.handle_request("Status")
        data = json.loads(result)
        htmlresult = "<li>Status: " + data["Status"] + "</li>\n"
        htmlresult += "<li>Load: " + data["Load"] + " </li>\n"
        htmlresult += "<li>Battery: " + data["Battery"] + " </li>\n"
        htmlresult += "<li>Time: " + data["Time"] + " </li>\n"
        column = column.replace("<SERVICE_VALUE>", htmlresult)
        return column
    
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    upspath = "/Ups?text=Status"
    test = UpsService()
    test.start(upspath)
