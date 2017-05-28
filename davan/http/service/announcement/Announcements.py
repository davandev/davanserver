#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
@author: davandev
'''
import os
import logging
import davan.util.application_logger as app_logger
import davan.config.config_creator as config_creator
import davan.util.helper_functions as helper_functions
import urllib2
from datetime import datetime, timedelta
from datetime import *

global logger
logger = logging.getLogger(os.path.basename(__file__))

global weekdays
weekdays=['måndag','tisdag','onsdag','torsdag','fredag','lördag','söndag',]
months=['december','januari','februari','mars','april','maj','juni','juli','augusti','september','oktober','november']
date= ['noll','första','andra','tredje','fjärde','femte','sjätte','sjunde','åttonde','nionde','tionde',
       'elfte','tolfte','trettonde','fjortonde','femtonde','sextonde','sjuttonde','artonde','nittonde','tjugonde',
       'tjugoförsta','tjugoandra','tjugotredje','tjugofjärde','tjugofemte','tjugosjätte','tjugosjunde',
       'tjugoåttonde','tjugonionde','trettionde','trettiförsta']

def create_morning_announcement():
    n = datetime.now()
    #current_time = format(n,"%H:%M:%S")
    t = n.timetuple()
    y, m, d, h, min, sec, wd, yd, i = t
    current_day = wd
    
    logger.info("Create morning announcement")
    announcement = "God morgon familjen äntligen är det en ny dag. Idag är det "
    announcement += str(weekdays[current_day]) + ' den '
    announcement += date[d] + " " + str(months[m]) + '. '
    logger.info("Current month:" + str(months[m]) + " day:" + str(d) + '. ')
    
    return helper_functions.encode_message(announcement)

def create_night_announcement():
    '''
    
    '''
    logger.info("Create night announcement")
    announcement = "Nu är det dags att gå och lägga sig Mia. God natt"
    
    return helper_functions.encode_message(announcement)

def create_water_announcement():
    '''
    
    '''
    logger.info("Create water announcement")
    announcement = "Kom ihåg att vattna blommorna och häcken"
    
    return helper_functions.encode_message(announcement)

def create_name_announcement():
    logger.info("Create name announcement")
    announcement = "Dagens namnsdagsbarn "
    
    encoded_result = urllib2.urlopen("http://www.dagensnamn.nu/").read()
    
    start_index = encoded_result.index("text-vertical-center")
    stop_index = encoded_result.index("....namnsdag")
    nr_of_char = stop_index-start_index 
    index_res = encoded_result[start_index:(start_index+nr_of_char)]

    start_index = encoded_result.index("margin-bottom:20px;")
    stop_index = encoded_result.index("</h1>")
    nr_of_char = stop_index-start_index 
    announcement += encoded_result[start_index+len('margin-bottom:20px;">'):(start_index+nr_of_char)]
    
    return helper_functions.encode_message(announcement+".")
    
if __name__ == '__main__':
    config = config_creator.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    result = create_name_announcement()
    logger.info("Quote: "+ result)