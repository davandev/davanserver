# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import __builtin__
import logging
import os
import time
import re
import traceback

import davan.util.cmd_executor as cmd
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.http.service.base_service import BaseService
from davan.http.service.audio.AudioService import AudioService
from davan.util import application_logger as log_config

class HtmlService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.HTML_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        
        self.start_date = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        self.expression = re.compile('<(.*?)object')
   
    def handle_request(self, msg):
        '''
        Received html request.
        '''
        self.logger.debug("Received html request: [" + msg + "}")
        self.increment_invoked()

        if ("applicationserver.log" in msg):
            logfile = msg.replace(".html","")
            self.logger.info("Logfile: "+ self.config['LOGFILE_PATH'] + " File "+ logfile)
            f = open(self.config['LOGFILE_PATH'] + logfile) 
            content = f.read()
            content = content.replace("\n","<br>")
        elif (msg == "/index.html"):
            f = open(self.config["HTML_INDEX_FILE"])
            content = f.read()
            f.close()
            result = self.generate_service_fragment()
            content = content.replace("<SERVICES>", result)
            content = self.get_server_info(content)
        elif (msg == "/select_logfile.html"):
            f = open(self.config["HTML_SELECT_LOGFILE"])
            content = f.read()
            f.close()
        
        elif (msg == "/style.css"):
            f = open(self.config["HTML_STYLE_FILE"])
            content = f.read()
            f.close()
            return constants.RESPONSE_OK, constants.MIME_TYPE_CSS, content

        elif (msg == "/logfiles.html"):
            content = self.get_logfiles()
        elif (msg == "/reboot.html"):
            content = "Server restarting"
        elif (msg == "/statistics.html"):
            content = self.get_statistics()
        elif (msg == "/status.html"):
            content = self.get_status()
           
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, content
    
    def generate_service_fragment(self):
        '''
        Iterate all services, generate and return the services page 
        '''
        try:
            column_id = 1
            tot_result = ""
            for name, service in __builtin__.davan_services.services.iteritems():
    #            if service.has_html_gui():
                if column_id == 1:
                    tot_result += '<div id="columns">\n'
                        
                tot_result += service.get_html_gui(column_id)
                column_id += 1
                if column_id == 4:
                    tot_result += '<div style="clear: both;"> </div></div>\n' 
                    column_id = 1
    
            tot_result += '<div style="clear: both;"> </div></div>\n' 
            return tot_result 
        except :
            self.logger.error(traceback.format_exc())        
    
    def get_logfiles(self):
        """
        Return the content of the current logfile
        """
        f = open(self.config['SERVICE_PATH'] + "html/log_file_template.html")
        content = f.read()
        f.close()

        options = ""
        for logfile in os.listdir(self.config["LOGFILE_PATH"]):
            if "applicationserver" in logfile:
                options +='<option value="http://192.168.2.50:8080/' + logfile + '.html">' + logfile + '</option>'
        content = content.replace("<OPTIONS_LOGFILES>", options)
        return content 
    
    def get_statistics(self):
        """
        Return statistics of running services
        """
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
    
    def get_server_info(self, content):
        '''
        Return information/statistics about server
        '''
        content = content.replace('<SERVER_STARTED_VALUE>', self.start_date)
        result = (cmd.execute_block("uptime", "uptime", True)).split()
        content = content.replace('<UPTIME>', result[2] + " " + result[3])
        content = content.replace('<CPU_VALUE>', result[9])
        result = (cmd.execute_block("df -hl | grep root", "memory usage", True)).split()
        content = content.replace('<DISK_VALUE>', result[4] + " ( Free " + result[3] + " )")
        
        content = content.replace('<RUNNING_SERVICES_VALUE>', str(len(__builtin__.davan_services.services.items()))) 
        return content
    
    def get_status(self):
        '''
        Return the status of the server.
        @return: status json formatted
        '''
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
    from davan.http.service.tts.TtsService import RoxcoreService
    from davan.http.service.ups.UpsService import UpsService
    from davan.http.service.dailyquote.DailyQuoteService import DailyQuoteService
    from davan.http.service.speedtest.SpeedtestService import SpeedtestService
    from davan.http.service.keypad.KeypadAliveService import KeypadAliveService
    from davan.http.service.monitor.ActiveScenesMonitorService import ActiveScenesMonitorService
    from davan.http.service.picture.PictureService import PictureService
    from davan.http.service.weather.WeatherService import WeatherService
    
    config = configuration.create()
    service = ServiceInvoker(config)
    service.services['A'] = AudioService(config)
    service.services['B'] = RoxcoreService(config)
    service.services['C'] = UpsService(config)
    service.services['D'] = DailyQuoteService(config) 
    service.services['D'] = SpeedtestService(config)
    service.services['E'] = KeypadAliveService(config)
    service.services['F'] = ActiveScenesMonitorService(config)
    service.services['F'] = PictureService(config)
    service.services['G'] = WeatherService(config)

    __builtin__.davan_services = service

    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = HtmlService(config)
    test.generate_service_fragment()
    #test.handle_request("/status.html")
