'''
Created on 10 mars 2017

@author: davandev
'''

import logging 
import os
import urllib2
import davan.util.cmd_executor as executor
import shutil

class TtsEngineAndroid():
    def __init__(self, config):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.config = config
        
    def generate_mp3(self, msg, mp3_file):
        ''' 
        Generate a mp3 file from the msg string.        
        Replace '_' with '%20' == whitespace
        @param msg message to translate
        @parm mp3_file output file where to store spoken msg.
        '''  
        encoded_msg = msg.replace("_", "%20")
        self.logger.debug("Encoded string [" + encoded_msg + "]")

        result = urllib2.urlopen(self.config["TTS_GENERATOR_CREATE_URL"] + "="+encoded_msg).read()
        
        return True
    
    def fetch_mp3(self, filename):
        self.logger.info("fetch_mp3") 
        result = urllib2.urlopen(self.config["TTS_GENERATOR_FETCH_URL"]).read()
        wav_file = self.config['TEMP_PATH'] + "tmp.wav"

        if (not os.path.exists(self.config['TEMP_PATH'])):
            os.mkdir(self.config['TEMP_PATH'])
                    
        if (os.path.exists(wav_file)):
            os.remove(wav_file)
            
        fd = open(wav_file, 'w')
        fd.write(result)
        fd.close()
        command = "lame --preset insane " + wav_file
        executor.execute_block(command, "lame", True)
        mp3_file = wav_file.replace('wav','mp3')
        shutil.move(wav_file, self.config['MP3_ROOT_FOLDER'] + filename)
        return filename
