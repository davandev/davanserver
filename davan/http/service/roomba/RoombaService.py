'''
Robot Data:
{
  ver: '3',
  hostname: 'iRobot-E3513FD46E1A4EFEB4336ED260280551',
  robotname: 'Bogda',
  robotid: 'E3513FD46E1A4EFEB4336ED260280551',
  ip: '192.168.2.110',
  mac: '50:14:79:23:74:49',
  sw: 'lewis+3.14.16+lewis-release-121+21',
  sku: 'i715040',
  nc: 0,
  proto: 'mqtt',
  cap: {
    binFullDetect: 2,
    dockComm: 1,
    wDevLoc: 2,
    bleDevLoc: 1,
    edge: 0,
    maps: 3,
    pmaps: 5,
    tLine: 2,
    area: 1,
    eco: 1,
    multiPass: 2,
    pose: 1,
    team: 1,
    pp: 0,
    lang: 2,
    '5ghz': 1,
    prov: 3,
    sched: 1,
    svcConf: 1,
    ota: 2,
    log: 2,
    langOta: 0,
    tileScan: 1
  },
  blid: 'E3513FD46E1A4EFEB4336ED260280551'
}
Password=> :1:1625084722:9dXs2npZq134h4jZ <= Yes, all this string.
Use this credentials in dorita980 lib :)
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
import requests
import time
import json
      
from davan.http.service.reoccuring_base_service import ReoccuringBaseService
import asyncio

class RoombaService(ReoccuringBaseService):
    '''
    Control roomba     
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.ROOMBA_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.user = config['ROOMBA_USER']
        self.pwd = config['ROOMBA_PWD']
        self.host = config['ROOMBA_HOST']
        self.roomba = None
        self.time_to_next_timeout = 300

    def get_next_timeout(self):
        return self.time_to_next_timeout

    def init_service(self):
        pass

    def handle_timeout(self):
        self.logger.info("Timeout, check status")
        loop = self._get_or_create_event_loop()
        loop.run_until_complete(self.check_status())
        
    def _get_or_create_event_loop(self):
        try:
            return asyncio.get_event_loop()

        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()
    
    async def check_status(self):
        import roomba.roomba980.roomba.roomba as roomba
        self.roomba = roomba.Roomba(self.host, self.user, self.pwd)
        self.roomba.connect()

        for i in range(10):
            res = json.dumps(self.roomba.master_state, indent=2)
            if len(self.roomba.master_state) > 0 :
                self.logger.info(res)
                break
            else:
                self.logger.info("No data received")
            await asyncio.sleep(1)

        self.roomba.disconnect()

    def do_self_test(self):
        pass

    def handle_request(self, msg, speaker_id="0"):
        '''
        Play mp3 file on volumio system.
        @param msg, file to play
        '''
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
            

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

        column = column.replace("<SERVICE_NAME>",   self.service_name)
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        res = "-"
        column  = column.replace("<SERVICE_VALUE>", res)

        return column
            
if __name__ == '__main__':

    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = RoombaService("",config)
    test.init_service()

    time.sleep(40)
    
