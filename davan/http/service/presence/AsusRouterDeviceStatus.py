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
        self.user = user
        self.ip_adress=ip_adress
        
        self.changed = False
        self.active = False
        self.last_active=""
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