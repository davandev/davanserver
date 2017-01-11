'''
Created on 8 feb. 2016

@author: davandev
'''
import logging
import os
import urllib
import datetime
from threading import Thread,Event
import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper
import telnetlib
from davan.http.service.presence.AsusRouterDeviceStatus import AsusRouterDeviceStatus
from davan.http.service.base_service import BaseService
'''
'''
class AsusRouterPresenceService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.DEVICE_PRESENCE_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.monitored_devices = {}
        self.list_active_devices_cmd = "/usr/sbin/ip neigh"
        
        for key, value in self.config['MONITORED_DEVICES'].items():
            self.monitored_devices[key]= AsusRouterDeviceStatus(key, value)

        self.event = Event()
    
    def stop_service(self):
        self.logger.info("Stopping service")
        self.event.set()
            
    def notify_change(self, device):
        '''
        Update Virtual device on Fibaro system send Telegram messages
        with the changed device and status
        @param device device that changed state
        '''
        self.logger.info("Notify status change")
        if device.active :
            status = "Hemma"
        else:
            status = "Borta"
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                               self.config['FIBARO_VD_PRESENCE_ID'],
                               self.config['FIBARO_VD_MAPPINGS'][device.user],
                               status)
        urllib.urlopen(url)        

        helper.send_telegram_message(self.config, device.user + " [" + status + "]")
        
    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        '''
        self.logger.info("Starting re-occuring event")
        def loop():
            while not self.event.wait(300): # the first call is in `interval` secs
                self.increment_invoked()
                self.timeout()
        Thread(target=loop).start()    
        return self.event.set
     
    def fetch_active_devices(self):
        '''
        Fetch device status from router. 
        @return list of found devices
        '''
        self.logger.info("Fetch active devices from router")
        tn = telnetlib.Telnet(self.config['ROUTER_ADRESS'])
        
        tn.read_until("login: ")
        tn.write(self.config['ROUTER_USER'] + "\n")
        tn.read_until("Password: ")
        tn.write(self.config['ROUTER_PASSWORD'] + "\n")
        
        tn.write(self.list_active_devices_cmd + "\n")
        tn.write("exit\n")
        
        result = tn.read_all()
        lines = result.split("\n")
    
        return lines
    
    def update_presence(self, monitored_devices, active_devices):
        '''
        Determine if any of the active devices in router is also
        monitored, then check device status
        '''
        for line in active_devices:
            if line.startswith("192."):
                items = line.split()
                if items[0] in monitored_devices.keys():
                    self.logger.info("Found a monitored device [" + items[0] +"]")
                    self.update_device_status(items, monitored_devices)

    def update_device_status(self, status, monitored_devices):
        '''
        Update device status of a monitored device
        '''
        device = monitored_devices[status[0]]
        device.changed = False
        previous_status = device.active
        
        if("REACHABLE" in status or "STALE" in status):
            device.active = True
        elif "FAILED" in status:
            device.active = False
            
        if (previous_status == device.active):
            self.logger.info("No change of status for device[" + status[0] + "]")
            device.changed = False
            if device.active:
                device.last_active = str(datetime.datetime.now())
        else:
            self.logger.info("Change of status for device[" + status[0] + "]")
            device.changed = True
            if device.active:
                device.first_active = str(datetime.datetime.now())

    def timeout(self):
        self.logger.info("Check active devices")
        active_devices = self.fetch_active_devices()
        self.update_presence(self.monitored_devices, active_devices)
        
        for ip, device in self.monitored_devices.items():
            device.toString()
            if device.changed:
                self.notify_change(device)
                
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
        htmlresult = ""
        for _,device in self.monitored_devices.items():
            htmlresult += "<li> " + device.user  + "["+device.active_toString()+"]</li>\n"
        column = column.replace("<SERVICE_VALUE>", htmlresult)
        
        return column
                
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create('/home/pi/private_config.py')
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = AsusRouterPresenceService(config)
    test.timeout()
