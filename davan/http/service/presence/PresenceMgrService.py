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
import davan.http.service.presence.url_helper as url_util
import davan.util.constants as constants
import davan.util.cmd_executor as cmd_executor
import time

from davan.http.service.presence.phone_status import PhoneStatus
from davan.http.service.base_service import BaseService
'''

'''
class PresenceMgrService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.PRESENCE_SERVICE_NAME, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.hping_cmd = ['sudo','/usr/sbin/hping3', '-2', '-c', '10', '-p', '5353', '-i' ,'u1','','-q']
        self.devices_cmd =['sudo','/usr/sbin/arp', '-an']#, | awk '{print $4} '"]
        self.delete_device_cmd =['sudo','/usr/sbin/arp', '-i' ,'eth0', '-d', '']

        self.users = []
        wilma = PhoneStatus("wilma","04:F1:3E:5C:79:75","192.168.2.11", iphone=True)
        self.users.append(wilma)
        david = PhoneStatus("david","64:BC:0C:4B:F6:72","192.168.2.115",iphone=True)
        self.users.append(david)
        viggo = PhoneStatus("viggo","40:40:A7:27:2C:98","192.168.2.106",iphone=True)
        self.users.append(viggo)
        mia = PhoneStatus("mia","E8:50:8B:F5:C8:8A","192.168.2.86",iphone=True)
        self.users.append(mia)
        self.event = Event()

    def handle_request(self, msg):
        msg = msg.split('?')
        res = msg[1].split('=')
        self.monitor_user(res[1])
        return 200, ""
    
    def stop_service(self):
        self.logger.info("Stopping service")
        self.event.set()

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
     
    def monitor_user(self, user_name):
        '''
        Starts monitoring user presence
        @param user, the user to monitor
        '''
        now = datetime.datetime.now()
        expire_time = now + datetime.timedelta(minutes = 7)
        self.logger.info("Got new user to monitor [" + user_name + "] New expire time:" +str(expire_time))

        for user in self.users:
            if user.user == user_name:
                user.expire_time = expire_time 

    def timeout(self):
        for user in self.users:
            user.status_changed = False
            previous_state = user.phone_status 
            
            self.logger.info("Check presence for user: [ "+ user.user +" ] Previous state [ " + str(previous_state)+ " ]")
            self.is_phone_on_wifi(user)
            self.is_phone_reporting(user)
            
            if (user.wifi_status or 
               user.reporting_status): 
                if (not previous_state):  
                    user.phone_status = True
                    user.status_changed = True
                    home_url = url_util.getUserHomeUrl(self.config, user.user)
                    urllib.urlopen(home_url)
            
            elif (not user.reporting_status and 
                  not user.wifi_status): 
                if previous_state:
                    user.phone_status = False
                    user.status_changed = True
                    away_url = url_util.getUserAwayUrl(self.config, user.user)
                    urllib.urlopen(away_url)

            user.toString()
        self.logger.info("-------------------------------------------------")
                        
    def is_phone_on_wifi(self,user):
        self.hping_cmd[9] = user.ip_adress
        cmd_executor.execute_block(self.hping_cmd, "hping", True)            
        time.sleep(3)
        result = cmd_executor.execute_block(self.devices_cmd, "devices", True)

        if user.mac_adress in result:
            if user.wifi_status:
                user.wifi_last_active = str(datetime.datetime.now())
            else:
                user.set_wifi_status(True)
                user.wifi_first_active = str(datetime.datetime.now())
                
            if user.has_iphone: #Special case for Iphone users, 
                now = datetime.datetime.now()
                expire_time = now + datetime.timedelta(minutes = 60)
                self.logger.info("User["+user.user+"] has iphone increase expire time to "+ str(expire_time) + " Current time:" + str(now))
                user.expire_time = expire_time 
                
                
            self.delete_device_cmd[5] = user.ip_adress 
            cmd_executor.execute_block(self.delete_device_cmd, "delete_device", True)
            cmd_executor.execute_block(self.hping_cmd, "hping", True)
                
        else:
            if user.wifi_status:
                user.set_wifi_status(False)
        
        
    def is_phone_reporting(self, user):
        '''
        Timeout received, check if any user is now away, 
        then inform fibaro system about it.
        '''

        current_time = datetime.datetime.now()
        if user.expire_time > current_time:
            if user.reporting_status:
                user.reporting_last_active = str(current_time)
            else:
                user.set_reporting_status(True)
                user.reporting_first_active = str(current_time)

        else:
            if user.reporting_status:
                user.set_reporting_status(False)

                
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=3)
    
    test = PresenceMgrService()
    test.monitor_user("david")
