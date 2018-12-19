'''
@author: davandev
'''

import logging
import os
import urllib
import urllib2
import traceback

from datetime import datetime
import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper
from davan.http.service.reoccuring_base_service import ReoccuringBaseService

class KeypadEvent():
    def __init__(self, name, ip):
        self.logger = logging.getLogger(os.path.basename(__file__))

        self.name = name
        self.ip = ip
        self.connected = False
        self.connected_at = ""
        self.disconnected_at = ""
        

    def toString(self):
        return "Name["+self.name+"] "\
            "IP["+self.ip+"] "\
            "Connected["+str(self.connected)+"] " \
            "Disconnected_at["+self.disconnected_at+"] " \
            "Connected_at["+self.connected_at+"]"
            
class KeypadAliveService(ReoccuringBaseService):
    '''
    Check if keypad is still running by sending a http request towards the keypad
    if there is no response from the keypad then a telegram message is sent.
    Re-occuring event every 5th minute 
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.KEYPAD_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.keypads= []
        self.time_to_next_timeout = 600
        try:
            for name, ip in self.config['KEYPAD_IP_ADDRESSES'].iteritems():
                keypad = KeypadEvent(name, ip)
                self.logger.info(keypad.toString())
                self.keypads.append(keypad)
        except:
            self.logger.error(traceback.format_exc())
            
    def get_next_timeout(self):
        '''
        Return time to next timeout
        '''
        return self.time_to_next_timeout
    
    def handle_timeout(self):
        '''
        Timeout received, send a "ping" to key pad, send telegram message if failure.
        '''
        self.logger.info("Got a timeout, send keep alive to")
        for keypad in self.keypads:
            try:
                self.logger.debug("Sending ping to keypad[" + keypad.name + "]")
                urllib.urlopen(self.config['KEYPAD_PING_URL'].replace('%IP%',keypad.ip))
                self.maybe_send_update(keypad, True)
            except:
                self.logger.warning("Failed to connect to keypad[" + keypad.name + "]")
                self.increment_errors()
                self.maybe_send_update(keypad, False)
    
    
    def get_log(self):
        self.logger.info("Fetch keypad logfile")
        try:
            log_file = urllib2.urlopen(self.config['KEYPAD_LOG_URL']).read()
            log_file = log_file.replace("<br>","\n")
            if os.path.exists(self.config["KEYPAD_LOG_FILE"]):
                os.remove(self.config["KEYPAD_LOG_FILE"])
                
            fd = open(self.config["KEYPAD_LOG_FILE"],'w')
            fd.write(log_file)
            fd.close()
            return self.config["KEYPAD_LOG_FILE"]
        except:
            self.increment_errors()
            self.logger.warning("Failed to fetch log file from keypad")
            return None
        
    def maybe_send_update(self, keypad, state):
        '''
        Send telegram message if state has changed
        @param state, current state of keypad
        '''
        #currentTime = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        n = datetime.now()
        currentTime = format(n,"%Y-%m-%d %H:%M")

        if keypad.connected == True and state == False:
            self.logger.info("Keypad[ " + keypad.name + " ] state changed[Disconnected]") 
            keypad.connected = False
            keypad.disconnected_at = currentTime
            str = constants.KEYPAD_NOT_ANSWERING.replace("%", keypad.name)
            self.raise_alarm(str,"Warning",str)
            
            helper.send_telegram_message(self.config, str)

        elif keypad.connected == False and state == True:
            self.logger.info("Keypad[" + keypad.name + "] state changed[Connected]") 
            str = constants.KEYPAD_NOT_ANSWERING.replace("%", keypad.name)
            self.clear_alarm(str)

            keypad.connected = True
            keypad.connected_at = currentTime
            keypad.disconnected_at = ""
            str = constants.KEYPAD_ANSWERING.replace("%", keypad.name)
            helper.send_telegram_message(self.config, str)
    
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
            return ReoccuringBaseService.get_html_gui(self, column_id)

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        html = ""
        for keypad in self.keypads:
            html += "<li>Name: " + str(keypad.name) + " </li>\n"
            html += "<li>Ip: " + str(keypad.ip) + " </li>\n"
            html += "<li>Connected: " + str(keypad.connected) + " </li>\n"
            html += "<li>Connected at: " + str(keypad.connected_at) + " </li>\n"
            html += "<li>Disconnected at: " + str(keypad.disconnected_at) + " </li>\n"
        column = column.replace("<SERVICE_VALUE>", html)
        return column
    
if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import time
    
    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=3)
    
    test = KeypadAliveService()
    time.sleep(10)
    test.stop_service()
