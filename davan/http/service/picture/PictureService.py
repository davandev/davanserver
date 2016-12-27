# -*- coding: utf-8 -*- 
'''
@author: davandev
'''

import logging
import os
import traceback
import sys

import davan.config.config_creator as configuration
import davan.util.constants as constants

from davan.util import cmd_executor as cmd_executor
from davan.http.service.base_service import BaseService

class PictureService(BaseService):
    '''
    Motion detected on sensors, take photo from camera and send to 
    all Telegram receivers
    '''

    def __init__(self, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, "TakePicture", config)
        self.logger = logging.getLogger(os.path.basename(__file__))
    
    def handle_request(self, msg):
        '''
        Handle received request, 
        - Take pictures from all configured cameras,
        - Send pictures to all configured receivers
        - Delete pictures.
        '''
        try:
            self.increment_invoked()
            camera = self.parse_request(msg)
            self.take_picture(camera)
            self.send_picture(camera)
            self.delete_picture()
            return 200, ""
        except:
            self.increment_errors()
            self.logger.info("Failed to carry out takepicture request")
            traceback.print_exc(sys.exc_info())
            pass

    def parse_request(self, msg):
        '''
        Return camera name from received msg.
        '''
        self.logger.info("Parsing: " + msg ) 
        msg = msg.replace("/TakePicture?text=", "")
        return msg

    def delete_picture(self):
        '''
        Deletes the taken photo
        '''
        self.logger.debug("Deleting picture")
        os.remove("/var/tmp/snapshot.jpg")
        
    def send_picture(self, camera):
        '''
        Send picture to all configured telegram receivers
        @param camera: camera name 
        '''
        for chatid in self.config['CHATID']:
            self.logger.info("Sending picture to chatid[" + chatid + "]")
            
            telegram_url = ('curl -X POST "https://api.telegram.org/bot' + 
                                 self.config['TOKEN'] + 
                                 '/sendPhoto" -F  chat_id=' + 
                                 chatid +
                                 ' -F photo="@/var/tmp/snapshot.jpg" -F caption="Rörelse upptäckt från ' +
                                 camera +'"' )       
            self.logger.debug(telegram_url)
            cmd_executor.execute_block(telegram_url,"curl")
        
    def take_picture(self, camera):
        '''
        Take a picture from the camera, store it temporary on file system
        Verify that camera is configured (has ip adress, user and password) otherwise rais an exception
        @param camera: camera name 
        '''
        self.logger.info("Take picture from camera " + camera)
        if self.config["CAMERAS"].has_key(camera):
            cam_picture_url = self.config["CAMERAS"][camera]
            cmd_executor.execute("wget " + cam_picture_url + "  --user=" + self.config["CAMERA_USER"] +
                                 " --password=" + self.config["CAMERA_PASSWORD"] + " --auth-no-challenge")
            cmd_executor.execute("sudo mv snapshot.cgi /var/tmp/snapshot.jpg")
        else:
            raise Exception("No camera url for [" + camera + "] configured")   

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
        column = column.replace("<SERVICE_VALUE>", "<li>Cameras: " + str(self.config["CAMERAS"].keys()) + " </li>\n")
        return column
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    camerapath = "/TakePicture?text=Framsidan"
    test = PictureService()
    test.start(camerapath)
