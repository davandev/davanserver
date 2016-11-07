"""
"""
#!/bin/env python
import logging
import os
import time
from BaseHTTPServer import BaseHTTPRequestHandler
from socket import gethostname
from SocketServer import ThreadingMixIn
import socket
import BaseHTTPServer
import httplib
import cgi
import argparse
import mimetypes
import traceback
import signal
import sys
import __builtin__

import davan.util.application_logger as log_manager
import davan.config.config_creator as config_factory
import davan.util.helper_functions as helper

from davan.http.ServiceInvoker import ServiceInvoker
global services

global logger
logger = logging.getLogger(os.path.basename(__file__))

class RunningServerException(Exception):
    """
    Exception raised when an existing distribution server is discovered on the host
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# Custom handler to handle http requests received in server.
class CustomRequestHandler(BaseHTTPRequestHandler):
    """
    Request handler that handles incoming requests.
    """

    def do_POST(self):
        """
        Handles POST requests.
        """
        try:
            logger.info("Received POST request for image from external host : " + self.address_string())

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            postvars = {}
            self.send_error(404, 'File Not Found: %s' % self.path)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_GET(self):
        '''
        Handle GET requests
        '''
        try:
            global services
            service = services.get_service(self.path)
            if not service == None:
                mimetype = 'text/html'
                if self.path.endswith(".css"):
                    mimetype ="text/css"
                
                result_code, result = service.handle_request(self.path)
                
                if result_code is not None:         
                    self.send_response(result_code)
                else:
                    self.send_response(200)
                    
                self.send_header('Content-type',    mimetype)
                self.end_headers()
                if result is not None:
                    self.wfile.write(result)
                return
            
# Another server is started, terminate this one.
            elif self.path.endswith("seppuku"):
                    if __builtin__.davan_services.is_running():
                        logger.info("Shutting down services")
                        __builtin__.davan_services.stop_services()
                        self.send_response(200)
                        self.send_header('Content-type',    'text/html')
                        self.end_headers()
                        self.wfile.write("hai")
                    else:
                        logger.info("Shutting down server")
                        self.send_response(200)
                        self.send_header('Content-type',    'text/html')
                        self.end_headers()
                        self.wfile.write("hai")
                        self.server.socket.close()
            else:
                self.send_error(404, 'File Not Found: %s' % self.path)

            return

        except :
            logger.error(traceback.format_exc())
            service.increment_errors()
            self.send_error(404, 'File Not Found: %s' % self.path)

    def log_message(self, format, *args):
        return


class ApplicationServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass
# Send a request to running server to shutdown.
def _tear_down_running_server(config):
    """
    Sends a request to an distribution server running on the same host 
    requesting it to shutdown.
    @param port: The port where to send the tear down request.
    """
    logger.debug("Tear down existing server on [" + config["SERVER_ADRESS"] + "]" +
                 " port[" + str(config["SERVER_PORT"]) + "]")

    conn1 = httplib.HTTPConnection(config["SERVER_ADRESS"] + ":" + str(config["SERVER_PORT"]))
    conn1.request("GET", "/seppuku")
    r1 = conn1.getresponse()
    response_msg = r1.read()
    if response_msg == "hai":
        conn1.request("GET", "/seppuku")
        r1 = conn1.getresponse()
        response_msg = r1.read()


# Try to start the server, return exception if an
# instance is already running
def start_server(configuration):
    """
    Starts the server on the provided port.
    @param port: The port that the server listens to
    """
    try:
        global services
        services = ServiceInvoker(config)
        services.discover_services()
        services.start_services()
        # ugly way to share services
        __builtin__.davan_services = services
        server = ApplicationServer(('', config["SERVER_PORT"]), CustomRequestHandler)
        helper.debug_big("Server started on host port[" + str(config["SERVER_PORT"]) + "] ")        
        while 1:
            server.handle_request()
            if not __builtin__.davan_services.is_running():
                server.server_close()
                logger.warning("Services has been stopped")
                sys.exit(1)
        
    except socket.error, (value, message):
        if value == 98:  # Address port already in use
            logger.debug("Failed to start server with message" +
                         " [" + message + "]")

            raise RunningServerException("Port is already in use")

    
def _parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start",
                    help="Start server",
                    action="store_true")
    parser.add_argument("-o", "--stop",
                    help="Stop server",
                    action="store_true")
    parser.add_argument("-d","--debug",
                    help="Enable debug",
                    action="store_true",
                    default=False) 
    parser.add_argument("-p","--privateconfig",
                    help="Configuration file with private data",
                    action="store",
                    default="/home/pi/private_config.py") 
    args = parser.parse_args()
    return args

def handler(signum, frame):
    logger.info("Caught Ctrl+c, stopping server")
    global services
    services.stop_services()    
    sys.exit(1)

if __name__ == '__main__':
    args = _parse_arguments() 
    config = config_factory.create(args.privateconfig)
    if args.debug: 
        #log_manager.start_file_logging(config["LOGFILE_PATH"])

        helper.debug_formated(config)
        
        log_manager.start_logging(config["LOGFILE_PATH"],loglevel=4)
    else:
        log_manager.start_logging(config["LOGFILE_PATH"],loglevel=0)

    

    try:
        if args.stop:
            _tear_down_running_server(config)
            logger.debug("Shutting down existing server")
            exit(1)
        else:
            signal.signal(signal.SIGINT, handler)
            start_server(config)
    except RunningServerException:  # Running server found
        if _tear_down_running_server(config):
            time.sleep(2)  # wait for running server to shutdown
            start_server(config)
        else:
            logger.error("Failed to terminate the running server")
    except socket.error:
        logger.error("Server not running")


