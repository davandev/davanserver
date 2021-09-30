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
import davan.util.helper_functions as helper 
import davan.http.service.roomba.RoombaStateUtilities as rooombaStateUtil      
from davan.http.service.reoccuring_base_service import ReoccuringBaseService
import asyncio

class RoombaService(ReoccuringBaseService):
    '''
    Control roomba     
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        region_id : 8 == Wilma
        region_id : 9 == Tvattstuga
        region_id : 7 == Viggo
        region_id : 14 == Korridor
        region_id : 7 == Hall
        region_id : 7 == Kök
        region_id : 7 == Matsal
        region_id : 13 == Arbetsrum


        '''
        ReoccuringBaseService.__init__(self, constants.ROOMBA_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        logging.getLogger('Roomba.roomba.roomba980.roomba.roomba').setLevel(logging.CRITICAL)
        logging.getLogger('Roomba.Password').setLevel(logging.CRITICAL)

        self.user = config['ROOMBA_USER']
        self.pwd = config['ROOMBA_PWD']
        self.host = config['ROOMBA_HOST']
        self.roomba = None
        
        self.time_to_next_timeout = 300
        self.is_running = False
        self.state = None
        self.current_state = "Unknown"
        self.phase = "Unknown"
        self.mission = None
        self.battery = "-1"
  
    def get_next_timeout(self):
        if self.is_running:
            self.logger.debug("Status is running ")
            return 60
        self.logger.debug("Status is NOT running ")
        return self.time_to_next_timeout

    def init_service(self):
        pass

    def handle_timeout(self):
        self.logger.debug("Timeout, check status")
        loop = self._get_or_create_event_loop()
        loop.run_until_complete(self.fetch_status())
        self.update_status()
        self.report_status()
        
    def _get_or_create_event_loop(self):
        try:
            return asyncio.get_event_loop()

        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()
    
    async def fetch_status(self):
        import roomba.roomba980.roomba.roomba as roomba
        self.roomba = roomba.Roomba(self.host, self.user, self.pwd)
        self.roomba.connect()
        data_received = False
        for i in range(10):
            res = json.dumps(self.roomba.master_state, indent=2)
            if len(self.roomba.master_state) > 0 :
                self.logger.debug(res)
                data_received = True
                break        
            else:
                self.logger.debug("No data received")
            await asyncio.sleep(1)
            
        self.roomba.disconnect()

        if data_received ==False:
            self.logger.debug("No contact with roomba")
        else:
            self.mission = str(self.roomba.mission)
            self.phase = str(self.roomba.phase)  
            self.battery = str(self.roomba.batPct)

    def get_latest_state(self):
        '''
        Detemine and return the state of roomba 
        '''
        try:
            report_state = self.current_state
            self.logger.debug("ReportState:"+ report_state + " Battery:" + self.battery)

            if self.battery == "100":
                if report_state == "charge" or report_state == "standby" :
                    #self.logger.debug("Return standby")
                    return "standby"

            #self.logger.debug("Return "+self.roomba.phase )
        except:
            self.logger.warning("Failed to retrieve latest state")
        return self.roomba.phase

    def update_status(self):
        #self.logger.debug("Updates status")
        latest_state = self.get_latest_state()
        if self.current_state != latest_state:
            self.current_state = latest_state
            state_in_swe=rooombaStateUtil.states[self.current_state]
            helper.send_telegram_message(self.config, "Bogda[" + state_in_swe+"]")

        #self.logger.debug("Current state " + str(self.current_state))

        if self.roomba.bin_full == True:
            helper.send_telegram_message(self.config, "Bogda[ Töm damm behållaren ]")
            self.services.get_service(constants.TTS_SERVICE_NAME).start(
                     constants.ROOMBA_EMPTY_BIN,
                     constants.SPEAKER_KITCHEN)

        if self.current_state =="stuck" :
            error_number = self.roomba.error_num
            self.logger.warning("Error number: "+ str(error_number))
            error_msg = self.roomba.error_message
            self.logger.warning("Error msg: "+ str(error_msg))
            
            state_swe=rooombaStateUtil.states[self.roomba.phase]
            self.logger.warning("Error state: "+ str(state_swe))
            error_swe=rooombaStateUtil._ErrorMessages[error_number]
            self.logger.warning("Error msg: "+ str(error_swe[0]))
            helper.send_telegram_message(self.config, "Bogda[ "+error_swe[1]+" ]")
            error_swe="Bogda har fastnat och behöver hjälp, " + error_swe[1]+" "+ error_swe[0]

            self.services.get_service(constants.TTS_SERVICE_NAME).start(
                     error_swe,
                     constants.SPEAKER_KITCHEN)


    def report_status(self):
        '''
        Send updates to fibaro virtual device
        '''

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROOMBA_ID'],
                                self.config['FIBARO_VD_ROOMBA_MAPPINGS']['State'],
                                self.current_state)
        helper.send_auth_request(url,self.config)
        
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROOMBA_ID'],
                                self.config['FIBARO_VD_ROOMBA_MAPPINGS']['Battery'],
                                str(self.roomba.batPct) + " %")
        helper.send_auth_request(url,self.config)

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROOMBA_ID'],
                                self.config['FIBARO_VD_ROOMBA_MAPPINGS']['Time'],
                                str(self.roomba.mssnM))                                
        helper.send_auth_request(url,self.config)

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROOMBA_ID'],
                                self.config['FIBARO_VD_ROOMBA_MAPPINGS']['Bin'],
                                str(self.roomba.bin_full))                                
        helper.send_auth_request(url,self.config)

        if str(self.roomba.phase) == 'run':
            self.is_running = True 
        else:
            self.is_running = False

    def do_self_test(self):
        pass

    def handle_request(self, msg, speaker_id="0"):
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

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        res = "State: " + self.current_state
        res = "Battery: " + self.battery
        column  = column.replace("<SERVICE_VALUE>", res)

        return column

            
if __name__ == '__main__':

    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = RoombaService("",config)
    test.init_service()

    time.sleep(40)
    
