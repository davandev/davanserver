'''
Created on 17 feb. 2017

@author: davandev
'''

import logging
import os
import re
import traceback
from davan.http.service.base_service import BaseService
from davan.util import application_logger as app_logger
import davan.util.constants as constants
import davan.util.helper_functions as helper
import davan.config.config_creator as configuration
import davan.http.service.speaker.commands as commands
import requests
import time
import json
import paramiko

class VolumioService(BaseService):
    '''
    Play tts on volumio    
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.VOLUMIO_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.user = config['VOLUMIO_USER']
        self.pwd = config['VOLUMIO_PWD']
        self.host = config['VOLUMIO_HOST']
        self.current_play = None

    def init_service(self):
        pass

    def transfer_file(self, file_name):
        '''
        Transfer file via sftp to /mnt/internal/
        @param file_name, name of the mp3 file to transfer
        '''
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.host, username=self.user, password=self.pwd)

        sftp = client.open_sftp() 
        file_path = self.config['MP3_ROOT_FOLDER'] + file_name
        self.logger.info('Transfer file '+ file_path)
        sftp.put(file_path, '/mnt/INTERNAL/' + file_name)
        sftp.close()

    def play_local_url(self, file_name):
        '''
        Send command to play a locally stored file.
        '''
        if self.current_play :
            playlist = commands.create_play_list_and_restore(file_name, self.current_play)
        else:
            playlist = commands.create_play_list(file_name)
        
        commands.play_announcement(playlist)

    def do_self_test(self):
        pass

    def handle_request(self, msg, speaker_id="0"):
        '''
        Play mp3 file on volumio system.
        @param msg, file to play
        '''
        try:
            self.logger.info("Play " + str(msg) + " in volumio speaker")
            self.maybe_save_current_play()
            self.transfer_file(msg)
            time.sleep(10)
            
            self.play_local_url(msg)


            self.increment_invoked()
        except:
            msg = "Misslyckades att spela upp meddelande i volumio" 
            helper.send_telegram_message(self.config, msg)
            self.raise_alarm(constants.VOLUMIO_SERVICE_NAME, "Warning", msg)
            
            self.logger.error(traceback.format_exc())
            self.increment_errors()

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
            
    def maybe_save_current_play(self):
        '''
        Store the current url to be able to restore after play
        of anouncement
        '''
        resp = commands.state()
        self.current_play = json.loads(resp.text)
        self.logger.info("Resp: " +str(resp.text))

        if self.current_play["status"] == "play":
            self.logger.info("Currently playing")
            commands.pause()
            return True
        else:
            self.current_play = None
            self.logger.info("Currently NOT playing")
        return False


    def stop_playing(self):
        self.logger.info("Stop playing in volumio speaker")
        commands.stop()

    def play_external_url(self, url):
        commands.play_radio(url)

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
        res = "Speakers:\n"
        for _,speaker in list(self.speakers.items()):
            res += speaker.slogan + ":" + speaker.address + "\n"
        column  = column.replace("<SERVICE_VALUE>", res)

        return column
            
if __name__ == '__main__':

    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = VolumioService("",config)
    test.init_service()
