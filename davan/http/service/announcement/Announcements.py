#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
@author: davandev
'''
import os
import logging
import traceback
import urllib2

import davan.util.application_logger as app_logger
import davan.config.config_creator as config_creator
import davan.util.helper_functions as helper_functions

from datetime import datetime, timedelta
from datetime import *
from astral import Astral

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
    t = n.timetuple()
    y, m, d, h, min, sec, wd, yd, i = t
    current_day = wd
    
    logger.info("Create morning announcement")
    announcement = "God morgon familjen äntligen är det en ny dag. Idag är det "
    announcement += str(weekdays[current_day]) + ' den '
    announcement += date[d] + " " + str(months[m]) + '. '
    logger.debug("Current month [" + str(months[m]) + "] Day [" + str(d) + ']')
    
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

def create_sunset_sunrise_announcement():
    announcement = ""
    try:
        city_name = 'Stockholm'
        a = Astral()
        a.solar_depression = 'civil'
        city = a[city_name]
        sun = city.sun(date=datetime.now(), local=True)
    
        announcement = "Solens upp och nedgång idag."
    
        dawn = get_hour_and_minute(str(sun['dawn']))
        announcement += "Gryning klockan " + dawn + "."
    
        sunrise = get_hour_and_minute(str(sun['sunrise']))
        announcement += "Soluppgång klockan " + sunrise + "."
        
        sunset = get_hour_and_minute(str(sun['sunset']))
        announcement += "Solnedgång klockan " + sunset + "."
        
        dusk = get_hour_and_minute(str(sun['dusk']))
        announcement += "Skymning klockan " + dusk + "."
    except:
        logger.error(traceback.format_exc())
    return helper_functions.encode_message(announcement)

def get_hour_and_minute(dateitem):    
    dateitem = dateitem.split(" ")[1]
    dateitem= dateitem.split(":")
    return dateitem[0] +":" + dateitem[1]
    
def create_name_announcement():
    logger.info("Create name announcement")
    announcement = ""
    try:
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
    except:
        logger.error(traceback.format_exc())
        
    return helper_functions.encode_message(announcement+".")
    
def create_menu_announcement(config):
    '''
    Create menu announcement, a text file contains all daily menus
    Determine current date and read date from menu file.
    '''
    logger.debug("Create menu announcement")
    menu = ""
    try:
        n = datetime.now()
        t = n.timetuple()
        y, m, d, h, min, sec, wd, yd, i = t
        
        if wd >=5:
            logger.info("Weekend no menu")
            return ""
    
        todays_date = str(d) + "/" + str(m)
        logger.debug("today:" + todays_date)
        with open(config['ANNOUNCEMENT_MENU_PATH']) as f:
            content = f.readlines()
            for line in content:
                if line.startswith(todays_date):
                    logger.debug("Found todays menu: " + todays_date +": " + line)
                    menu = "Meny i Neptuniskolan. "
                    menu += line.replace(todays_date, "")
                    menu = menu.rstrip()
                    menu += "."
    except:
        logger.error(traceback.format_exc())

    return helper_functions.encode_message(menu)
                
if __name__ == '__main__':
    config = config_creator.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    result = create_menu_announcement()
    logger.info("Menu: "+ result)