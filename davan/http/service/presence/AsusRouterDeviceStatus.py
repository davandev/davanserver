'''
Created on 11 jan. 2017
@author: davandev
'''

import logging
import os

class AsusRouterDeviceStatus(object):
    '''
    classdocs
    '''
    def __init__(self, ip_adress, user):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(os.path.basename(__file__))
        # Name of the device owner
        self.user = user
        # Ip address of device
        self.ip_adress = ip_adress
        # Is device state changed
        self.changed = False
        # Is device active == on wifi network
        self.active = False
        # Time the device was last active
        self.last_active=""
        # Time the device was first active 
        self.first_active=""
    
    def active_toString(self):
        if self.active:
            return "Hemma"
        else:
            return "Borta"          
              
    def toString(self):
        self.logger.debug("User["+self.user+"] " + 
                          "ip["+self.ip_adress+"] " + 
                          "Status["+str(self.active)+"] " +
                          "StatusChanged["+str(self.changed)+"] " +
                          "FirstActive["+self.first_active+"] " +
                          "LastActive["+self.last_active+"] ")