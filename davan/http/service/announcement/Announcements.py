'''
Created on 26 apr. 2017

@author: davandev
'''
import os
import logging
import davan.util.application_logger as app_logger
import davan.config.config_creator as config_creator
import davan.util.constants as constants
import davan.util.helper_functions as helper_functions
import urllib2
from datetime import datetime, timedelta
from datetime import *
import __builtin__

global logger
logger = logging.getLogger(os.path.basename(__file__))

global weekdays
weekdays=['m�ndag','tisdag','onsdag','torsdag','fredag','l�rdag','s�ndag',]
months=['december','januari','februari','mars','april','maj','juni','juli','augusti','september','oktober','november']
date= ['noll','f�rsta','andra','tredje','fj�rde','femte','sj�tte','sjunde','�ttonde','nionde','tionde',
       'elfte','tolfte','trettonde','fjortonde','femtonde','sextonde','sjuttonde','artonde','nittonde','tjugonde',
       'tjugof�rsta','tjugoandra','tjugotredje','tjugofj�rde','tjugofemte','tjugosj�tte','tjugosjunde',
       'tjugo�ttonde','tjugonionde','trettionde','trettif�rsta']

def create_weather_announcement(services):
    '''
    
    '''
    logger.info("Create weather announcement")
    weather = services.get_service(constants.WEATHER_SERVICE).get_announcement()
    service_data = weather.get_cache_service_data()
    if service_data == None:
        logger.warning("Cached service data is none")
        return None
    announcement = "Just nu �r det "
    announcement += str(service_data["current_observation"]["temp_c"])
    announcement += " grader ute och det k�nns som "
    announcement += str(service_data["current_observation"]["feelslike_c"]) + " grader. "
    return helper_functions.encode_message(announcement)

def create_morning_announcement():
    n = datetime.now()
    current_time = format(n,"%H:%M:%S")
    t = n.timetuple()
    y, m, d, h, min, sec, wd, yd, i = t
    current_day = wd
    
    logger.info("Create morning announcement")
    announcement = "God morgon familjen �ntligen �r det en ny dag. Idag �r det "
    announcement += str(weekdays[current_day]) + ' den '
    announcement += date[d] + " " + str(months[m]) + '. '
    logger.info("Current month:" + str(months[m]) + " day:" + str(d) + '. ')
    
    return helper_functions.encode_message(announcement)

def create_night_announcement():
    logger.info("Create night announcement")
    announcement = "Nu �r det dags att g� och l�gga sig Mia. God natt"
    
    return helper_functions.encode_message(announcement)

def create_calendar_announcement(services):
    logger.info("Create calendar announcement")
    announcement = services.get_service(constants.CALENDAR_SERVICE_NAME).get_announcement()
    return helper_functions.encode_message(announcement)

def create_quote_announcement():
    '''
    Fetch quote from dagenscitat.nu 
    @return the result
    '''
    logger.info("Fetching quote")
    quote = urllib2.urlopen("http://www.dagenscitat.nu/citat.js").read()

    quote = quote.split("<")[1]
    result = "Dagens citat "
    result += quote.split(">")[1]
    
    return helper_functions.encode_message(result)

    
    
    
    
    
    
    
    
"""    
def encode_message(message):
    '''
    Encode the quote
    '''
    logger.debug("Encoding message")
    message = message.replace(" ","%20") 
    
    message = message.replace('�','%C3%A5')
    message = message.replace('�','%C3%B6')
    message = message.replace('�','%C3%A4')

    message = message.replace('&auml;','%C3%A4')        
    message = message.replace('&aring;','%C3%A5')
    message = message.replace('&ouml;','%C3%B6')       
    logger.debug("Encoded quote:" + message)
    return message
"""
    
    
    
if __name__ == '__main__':
    config = config_creator.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    result = create_morning_announcement()
    logger.info("Quote: "+ result)