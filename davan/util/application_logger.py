import logging.handlers
import os
import time
import inspect

levels = [('CRITICAL' , logging.CRITICAL),
          ('ERROR' , logging.ERROR),
          ('WARNING' , logging.WARNING),
          ('INFO' , logging.INFO),
          ('DEBUG' , logging.DEBUG)]

def start_file_logging(log_file_path, log_file_name =""):
    """
    Starts logging to a specific file. 
    """
    if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)

    if not log_file_name:
        log_file_name = get_caller_name()

    logfile = log_file_path + '/' + log_file_name + '_' + time.strftime("%Y-%m-%d_%H%M%S", time.gmtime()) + '.log'
    masterLog = logging.getLogger('')
    masterLog.setLevel(logging.DEBUG)
    masterHandler = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(name)-35s %(levelname)-8s %(message)s')
    masterHandler.setFormatter(formatter)
    logging.getLogger('').addHandler(masterHandler)

def stop_file_logging(file_name):
    """
    Stop logging to the file file_name, by 
    removing the filehandler.  
    """
    for handler in logging.root.handlers[:]:
        if isinstance(handler, logging.FileHandler ):
            if os.path.basename(handler.baseFilename) == file_name:
                logging.root.removeHandler(handler)
                return

def stop_logging():
    """
    Stop all logging, by removing all handlers
    """
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


def start_logging(log_file_path, debug=True, loglevel=4, log_file_name=""):
    if loglevel < 0 or loglevel > 5 :
        loglevel = 4
    if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)
    if not log_file_name:
        log_file_name = get_caller_name()

    logfile = log_file_path + '/' + log_file_name + '_' + time.strftime("%Y-%m-%d_%H%M%S", time.gmtime()) + '.log'
    logging.basicConfig(level=levels[loglevel][1],
                    format='%(asctime)s %(name)-35s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=logfile,
                    filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(levels[loglevel][1])

    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-35s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    logger = logging.getLogger(os.path.basename(__file__))
    logger.info('Logging configuration: Console['+ levels[loglevel][0] +'] File[VERBOSE] Logfile[' + logfile + ']')    
    
def get_caller_name():
    """
    Returns the filename of the calling module.
    """
    _, filename, _, _, _, _ =\
        inspect.getouterframes(inspect.currentframe())[2]
    log_file_name = os.path.splitext(os.path.basename(filename))[0]
    return log_file_name

def get_logfile_name():
    return logging.getLoggerClass().root.handlers[0].baseFilename