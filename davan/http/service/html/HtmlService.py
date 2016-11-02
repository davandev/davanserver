# -*- coding: utf-8 -*-
'''
Created on 8 feb. 2016

@author: davandev
'''
import logging
import os
import time
import json
import urllib2
import re
import davan.util.cmd_executor as cmd
import davan.config.config_creator as configuration
from davan.http.service.base_service import BaseService
import __builtin__
from davan.http.ServiceInvoker import ServiceInvoker
from davan.http.service.audio.AudioService import AudioService
from davan.util import application_logger as log_config
import davan.util.constants as constants

class HtmlService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, "HtmlService", config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.start_date = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
        self.expression = re.compile('<(.*?)object')
   
    def handle_request(self, msg):
        '''
        Received request for html statistics.
        '''
        self.logger.debug("Received html request: [" + msg + "}")
        self.increment_invoked()
        if (msg == "/index.html"):
            f = open(self.config["HTML_INDEX_FILE"])
            content = f.read()
            f.close()
            content = self.getServerInfo(content)
            content = self.getDailyQuote(content)
            content = self.getUpsInfo(content)
            content = self.getInternetInfo(content)
            content = self.getWeatherInfo(content)
        
        elif (msg == "/style.css"):
            f = open(self.config["HTML_STYLE_FILE"])
            content = f.read()
            f.close()
        
        elif (msg == "/logfile.html"):
            content = self.get_logfile()
        elif (msg == "/reboot.html"):
            content = "Server restarting"
        elif (msg == "/statistics.html"):
            content = self.get_statistics()
        elif (msg == "/status.html"):
            content = self.getStatus()
           
        return 200, content
    
    def get_logfile(self):
        logfile = log_config.get_logfile_name()
        self.logger.info("LogFile:" + logfile)   
        f = open(logfile)
        content = ""
        for line in f.readlines():
            content += line + "</br>"
        f.close()
        return content 
    
    def get_statistics(self):
        self.logger.info("Statistics")
        f = open(self.config["HTML_STATISTICS_FILE"])
        content = f.read()
        stat= constants.HTML_TABLE_START
        for key, value in __builtin__.davan_services.services.iteritems():
            service = self.expression.findall(str(value))[0]
            service_name = service.split(".")[0]
            success, error = value.get_counters()
            stat += "<tr><th>" + str(service_name) + "</th><th>" + str(success) + "</th><th>" + str(error) + "</th></th>"  
        stat += constants.HTML_TABLE_END
        content = content.replace("<SERVICES_STATISTICS_VALUE>", stat)
        return content
    
    def getWeatherInfo(self, content):
        result = urllib2.urlopen(self.config["WUNDERGROUND_PATH"]).read()
        data = json.loads(result)
        htmlresult = "<li>Temp: " + str(data["current_observation"]["temp_c"]) + "</li>\n"
        htmlresult += "<li>Humidity: " + str(data["current_observation"]["relative_humidity"]) + " </li>\n"
        htmlresult += "<li>Pressure: " + str(data["current_observation"]["pressure_mb"]) + " bar </li>\n"
        htmlresult += "<li>Feels like: " + str(data["current_observation"]["feelslike_c"]) + " </li>\n"
        htmlresult += "<li>Rain: " + str(data["current_observation"]["precip_today_metric"]) + " mm</li>\n"
        htmlresult += "<li>Wind dir: " + str(data["current_observation"]["wind_dir"]) + " </li>\n"
        htmlresult += "<li>Wind degree: " + str(data["current_observation"]["wind_degrees"]) + " </li>\n"
        htmlresult += "<li>Time: " + str(data["current_observation"]["observation_time_rfc822"]) + " </li>\n"
        content = content.replace("<WEATHER_SERVICE_VALUE>", htmlresult)
        return content

    def getUpsInfo(self, content):
        from davan.http.service.ups.UpsService import UpsService
        _, result = __builtin__.davan_services.services['Ups'].handle_request("Status")
        data = json.loads(result)
        htmlresult = "<li>Status: " + data["Status"] + "</li>\n"
        htmlresult += "<li>Load: " + data["Load"] + " </li>\n"
        htmlresult += "<li>Battery: " + data["Battery"] + " </li>\n"
        htmlresult += "<li>Time: " + data["Time"] + " </li>\n"
        content = content.replace("<UPS_SERVICE_VALUE>", htmlresult)
        return content

    def getInternetInfo(self, content):
        
        _, result = __builtin__.davan_services.services['speedtest'].handle_request("speedtest")
        data = json.loads(result)
        htmlresult = "<li>Ping: " + str(data["Ping_ms"]) + " ms</li>\n"
        htmlresult += "<li>Download: " + str(data["Download_Mbit"]) + " Mbit</li>\n"
        htmlresult += "<li>Upload: " + str(data["Upload_Mbit"]) + " Mbit</li>\n"
        htmlresult += "<li>Date: " + data["Date"] + " </li>\n"
        content = content.replace("<INTERNET_SERVICE_VALUE>", htmlresult)
        return content
    
    def getDailyQuote(self, content):
        from davan.http.service.dailyquote.DailyQuoteService import DailyQuoteService
        quote = __builtin__.davan_services.services['DailyQuote'].fetch_quote()
        content  = content.replace("<DAILY_QUOTE_VALUE>", quote)
        return content
    
    def getServerInfo(self, content):
        content = content.replace('<SERVER_STARTED_VALUE>', self.start_date)
        result = (cmd.execute_block("uptime", "uptime", True)).split()
        self.logger.info(str(result))
        
        content = content.replace('<UPTIME>', result[2] + " " + result[3])
        content = content.replace('<CPU_VALUE>', result[9])
        result = (cmd.execute_block("df -hl | grep root", "memory usage", True)).split()
        content = content.replace('<DISK_VALUE>', result[4] + " ( Free " + result[3] + " )")
        
        self.logger.info(str(result))
         
        self.logger.info(str(__builtin__.davan_services.services))
        running_services = ""
        for key, value in __builtin__.davan_services.services.iteritems():
            service = self.expression.findall(str(value))[0]
            service_name = service.split(".")[0]

            running_services += str(service_name) + "</br>"
        content = content.replace('<RUNNING_SERVICES_VALUE>', running_services) 
        return content
    
    def getStatus(self):
        result = (cmd.execute_block("uptime", "uptime", True)).split()
        uptime = result[2] + " " + result[3]
        cpuload = result[9]
        result = (cmd.execute_block("df -hl | grep root", "memory usage", True)).split()
        memory = result[4] + " ( Free " + result[3] + " )"
        services = len(__builtin__.davan_services.services.keys())
        json_string = '{"Uptime": "'+uptime+'", "ServerStarted":"'+str(self.start_date)+'","CpuLoad":"'+cpuload+'", "Disk":"'+memory+'", "Services":"'+str(services)+'"}'
        return json_string
    
if __name__ == '__main__':
    from davan.http.ServiceInvoker import ServiceInvoker
    from davan.http.service.tts.TtsService import TtsService
    config = configuration.create()
    service = ServiceInvoker(config)
    service.services['A'] = AudioService(config)
    service.services['B'] = TtsService(config)
    __builtin__.davan_services = service

    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = HtmlService(config)
    test.handle_request("/index.html")
