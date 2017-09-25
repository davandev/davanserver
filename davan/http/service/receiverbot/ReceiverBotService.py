'''
@author: davandev
'''
# coding: utf-8
import logging
import os
import traceback
import json
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.keyboardbutton import KeyboardButton


import urllib
import re

from threading import Thread,Event
import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper_functions
import davan.util.converter_functions as converter
from davan.util import application_logger as log_manager
from davan.http.service.base_service import BaseService

logger = logging.getLogger(os.path.basename(__file__))

COMMAND, SPEAKER, TTS, SERVICES, TV, TVTEXT = range(6)

class ReceiverBotService(BaseService):
    '''
    Start a telegram bot to handle 
    Requires python-telegram-bot:
    pip install python-telegram-bot
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.RECEIVER_BOT_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        logging.getLogger('telegram.bot').setLevel(logging.CRITICAL)
        logging.getLogger('telegram.ext').setLevel(logging.CRITICAL)        
        self.current_speaker = "0"
        self.TAG_RE = re.compile(r'<[^>]+>')
        self.event = Event()
        self.bot = None
        self.handler = None

    def _parse_request(self,msg):
        self.logger.info("Parse request:" + msg)
        return msg.replace("/ReceiverBotService3=", "")
                
    def handle_request(self, msg):
        '''
        Received http request
        '''
        command = self._parse_request(msg)
        
        if command == "stop":
            self.stop_service()
        
        if command == "start":
            self.start_service()
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG
    
    def tts(self, bot, update):
        text = update.message.text.replace("/tts ", "")
        encoded_message = helper_functions.encode_message(text.encode('utf-8'))
        tts_service = self.services.get_service(constants.TTS_SERVICE_NAME)
        tts_service.start(encoded_message, self.current_speaker)
        self.increment_invoked()
        update.message.reply_text("Text message played in speaker "+ str(self.current_speaker))
        self.build_start_menu(bot, update)
        return COMMAND


    def tv(self, bot, update):
        text = update.message.text.replace("/tv ", "")
        encoded_message = helper_functions.encode_message(text.encode('utf-8'))
        url = 'http://192.168.2.173:80/web/message?text=%s&type=1&timeout=5' %encoded_message
        result = urllib.urlopen(url)
        res = result.read()
        self.increment_invoked()
        update.message.reply_text("Text message displayed on tv")
        self.build_start_menu(bot, update)
        return COMMAND
        
    def log(self, bot, update):
        file_name = log_manager.get_logfile_name()
        self.increment_invoked()
        bot.send_document(chat_id=update.message.chat_id, document=open(file_name, 'r'))
        return "Logfile sent"

    def audio(self, bot, update):
        '''
        Recieved a voice message, play it in speakers 
        '''
        self.handle_voice_message(bot, update.message)
        self.increment_invoked()
        update.message.reply_text('Voice message played in speaker ' +str(self.current_speaker))

    def stop_service(self):
        '''
        Stop telegram-bot 
        '''
        self.logger.info("Stopping service")
        try:
            self.bot.stop()
            self.event.set()
        except Exception:
            logger.error(traceback.format_exc())
#             
    def start_service(self):
        '''
        Start a telegram-bot and register command and message handlers.
        '''
        self.logger.debug("Starting telegram conversation bot")
        self.bot = Updater(token=self.config["RECEIVER_BOT_TOKEN"])
        self.bot.dispatcher.add_handler(MessageHandler(Filters.voice, self.audio))
        # Get the dispatcher to register handlers
        dp = self.bot.dispatcher
     
        # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('c', self.build_start_menu)],
     
            states={
                COMMAND: [RegexHandler('^(Services|Log|Speakers|TTS|Tv|Status)$', self.handle_command)],
                SPEAKER: [RegexHandler('^(Hallway|Kitchen|All|Menu)$', self.handle_speaker)],
                SERVICES: [RegexHandler('^(.*)$', self.handle_service)],
                TV: [RegexHandler('^(On|Off|Text|Menu)$', self.handle_tv)],
                TTS: [MessageHandler(Filters.text, self.tts)],
                TVTEXT: [MessageHandler(Filters.text, self.tv)]
            },
     
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
     
        dp.add_handler(conv_handler)
     
 
        def loop():
            self.bot.start_polling()
         
        Thread(target=loop).start()    
        return self.event.set

            
    def handle_voice_message(self, bot, message):
        '''
        A voice message is returned from Telegram, download it.
        Convert the downloaded ogg file to wav, needed since the 
        roxcore speakers cannot handle the ogg encoding.
        @param message message to play in speaker.
        '''
        ogg_file = self.config['TEMP_PATH'] + 'telegram_voice.ogg'
        file_id = message.voice.file_id
        newFile = bot.get_file(file_id)
        newFile.download(ogg_file)        
        wav_file = converter.ogg_to_wav(self.config, ogg_file)
        speaker = self.services.get_service(constants.ROXCORE_SPEAKER_SERVICE_NAME)
        speaker.handle_request(wav_file,self.current_speaker)
        return "Voice message played in speaker " + str(self.current_speaker)
    
    def build_start_menu(self, bot, update):
        '''
        Generate the start/command menu to display
        '''
        reply_keyboard = [['Status','Services', 'Log'],['TTS','Tv','Speakers']]
        
        update.message.reply_text("Select command:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
 
        return COMMAND
 
    def build_speaker_menu(self,update):
        '''
        Generate the speaker menu to display
        '''
        reply_keyboard = [['Hallway', 'Kitchen', 'All'],['Menu']]
        
        update.message.reply_text('Select speaker:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    def build_tv_menu(self,update):
        '''
        Generate the tv menu to display
        '''
        reply_keyboard = [['On', 'Off', 'Text'],['Menu']]
        
        update.message.reply_text('Select command:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    def build_service_menu(self, update):
        '''
        Generate the service menu to display
        '''
        button_list = []
        for name, service in self.services.services.iteritems():
            if service.is_enabled():
                button_list.append(KeyboardButton(name))
            
        footer = [KeyboardButton("Menu")]
        reply_keyboard = self.build_menu(button_list, 3, None, footer_buttons=footer)
        update.message.reply_text(
        'Select service:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
 
    def handle_command(self, bot, update):
        '''
        Command has been selected, perform action
        '''
        logger.info("Selected command %s" % (update.message.text))
        
        if update.message.text == "Speakers":
            self.build_speaker_menu(update)
            return SPEAKER
        
        if update.message.text == "Status":
            self.handle_status(bot, update)
            return COMMAND
        
        if update.message.text == "Log":
            file_name = log_manager.get_logfile_name()
            self.increment_invoked()
            bot.send_document(chat_id=update.message.chat_id, document=open(file_name, 'r'))
            return COMMAND
        
        if update.message.text == "TTS":
            self.handle_tts(bot, update)
            return TTS    
        
        if update.message.text == "Tv":
            self.build_tv_menu(update)
            #self.handle_tv(bot, update)
            return TV
        
        if update.message.text == "Services":
            self.build_service_menu(update)
            return SERVICES    
            
        return ConversationHandler.END    

    def handle_service(self, bot, update):
        logger.info("Selected service %s" % (update.message.text))
        
        if update.message.text == "Menu":
            self.build_start_menu(bot, update)
            return COMMAND
        for name, service in self.services.services.iteritems():
            if name == update.message.text:
                self.logger.info("Name:" + name)
                item = self.services.get_service(name)
                text = item.get_html_gui("")   
                success, error = item.get_counters()
                result = text + "\n" + "Success: " + str(success) + "\nError:" + str(error)
                self.increment_invoked()
#                update.message.reply_text(self.TAG_RE.sub('', text),reply_markup=ReplyKeyboardRemove())
                update.message.reply_text(self.TAG_RE.sub('', result))
        return SERVICES    

    def handle_status(self, bot, update):
        logger.info("Selected %s:" % (update.message.text))
        service = self.services.get_service(constants.HTML_SERVICE_NAME)
        result = json.loads(service.get_status())
        res_string = "Uptime: " + result['Uptime'] +"\n"
        res_string += "Server started: " + result['ServerStarted'] +"\n"
        res_string += "Cpu load: " + result['CpuLoad'] +"\n"
        res_string += "Disk usage : " + result['Disk'] +"\n"
        res_string += "Memory usage (used/free): " + result['Memory'] +"\n"
        
        res_string += "Services: " + result['Services']
        
        update.message.reply_text(self.TAG_RE.sub('', res_string))
        self.build_start_menu(bot, update)
        return COMMAND

    def handle_tts(self, bot, update):
        '''
        '''
        logger.info("Selected tts %s:" % (update.message.text))
        update.message.reply_text("Write message to play in speaker ", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def handle_show_text(self, bot, update):
        '''
        Display the message on Tv
        '''
        logger.info("Selected message:%s:" % (update.message.text))
        update.message.reply_text("Write message on TV", reply_markup=ReplyKeyboardRemove())
        #return TVTEXT

    def handle_tv(self, bot, update):
        '''
        A speaker has been selected
        '''
        logger.info("Selected tv-command %s:" % (update.message.text))
        if update.message.text != 'Menu':
            if update.message.text == 'On':
                update.message.reply_text("Turning on TV")
                tv = self.services.get_service("TvService")
                tv.enable(True)
                update.message.reply_text("Turned on TV ")
                self.build_start_menu(bot, update)
                return COMMAND    
            if update.message.text == 'Off':
                update.message.reply_text("Turning off TV")
                tv = self.services.get_service("TvService")
                tv.enable(False)
                update.message.reply_text("Turned off TV")
                self.build_start_menu(bot, update)
                return COMMAND    
            if update.message.text == 'Text':
                self.handle_show_text(bot,update)
                return TVTEXT 

            self.increment_invoked()


    def handle_speaker(self, bot, update):
        '''
        A speaker has been selected
        '''
        logger.info("Selected speaker %s:" % (update.message.text))
        if update.message.text != 'Menu':
            if update.message.text == 'Kitchen':
                self.current_speaker = "0"
            if update.message.text == 'Hallway':
                self.current_speaker = "1"
            if update.message.text == 'All':
                self.current_speaker = "2"

            self.increment_invoked()
            update.message.reply_text("Current speaker is now: " + update.message.text)
        self.build_start_menu(bot, update)
        return COMMAND
 
    def cancel(self, bot, update):
        logger.info("User canceled the conversation.")
 
        return ConversationHandler.END    
    
    def build_menu(self, buttons,
                   n_cols,
                   header_buttons=None,
                   footer_buttons=None):
        self.logger.info("build menu")
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return menu                

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        if not self.is_enabled():
            return BaseService.get_html_gui(self, column_id)
        
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", "<li>Monitor: " + str() + " </li>\n")
        return column


if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = ReceiverBotService(config)
    test.start_service()
