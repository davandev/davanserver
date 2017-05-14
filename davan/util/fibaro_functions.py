'''
Created on 1 maj 2017

@author: Wilma
'''
import urllib
import json

def is_alarm_armed(config):
    '''
    Check if alarm is armed
    @return True if alarm is armed, False otherwise
    '''
    result = urllib.urlopen(config['FIBARO_API_ADDRESS'] + "globalVariables")
    res = result.read()
    data = json.loads(res)
    
    alarm = False 
    armed = False
    for items in data:
        if items["name"] =="AlarmState" and items["value"] == "Armed":
            armed = True
        if items["name"] =="AlarmType" and items["value"] == "Alarm":
            alarm = True
    if alarm and armed:
        return True 
    return False
