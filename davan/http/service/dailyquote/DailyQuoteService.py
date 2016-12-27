# -*- coding: utf-8 -*-

'''
@author: davandev
'''
import logging
import os
import time
import urllib2

import davan.config.config_creator as configuration
import davan.util.constants as constants

from davan.util import application_logger as app_logger
from davan.http.service.tts.TtsService import TtsService 
from davan.http.service.audio.AudioService import AudioService
from davan.http.service.base_service import BaseService

class DailyQuoteService(BaseService):
    '''
    classdocs
    sys.setdefaultencoding('latin-1')

    '''

    def __init__(self, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.QUOTE_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))


    # Implementation of BasePlugin abstract methods        
    def handle_request(self, msg):
        '''
        Recevied request from Fibaro system to speak message.
        Check if message if already available, otherwise contact
        VoiceRSS to translate and get the mp3 file.
        @param msg to translate and speak.
        '''
        self.increment_invoked()
        qoute = self.add_prefix()
    
        qoute += self.fetch_quote()
        qoute = self.encode_quote(qoute)
        
        self.generate_mp3(qoute)
        self.play_file()
        
    def add_prefix(self):
        """
        Add some extra spoken text to handle case when first couple of 
        seconds disappear
        """
        quote="ding dong ding dong ding dong. Nu kommer ett meddelande "
        return quote
    
    def play_file(self):
        '''
        Play the mp3 file using receiver and chromecast
        '''
        self.logger.info("Play file")
        audio = AudioService(self.config)
        audio.turn_on_receiver()
        time.sleep(20)
        filename = os.path.basename(self.config['TTS_DAILY_QUOTE_FILE'])
        audio.play_message(filename)
        time.sleep(30)
        audio.turn_off_receiver()
            
    def generate_mp3(self, quote):
        '''
        Generate an mp3 file base on the quote
        @param quote, the text to generate
        '''
        self.logger.info("Generate mp3")
        tts = TtsService(self.config)

        if not os.path.exists(self.config['TTS_DAILY_QUOTE_PATH']):
            os.mkdir(self.config['TTS_DAILY_QUOTE_PATH'])
        if os.path.exists(self.config['TTS_DAILY_QUOTE_FILE']):
            os.remove(self.config['TTS_DAILY_QUOTE_FILE'])
                    
        tts.generate_mp3(quote, self.config['TTS_DAILY_QUOTE_FILE'])
        
    def encode_quote(self, quote):
        '''
        Encode the quote
        '''
        self.logger.debug("Encoding qoute")
        quote = quote.replace(" ","%20") # Whitespace
        quote = quote.replace('&auml;','%C3%A4') # ä
        quote = quote.replace('&aring;','%C3%A5') # å
        quote = quote.replace('&ouml;','%C3%A6') # ö
        
        quote = quote.replace('ä','%C3%A4') # Whitespace
        quote = quote.replace('å','%C3%A5') # Whitespace
        quote = quote.replace('ö','%C3%B6') # Whitespace
        self.logger.debug("Encoded quote:" + quote)
        return quote
    
    def fetch_quote(self):
        '''
        Fetch quote from dagenscitat.nu 
        @return the result
        '''
        self.logger.info("Fetching quote")
        quote = urllib2.urlopen("http://www.dagenscitat.nu/citat.js").read()
        self.logger.info("Received quote:" + quote)
        quote = quote.split("<")[1]
        result = quote.split(">")[1]
        self.logger.info("Result:" + result)
        return result
        

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        quote = self.fetch_quote()
        column  = column.replace("<SERVICE_VALUE>", quote)

        return column

if __name__ == '__main__':
    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = DailyQuoteService()
    test.start()
