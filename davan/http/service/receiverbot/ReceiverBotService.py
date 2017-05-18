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
import davan.util.converter_functions as converter
from davan.util import application_logger as log_manager
from davan.http.service.base_service import BaseService

logger = logging.getLogger(os.path.basename(__file__))

class ReceiverBotService(BaseService):
    '''
    Monitor active scenes on Fibaro system, in some cases
    scenes that should always be running are stopped.
    Check status of each active scene and start it if stopped. 
    
    Requires telepot:
    pip install telepot
    
    Requires opus-tools to convert
    sudo apt-get install opus-tools
    opusdec myaudio.ogg myaudio.wav
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.RECEIVER_BOT_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        logging.getLogger('urllib3').setLevel(logging.CRITICAL)
        self.current_speaker = "0"
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
        """
        Override and provide gui
        """
        if not self.is_enabled():
            return BaseService.get_html_gui(self, column_id)
        
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", "<li>Monitor: " + str() + " </li>\n")
        return column


    def handle(self,msg):
        '''
        Receive a message from telegram (telepot)
        Determine if it is a voice or text message and
        play in the configured speaker. 
        '''
        try:
            logger.info("Handle : "+str(msg))
            chat_id = msg['chat']['id']
 
            if self.is_text_message(msg):
                result = self.handle_text_message(msg)
            else:
                result = self.handle_voice_message(msg)
            self.increment_invoked()
            
            self.bot.sendMessage(chat_id, result)
        except Exception:
            logger.error(traceback.format_exc())
            self.bot.sendMessage(chat_id, "Failed to handle message")
            
    def handle_voice_message(self, message):
        '''
        A voice message is returned from Telegram, download it.
        Convert the downloaded ogg file to wav, needed since the 
        roxcore speakers cannot handle the ogg encoding.
        @param message message to play in speaker.
        '''
        ogg_file = self.config['TEMP_PATH'] + 'telegram_voice.ogg'
        self.bot.download_file(message['voice']['file_id'], ogg_file)
        wav_file = converter.ogg_to_wav(self.config, ogg_file)
        speaker = self.services.get_service(constants.ROXCORE_SPEAKER_SERVICE_NAME)
        speaker.handle_request(wav_file,self.current_speaker)
        return "Voice message played in speaker " + self.current_speaker
        

    def handle_text_message(self,message):
        '''
        Received a text message, 
        '''            
        command = message['text']
        logger.info( 'Got command: %s' % command )
        
        if command == "speakers":
            speaker = self.services.get_service(constants.ROXCORE_SPEAKER_SERVICE_NAME)
            result = "Available speakers: \n"
            for key,value in speaker.speakers.items():
                result += "Id[" + key + "]" + "Name[" +value.slogan+ "]\n"
            result += "Current speaker is " + self.current_speaker
            return result
        elif command.startswith("set speaker "):
            self.current_speaker = command.replace("set speaker ", "")
            result = "Current speaker is : "+ self.current_speaker
            return result
        else:
            encoded_message = helper_functions.encode_message(command.encode('utf-8'))
            tts_service = self.services.get_service(constants.TTS_SERVICE_NAME)
            tts_service.start(encoded_message,self.current_speaker)
    
            url = 'http://192.168.2.173:80/web/message?text=%s&type=1&timeout=5' %encoded_message
            result = urllib.urlopen(url)
            res = result.read()
            return "Text message played in speaker "+ self.current_speaker 

    def is_text_message(self, msg):
        '''
        Determine if text message is a text or voice message
        @return True if text message, False otherwise
        '''
        try:
            msg['text']
            return True
        except:
            return False
        
if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = ReceiverBotService(config)
    test.start_service()