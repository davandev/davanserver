# -*- coding: utf-8 -*-

'''
@author: davandev
'''
import logging
import os

import davan.util.cmd_executor as executor
import davan.util.constants as constants
import davan.util.helper_functions as helper_functions
from davan.http.service.base_service import BaseService

class TvService(BaseService):
    '''
    classdocs
    sys.setdefaultencoding('latin-1')
     harmony --harmony_ip 192.168.2.143 start_activity --activity 26681450
     harmony --harmony_ip 192.168.2.143 power_off
     harmony --harmony_ip 192.168.2.143 show_config
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.TV_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        
        self.base_cmd = "harmony --harmony_ip "
        self.start_activity_cmd = 'start_activity --activity '
        self.stop_activity_cmd = 'power_off'
        self.current_activity_cmd = 'show_current_activity'
        self.watch_tv_activity = '26681450'
        
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
        
        column  = column.replace("<SERVICE_VALUE>", "")

        return column
    
    def enable(self, enable):
        cmd = self.base_cmd + self.config['HARMONY_IP_ADRESS']
        
        if enable == True:
            cmd += self.start_activity_cmd
            cmd += self.watch_tv_activity
            executor.execute_block(cmd, 'Harmony')
            self.status = "On"
        else:
            cmd += self.stop_activity_cmd
            executor.execute_block(cmd, 'Harmony')
            self.status = "Off"
            
    def get_status(self):
        '''
        Get the current status
        '''
        cmd = str(self.base_cmd)
        cmd += str(self.config['HARMONY_IP_ADRESS'] + " ")
        cmd += self.current_activity_cmd
        self.logger.info(cmd)
        result = executor.execute_block(cmd, 'Harmony', True).strip()
        self.logger.info("Res:" + result)
        if result == 'PowerOff':
            self.status = 'Off'
        elif result == 'Watch TV':
            self.status = 'On'
        else:
            self.logger.warning("Unknown activity")
            self.status = 'Unknown state'
        return self.status
        
    def get_announcement(self):
        '''
        Compile and return announcment.
        @return html encoded result
        '''
        return helper_functions.encode_message("Tv status " + self.status)
    
if __name__ == '__main__':
    import davan.config.config_creator as configuration
    from davan.util import application_logger as log_manager
    
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = TvService("", config)
    test.get_status()
