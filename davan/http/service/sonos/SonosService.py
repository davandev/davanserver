'''
@author: davandev
'''

import logging
import os
import urllib

import davan.config.config_creator as configuration
from davan.util import application_logger as app_logger
from davan.http.service.base_service import BaseService
import davan.util.constants as constants 

from soco import SoCo

class SonosService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, config):
        '''
        Constructor
        /Sonos?msg=sdfsa_asdfdf_asdf
        '''
        BaseService.__init__(self, constants.SONOS_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))

    def _parse_request(self, msg):
        return self.start(msg.split('=')[1])
    
    def handle_request(self, msg):
        '''
        Recevied request from Fibaro system to speak message via Sonos speakers.
        Check if message if already available, otherwise contact
        VoiceRSS to translate and get the mp3 file.
        @param msg to translate and speak.
        '''
        self.increment_invoked()
        tts_content = self._parse_request(msg)

        self.logger.info("Received request for new TTS message ["+ tts_content + "]")
        
        mp3_file = self.config['TTS_PRECOMPILED_ALARM_MSG_PATH'] + tts_content + ".mp3"

        self.logger.debug("Search for cached file: "+ mp3_file)
        if os.path.exists(mp3_file):
            self.logger.debug("Using cached mp3 file")
        else:   
            self.logger.debug("Generate mp3 for [" + tts_content+"]")
            self.generate_mp3(tts_content, mp3_file)
        
        self.logger.info("Playing file: " + 'http://'+ self.config["SERVER_ADRESS"] + ":" + str(self.config["SERVER_PORT"]) + '/' + mp3_file)
#        sonos = SoCo(self.config['SONOS_IP_ADRESS']) 
        sonos = SoCo('192.168.2.122:59152') 
        sonos.play_uri('http://192.168.2.50:8080/test-mp3')
        # Pass in a URI to a media file to have it streamed through the Sonos speaker
#        sonos.play_uri('http://'+ self.config["SERVER_ADRESS"] + ":" + str(self.config["SERVER_PORT"]) + '/' + mp3_file)
        
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG
    
    def generate_mp3(self, msg, mp3_file):
        ''' 
        Generate a mp3 file from the msg string.        
        Replace '_' with '%20' == whitespace
        @param msg message to translate
        @parm mp3_file output file where to store spoken msg.
        '''  
        encoded_msg = msg.replace("_", "%20")
        self.logger.debug("Encoded string [" + encoded_msg + "]")
        
        url = self.config['VOICERSS_URL'].replace("REPLACE_WITH_MESSAGE", encoded_msg)
        self.logger.debug("Url: ["+ url + "]")
        
        urllib.urlretrieve(url, mp3_file )

if __name__ == '__main__':

    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = SonosService()
    test.start("tts=skalskyddet_aktiverat")
