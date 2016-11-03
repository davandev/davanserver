'''
Created on 8 feb. 2016

@author: davandev
'''
import logging
import os

import davan.config.config_creator as configuration
from davan.util import application_logger as app_logger
import pychromecast.pychromecast as chromecast
import davan.util.cmd_executor as cmd_executor
from davan.http.service.base_service import BaseService


class AudioService(BaseService):
    '''
    Following service requires https://github.com/miracle2k/onkyo-eiscp to 
    control the onkyo receiver
    and https://github.com/balloob/pychromecast/tree/master/pychromecast
    for controlling chromecast 
    sys.setdefaultencoding('latin-1')

    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, "AudioService",config)
        self.logger = logging.getLogger(os.path.basename(__file__))

    # Implementation of BasePlugin abstract methods        
    def handle_request(self, msg):
        '''
        Recevied request from Fibaro system to speak message.
        Check if message if already available, otherwise contact
        VoiceRSS to translate and get the mp3 file.
        @param msg to translate and speak.
        '''
        try:
            self.logger.info("Start")
            self.increment_invoked()
            
            self.turn_on_receiver()
            self.play_message(msg)
            self.turn_off_receiver()
        except:
            self.increment_errors()
            
    def turn_on_receiver(self):
        self.logger.info("Turn on receiver")
        cmd_executor.execute_block(self.config['RECEIVER_TURN_ON'], "onkyo")
        cmd_executor.execute_block(self.config['RECEIVER_SELECT_INPUT'], "onkyo")
        cmd_executor.execute_block(self.config['RECEIVER_SET_VOLUME'], "onkyo")
        
    def turn_off_receiver(self):
        self.logger.info("Turn off receiver")
        cmd_executor.execute_block(self.config['RECEIVER_TURN_OFF'], "onkyo")        
        
    def play_message(self, msg):
        self.logger.info("Play message : " + msg)
        self.logger.info("Connect")

        cast = chromecast.get_chromecast(friendly_name=self.config["CHROMECAST_NAME"])
        cast.wait()
        
        self.logger.info(cast.device)
        self.logger.info(cast.status)
        mc = cast.media_controller
        self.logger.info("Playing message:" + msg)

        mc.play_media('http://'+ self.config["SERVER_ADRESS"] + ":" + str(self.config["SERVER_PORT"]) + '/mp3=' + msg, 'audio/mpeg', autoplay=True)
        
if __name__ == '__main__':
    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = AudioService()
    test.start("Aktiverar_alarm_om_trettio_sekunder.mp3")
