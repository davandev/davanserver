'''
@author: davandev
'''
# coding: utf-8
import logging
import os
import traceback
import random
import datetime
import telepot
import urllib

from threading import Thread,Event
import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper_functions

from davan.util import application_logger as log_manager
from davan.http.service.base_service import BaseService

logger = logging.getLogger(os.path.basename(__file__))

class ReceiverBotService(BaseService):
    '''
    Monitor active scenes on Fibaro system, in some cases
    scenes that should always be running are stopped.
    Check status of each active scene and start it if stopped. 
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.RECEIVER_BOT_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        logging.getLogger('urllib3').setLevel(logging.CRITICAL)

        self.event = Event()
        self.bot = None

    def _parse_request(self,msg):
        self.logger.info("Parse request:" + msg)
        msg = msg.replace("/LogEntry?text=", "")
        return urllib.unquote(msg)
                
    def handle_request(self, msg):
        self.logger.info("handle_request: %s" %msg)
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG
    
    def stop_service(self):
        self.logger.info("Stopping service")
        try:
            self.event.set()
        except Exception:
            logger.error(traceback.format_exc())
#             
    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        '''
        self.logger.info("Starting re-occuring event")
 
        self.bot = telepot.Bot(self.config["RECEIVER_BOT_TOKEN"])
        self.bot.message_loop(self.handle)
 
        def loop():
            while not self.event.wait(10): # the first call is in `interval` secs
                pass
 
         
        Thread(target=loop).start()    
        return self.event.set
    


    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_id):
#         """
#         Override and provide gui
#         """
        if not self.is_enabled():
            return BaseService.get_html_gui(self, column_id)
        
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", "<li>Monitor: " + str() + " </li>\n")
        return column


    def handle(self,msg):
        try:
            logger.info("Handle : "+str(msg))
            chat_id = msg['chat']['id']
            command = msg['text']
         
            self.increment_invoked()
            logger.info( 'Got command: %s' % command )
            encoded_message = helper_functions.encode_message(command.encode('utf-8'))
            self.services.get_service(constants.TTS_SERVICE_NAME).start(encoded_message,1)
            url = 'http://192.168.2.173:80/web/message?text=%s&type=1&timeout=5' %encoded_message
            result = urllib.urlopen(url)
            res = result.read()
            self.bot.sendMessage(chat_id, "Message handled")

# local textinfo =fibaro:getGlobalValue("TvDisplayText")
# msg2 = string.gsub(textinfo,'%s','%%20')
# 
# local message = "/web/message?text=" .. msg2 .."&type=1&timeout=5"
# fibaro:debug("Message:" .. message)
# response ,status, errorCode = oFHttp:GET(message) 
# fibaro:debug("Response:" .. response .. " Status: " ..status .. " ErrorCode: ".. errorCode)
                
        except Exception:
            logger.error(traceback.format_exc())
        
if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = ReceiverBotService(config)
    test.start_service()