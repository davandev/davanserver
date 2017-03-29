# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os
import json
import re
import time
from threading import Thread,Event

import davan.config.config_creator as configuration
import davan.util.cmd_executor as cmd
import davan.util.constants as constants
from davan.http.service.base_service import BaseService

class SpeedtestService(BaseService):
    '''
    Starts a re-occuring service that will measure internet speed (Download/Upload/ping)
    Requires speedtest-cli : installed with "sudo pip install speedtest-cli"
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.SPEEDTEST_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.event = Event()
        self.command = "/usr/local/bin/speedtest-cli --simple"
        
        self.ping_exp = re.compile(r'Ping:(.+?)ms')
        self.download_exp = re.compile(r'Download:(.+?)Mbit/s')
        self.upload_exp = re.compile(r'Upload:(.+?)Mbit/s')
        self.measure_time = ""
        
        self.encoded_string =""
        self.ping = 0
        self.download = 0
        self.upload = 0
        
    def stop_service(self):
        self.logger.info("Stopping service")
        self.event.set()
                
    def handle_request(self, msg):
        '''
        Received request for the latest speedtest measurements.
        '''
        self.increment_invoked()
        self.logger.debug("SpeedTest content: " + self.encoded_string)
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, self.encoded_string
    
    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        '''
        self.logger.info("Starting re-occuring event")
        def loop():
            while not self.event.wait(900): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()

        Thread(target=loop).start()    
        return self.event.set

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        if not self.is_enabled():
            return BaseService.get_html_gui(self, column_id)

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        #ok, mime, result = self.handle_request("")
        #data = json.loads(result)
        htmlresult = "<li>Ping: " + self.ping + " ms</li>\n"
        htmlresult += "<li>Download: " + self.download + " Mbit</li>\n"
        htmlresult += "<li>Upload: " + self.upload + " Mbit</li>\n"
        htmlresult += "<li>Date: " + self.measure_time + " </li>\n"
        
        column = column.replace("<SERVICE_VALUE>", htmlresult)
        
        return column

    def timeout(self):
        self.logger.info("Got a timeout, fetch internet speed")
        self.measure_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        self.ping = "0"
        self.download = "0"
        self.upload = "0"
        
        try:
            result = cmd.execute_block(self.command, "speedtest", True)
            match = self.ping_exp.search(result)
            if match:
                self.ping = match.group(1).strip()
            match = self.download_exp.search(result)
            if match:
                self.download = match.group(1).strip()
            match = self.upload_exp.search(result)
            if match:
                self.upload = match.group(1).strip()
        except:
            self.logger.warning("Caught exception when fetching internet speed")
                    
        self.encoded_string = json.JSONEncoder().encode({"Upload_Mbit":self.upload,"Download_Mbit":self.download,"Ping_ms": self.ping,"Date":str(self.measure_time)})
        self.logger.info("Encoded String:" + self.encoded_string)


if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import time
    
    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = SpeedtestService(config)
