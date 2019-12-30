'''
@author: davandev
'''

import logging
import os
import urllib
import datetime
import telnetlib
import paramiko

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper

from davan.http.service.presence.AsusRouterDeviceStatus import AsusRouterDeviceStatus,\
    FAMILY, GUESTS, HOUSE
from davan.http.service.reoccuring_base_service import ReoccuringBaseService

'''
'''
class AsusRouterPresenceService(ReoccuringBaseService):
    '''
    This service is tested on an Asus router and relies on Telnet being enabled in the router.
    It is enabled in the router configuration.
    The presence of the monitored devices are determined on whether the device is 
    connected on the wifi network.
    The check is done by logging into the router via Telnet, and checking the connections
    using command "/usr/sbin/ip neigh" this gives a list of devices registered.
    Each device can be in state ESTABLISHED, STALE or FAILED.
    FAILED means that the device is not connected to the network. The states ESTABLISHED and STALE is
    interpreted as being available on wifi network.
    At state change a telegram message is sent to the receivers. Virtual device on Fibaro HC2 is also updated 
    with the state change.
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.DEVICE_PRESENCE_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        
        # Command to run on router to list available devices
        self.list_active_devices_cmd = "/usr/sbin/ip neigh"
        # Check status every 5th minute
        self.time_to_next_timeout = 300
        self.unknown_devices = []
        self.family_devices = {}
        for key, value in self.config['FAMILY_DEVICES'].items():
            self.family_devices[key]= AsusRouterDeviceStatus(key, value, FAMILY)
            
        self.guest_devices = {}
        for key, value in self.config['GUEST_DEVICES'].items():
            self.guest_devices[key]= AsusRouterDeviceStatus(key, value, GUESTS)

        self.house_devices = {}
        for key, value in self.config['HOUSE_DEVICES'].items():
            self.house_devices[key]= AsusRouterDeviceStatus(key, value, HOUSE)
    
    def get_next_timeout(self):
        return self.time_to_next_timeout
    
    def handle_timeout(self):
        #self.logger.info("Check presence of monitored devices")

        active_devices = self.fetch_active_devices()
        # Check family status
        self.check_device_group(self.family_devices, active_devices)
        # check guest status
        self.check_device_group(self.guest_devices, active_devices)
        # check house devices
        self.check_device_group(self.house_devices, active_devices)
        
        self.check_unknown_devices(active_devices)
    
    def check_unknown_devices(self, active_devices):
        #self.logger.info("Check unknown devices")
        for line in active_devices:
            if line.startswith("192."):
                items = line.split()
                if items[0] in self.family_devices.keys():
                    continue
                elif items[0] in self.guest_devices.keys():
                    continue
                elif items[0] in self.house_devices.keys():
                    continue
                else:
                    if items[0] not in self.unknown_devices:
                        self.logger.warning("Unknown: "+ items[0])
                        self.unknown_devices.append(items[0])
                    if items[3] == "REACHABLE" or items[3] == "STALE":
                        self.logger.warning("Unknown active device : "+ str(items))
                        helper.send_telegram_message(self.config, "Unknown device is now active on network")

                        
 
    def check_device_group(self, monitored_devices, active_devices):
        # Reset changed state to false for all devices
        for ip, device in monitored_devices.iteritems():
            monitored_devices[ip].changed = False
        
        self.update_presence(monitored_devices, active_devices)
        
        for _, device in monitored_devices.items():
            if device.changed:
#                device.toString()
                self.notify_change(device)
                
    def notify_change(self, device):
        '''
        Update Virtual device on Fibaro system and send Telegram messages
        with the changed device and status
        @param device device that changed state
        '''
        if device.type == FAMILY:
            url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                   self.config['FIBARO_VD_PRESENCE_ID'],
                                   self.config['FIBARO_VD_MAPPINGS'][device.user],
                                   device.active_toString())
            urllib.urlopen(url)        
        if (device.type == FAMILY or device.type == GUESTS):
            helper.send_telegram_message(self.config, device.user + " [" + device.active_toString() + "]")
        
    def fetch_active_devices_telnet(self):
        '''
        Fetch a list of all devices status from router. 
        @return list of found devices
        '''
#        self.logger.info("Fetch active devices from router")
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

    def fetch_active_devices(self):
        '''
        Fetch a list of all devices status from router. 
        @return list of found devices
        '''
        p = paramiko.SSHClient()
        p.set_missing_host_key_policy(paramiko.AutoAddPolicy())   # This script doesn't work for me unless this line is added!
        p.connect(self.config['ROUTER_ADRESS'], 
                  port=22, 
                  username=self.config['ROUTER_USER'], 
                  password=self.config['ROUTER_PASSWORD'])
        
        stdin, stdout, stderr = p.exec_command(self.list_active_devices_cmd)
        #p.close()
        result = stdout.readlines()
        return result
   
    def update_presence(self, monitored_devices, active_devices):
        '''
        Determine if any of the active devices in router is also
        monitored, then check device status
        '''
        for line in active_devices:
            if line.startswith("192."):
                items = line.split()
                if items[0] in monitored_devices.keys():
                    self.update_device_status(items, monitored_devices)

    def update_device_status(self, status, monitored_devices):
        '''
        Update device status of a monitored device
        @param status the status from router
        @param monitored_devices list of configured monitored devices
        '''
        device = monitored_devices[status[0]]
        #device.toString()
        previous_status = device.active
        
        if("REACHABLE" in status or "STALE" in status):
            device.active = True
            if status[4].strip() != device.mac:
                self.logger.info(device.user +"["+device.ip_adress+"] do not match received[" + status[4].strip() + "] != stored[" + device.mac+"]")
        elif "FAILED" in status:
            device.active = False
            
        if (previous_status == device.active): # No state changed
 #           self.logger.info("No change of status for device[" + status[0] + "]")
            device.changed = False
            if device.active:
                device.last_active = str(datetime.datetime.now())
        else: # State is changed
#            self.logger.info("Change of status for device[" + status[0] + "]")
            device.changed = True
            if device.active:
                device.first_active = str(datetime.datetime.now())
        #self.family_devices[status[0]] = device


    def get_announcement(self):
        '''
        Compile announcement to be read 
        '''
        announcement = ""
        for _, device in self.family_devices.items():
            announcement += device.user + " �r " + device.active_toString()+", "
        
        return helper.encode_message(announcement)
    
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
            return ReoccuringBaseService.get_html_gui(self, column_id)
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
         
        htmlresult = ["Family</br>\n"]
        
        for _,family in self.family_devices.items():
            htmlresult.append(family.user  + "["+family.active_toString()+"]</br>\n")

        htmlresult += "\nGuests</br>\n"
        for _,guests in self.guest_devices.items():
            htmlresult.append(guests.user  + "["+guests.active_toString()+"]</br>\n")
            
        htmlresult += "\nDevices</br>\n"
        for _,device in self.house_devices.items():
            htmlresult.append(device.user  + "["+device.active_toString()+"]</br>\n")

        htmlresult += "\nUnknown Devices</br>\n"
        for device in self.unknown_devices:
            htmlresult.append(str(device)+"</br>\n")
        column = column.replace("<SERVICE_VALUE>", ''.join(htmlresult))
        
        return column
                
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create('/home/pi/private_config.py')
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = AsusRouterPresenceService("",config)
    test.handle_timeout()
