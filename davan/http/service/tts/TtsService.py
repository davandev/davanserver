'''
@author: davandev
'''
 
import logging
import os
import urllib
import shutil
import __builtin__
import hashlib
import davan.config.config_creator as configuration
import davan.util.cmd_executor as cmd_executor
from davan.util import application_logger as app_logger
from davan.http.service.base_service import BaseService
import davan.util.constants as constants 
from davan.http.service.tts.tts_engine_voicerss import TtsVoiceRssFactory 
from davan.http.service.tts.tts_engine_android import TtsEngineAndroid

class TtsService(BaseService):
    '''
    classdocs
    sys.setdefaultencoding('latin-1')

    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.TTS_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.tts_engine = TtsEngineAndroid(config)
        self.async_filename = None
        
    def handle_request(self, msg):
        '''
        Received request to generate speech from msg
        @param msg, received request 
        '''
        self.logger.info("Msg:"+msg)
        if ("tts=Completed" in msg):
            self.handle_ttsCompleted_callback()
        else:
            self.start(msg.split('=')[1])

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG
    
    def start(self, msg):
        '''
        Recevied request from Fibaro system to speak message.
        Check if message if already available, otherwise contact
        VoiceRSS to translate and get the mp3 file.
        @param msg to translate and speak.
        '''
        self.increment_invoked()

        if os.path.exists(self.config['SPEAK_FILE']):
            os.remove(self.config['SPEAK_FILE'])

        self.logger.info("Received request for new TTS message ["+ msg + "]")
        mp3_file = self.calculate_file_name(msg)
        
        isAsync = False
        if os.path.exists(self.config['MP3_ROOT_FOLDER'] + mp3_file):
            self.logger.debug("Using cached mp3 file")
        else:   
            self.logger.debug("Generate mp3 for [" + msg+"]")
            isAsync = self.tts_engine.generate_mp3(msg, mp3_file)
        
        if not isAsync:
            self.play_file(mp3_file)
        else:
            self.async_filename = mp3_file
            self.logger.info("Wait for TTS results")
                    
    def play_file(self, mp3_file):
        """
        Play the mp3 files in speakers
        """
        shutil.copyfile(self.config['MP3_ROOT_FOLDER'] + mp3_file, self.config['SPEAK_FILE'])
        cmd_executor.execute_block_in_shell(self.config['SPEAK_CMD'] + ' ' + 
                                   self.config['SPEAK_FILE'] , 
                                   self.config['SPEAK_CMD'])

        speaker = __builtin__.davan_services.get_service(constants.ROXCORE_SPEAKER_SERVICE_NAME)
        speaker.handle_request(mp3_file)
        
    def handle_ttsCompleted_callback(self):
        """
        Received completed callback from TTS service  
        """
        self.logger.info("handle_ttsCompleted_callback") 
        if self.async_filename == None:
            return

        mp3_file = self.tts_engine.fetch_mp3(self.async_filename)
        self.play_file(mp3_file)
        self.async_filename = None        

    def calculate_file_name(self, msg):
        """
        Create the file name based on a md5 hash of the message
        """
        md5 = hashlib.md5()
        md5.update(msg)
        result = md5.hexdigest()
        mp3_file = result + ".mp3"
        self.logger.info("Checksum of ["+msg+"] = " + result)        
        return mp3_file
