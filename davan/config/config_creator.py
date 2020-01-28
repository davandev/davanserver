"""
Creates the config data used by services.

@author: Davandev
"""

import davan.util.helper_functions as common
import os
import imp

def create_config(secret_config, config):

    #------------------------------------------------------------------------------------------------
    # General server configuration
    #------------------------------------------------------------------------------------------------
    # CRITICAL=0, ERROR,WARNING,INFO,DEBUG=4
    config["LOGLEVEL"]      = 4
    # Root path of server
    config["ROOT"]          = '/share/davanserver/'
    # Log directory path
    config['LOGFILE_PATH']  = config["ROOT"] + "logs"
    config['TEMP_PATH']     = config["ROOT"] + "temp"
    # Service directory path
    config['SERVICE_PATH']  = config["ROOT"] + "davan/http/service/"
    # Server port
    config["SERVER_PORT"]   = 8080
    config["SERVER_ADRESS"] = "192.168.2.50"

    #---------------------------------------------------------------------------------------------
    # Fibaro configuration
    #---------------------------------------------------------------------------------------------
    config['FIBARO_USER_NAME']   = secret_config.FIBARO_USER
    config['FIBARO_PASSWORD']    = secret_config.FIBARO_PASSWORD
    config['FIBARO_IP_ADDRESS']  = "192.168.2.54"

    #---------------------------------------------------------------------------------------------
    # Fibaro path for common functions
    # --------------------------------------------------------------------------------------------
    # Fibaro api access path
    config['FIBARO_API_ADDRESS'] = "http://" + config['FIBARO_USER_NAME'] + ":" + config['FIBARO_PASSWORD'] + "@" + config['FIBARO_IP_ADDRESS'] + "/api/"
    # Set property in a virtual device
    config['UPDATE_DEVICE'] = config['FIBARO_API_ADDRESS'] + "callAction?deviceID=<DEVICEID>&name=setProperty&arg1=<LABELID>&arg2=<VALUE>"
    # Press button on virtual device
    config['VD_PRESS_BUTTON_URL'] =  config['FIBARO_API_ADDRESS'] + "callAction?deviceID=<ID>&name=pressButton&arg1=<BUTTONID>"
    # Get state of a scene
    config['GET_STATE_SCENE_URL'] = config['FIBARO_API_ADDRESS'] + "scenes/<ID>"
    # Command to start a scene
    config['START_SCENE_URL'] = config['FIBARO_API_ADDRESS'] + "sceneControl?id=<ID>&action=start"
    # Command to set a value on a device (dimmer)
    config['DEVICE_SET_VALUE_WITH_ARG_URL'] =  config['FIBARO_API_ADDRESS'] + "callAction?deviceID=<ID>&name=setValue&arg1=<VALUE>"
    config['DEVICE_SET_VALUE_URL'] =  config['FIBARO_API_ADDRESS'] + "callAction?deviceID=<ID>&name=<VALUE>"


    #-----------------------------------------------------------------------------------------
    # Logreceiver configuration
    #-----------------------------------------------------------------------------------------
    config["LogEntryEnabled"] = True

    # Log directory path
    config['HC2LOG_PATH'] = config["LOGFILE_PATH"] + "/hc2"
    
    #---------------------------------------------------------------------------------------------
    # Telegram configuration
    #---------------------------------------------------------------------------------------------
    # Telegram chat id, stored in a dict 
    config['CHATID'] = secret_config.TELEGRAM_CHATID
    # Telegram token
    config['TOKEN'] = secret_config.TELEGRAM_TOKEN
    # Telegram api path for sending messages
    config['TELEGRAM_PATH'] = "https://api.telegram.org/bot"+config['TOKEN']+"/sendMessage?chat_id=<CHATID>&text="
    
    #---------------------------------------------------------------------------------------------    
    # Outdoor camera configuration
    #---------------------------------------------------------------------------------------------
    config["TakePictureEnabled"] = True
    config['CAMERAS'] = {'Balkong':'http://192.168.2.119:99/snapshot.cgi/snapshot.cgi',
                         'Uterum':'http://192.168.2.76:99/snapshot.cgi/snapshot.cgi',
                         'Farstukvist':'http://192.168.2.172/tmpfs/snap.jpg'}
    # Username used when accessing cameras
    config['CAMERA_USER'] = secret_config.CAMERA_USER
    # Password used when accessing cameras
    config['CAMERA_PASSWORD'] = secret_config.CAMERA_PASSWORD
    
    #---------------------------------------------------------------------------------------
    # Presence Service configuration
    #---------------------------------------------------------------------------------------
    config["presenceEnabled"] = False
    # Scene ids for each user
    config['MIA_AWAY_SCENE_ID'] = "13"
    config['MIA_HOME_SCENE_ID'] = "12"
    config['DAVID_AWAY_SCENE_ID'] = "10"
    config['DAVID_HOME_SCENE_ID'] = "9"
    config['WILMA_AWAY_SCENE_ID'] = "15"
    config['WILMA_HOME_SCENE_ID'] = "14"
    config['VIGGO_HOME_SCENE_ID'] = "16"
    config['VIGGO_AWAY_SCENE_ID'] = "17"

    #---------------------------------------------------------------------------------------
    # Asus router presence Service configuration
    #---------------------------------------------------------------------------------------
    config["DevicePresenceServiceEnabled"] = True
    config["ROUTER_ADRESS"] = "192.168.2.1"
    config["ROUTER_USER"] = secret_config.ROUTER_USER
    config["ROUTER_PASSWORD"] = secret_config.ROUTER_PASSWORD
    # Virtual device id of the virtual device in HC2 that shows the presence of the users 
    config['FIBARO_VD_PRESENCE_ID'] = "75"
    # Mappings of users and the label in the presense virtual device
    config['FIBARO_VD_MAPPINGS'] = {
      # User    : HC2 Virtualdevice ID
        'Wilma' : 'ui.Label3.value',
        'David' : 'ui.Label1.value',
          'Mia' : 'ui.Label2.value',
        'Viggo' : 'ui.Label4.value' }

    # Ipadresses of devices where its wifi presence should be monitored
    config['FAMILY_DEVICES'] = secret_config.DEVICES_FAMILY
    config['GUEST_DEVICES'] = secret_config.DEVICES_FRIEND
    config['HOUSE_DEVICES'] = secret_config.DEVICES_HOUSE
    config['UNKNOWN_DEVICES'] = secret_config.DEVICES_UNKNOWN
#---------------------------------------------------------------------------------------
    # Authentication configuration  98:00:c6:32:85:30
    #---------------------------------------------------------------------------------------
    config["authenticateEnabled"] = False

    config['disarmAlarm'] = config['FIBARO_API_ADDRESS'] + "sceneControl?id=36&action=start"
    config['disarmSkalskydd'] = config['FIBARO_API_ADDRESS'] + "sceneControl?id=38&action=start"
    config['armSkalskydd'] = config['FIBARO_API_ADDRESS'] + "sceneControl?id=34&action=start"
    config['armAlarm'] = config['FIBARO_API_ADDRESS'] + "sceneControl?id=35&action=start"
    
    # User pin codes    
    config['USER_PIN'] = secret_config.USER_PIN

    #---------------------------------------------------------------------------------------------
    # Telldus sensor configuration
    #---------------------------------------------------------------------------------------------
    config["TelldusSensorServiceEnabled"] = True
    config["telldusEnabled"] = True
    # Telldus public key
    config["TELLDUS_PUBLIC_KEY"] = secret_config.TELLDUS_PUBLIC_KEY
    # Telldus private key
    config["TELLDUS_PRIVATE_KEY"] =  secret_config.TELLDUS_PRIVATE_KEY
    # Dict holding name of room and virtual device id
    config['SENSOR_MAP'] = {
               # Room name : HC2 Virtualdevice ID 
                  'Badrum' :  '147', 
               'Tvattstuga':  '220',
                   'Garage':  '149',
               'Gillestuga':  '153',
              'Farstukvist':  '152',
                   'Sovrum':  '151',
                    'Wilma':  '150' }
    
    config['SENSOR_HUMIDITY_LIMITS'] = {'Badrum': 60, 'Tvattstuga': 60}
    config['SENSOR_TEMP_HIGH_LIMITS'] = {}
    config['SENSOR_TEMP_LOW_LIMITS'] = {}
    # Temperature virtual devices 
    config['LABEL_TEMP'] = "ui.Label1.value"
    config['LABEL_HUMIDITY'] = "ui.Label2.value"
    config['LABEL_DATE'] = "ui.Label3.value"

    #---------------------------------------------------------------------------------------------
    # Keypad keep alive configuration   
    #---------------------------------------------------------------------------------------------
    config["KeypadAliveServiceEnabled"] = True
    # IP address of android alarm keypad
    config['KEYPAD_IP_ADDRESSES'] = {
               # Name :  IP Address 
                  'S4'  :  '192.168.2.155:8080'}
                  #'S6'  :  '192.168.2.88:8080',  
                  #'P5'  :  '192.168.2.233:8080', 
                  #'lgg4':  '192.168.2.100:8080'}
    
    config['KEYPAD_IP_ADDRESS']         = "192.168.2.155:8080"
    
    config["KEYPAD_LOG_FILE"]           = config['TEMP_PATH'] + "/keypad_log.txt"
    # URI used to verify if keypad is alive
    config['KEYPAD_PING_URL']           = "http://%IP%/Ping"
    # URI used to fetch logfile
    config['KEYPAD_LOG_URL']            = "http://" + config['KEYPAD_IP_ADDRESS'] + "/log"
    #-----------------------------------------------------------------------------------------
    # TTS configuration
    #-----------------------------------------------------------------------------------------
    config["ttsEnabled"] = True
    # VoiceRSS token
    config['VOICERSS_TOKEN'] = secret_config.VOICERSS_TOKEN
    # VoiceRSS api path for generating mp3 from message 
    config['VOICERSS_URL'] = "http://api.voicerss.org/?key=" + config['VOICERSS_TOKEN'] + "&src=REPLACE_WITH_MESSAGE&f=22khz_16bit_mono&hl=sv-se"
    # Url with key where to translate message to mp3
    config['TTS_GENERATOR_IP_ADDRESS'] = "192.168.2.155:8080"
    # Path to cached tts messages
    config['TTS_PRECOMPILED_MSG_PATH'] = config["ROOT"] + "davan/tts_mp3/"
    # Path to cached tts alarm messages
    config['TTS_PRECOMPILED_ALARM_MSG_PATH'] = config["TTS_PRECOMPILED_MSG_PATH"] + "alarm/"
    # Mp3 file to play
    config['SPEAK_FILE'] = '/dev/shm/speak.mp3'
    # Application used to play mp3 file on raspberry pi
    config['SPEAK_CMD'] = '/usr/bin/mpg123'
    # Url to fetch created mp3 file on android phone
    config['TTS_GENERATOR_FETCH_URL'] = "http://" + config['TTS_GENERATOR_IP_ADDRESS'] + "/ttsFetch"
    # Url to generate mp3 file on android phone
    config['TTS_GENERATOR_CREATE_URL'] = "http://" + config['TTS_GENERATOR_IP_ADDRESS'] + "/tts"
    # Select the speakers for plauging TTS messages, currently supports 
    # "RoxcoreService", "SonosService" or internal speaker
    config['SPEAKER_SERVICE'] = "RoxcoreService"
    #-----------------------------------------------------------------------------------------
    # Mp3 provider configuration
    #-----------------------------------------------------------------------------------------
    config["mp3Enabled"] = True
    config['MP3_ROOT_FOLDER'] = config['TTS_PRECOMPILED_MSG_PATH']
 
    
    #-----------------------------------------------------------------------------------------
    # DailyQuote configuration
    #-----------------------------------------------------------------------------------------
    config["DailyQuoteEnabled"] = True
    # Path to dailyquote path
    config['TTS_DAILY_QUOTE_PATH'] = config["TTS_PRECOMPILED_MSG_PATH"] + "daily_quote/"
    # Path to dailyquote file
    config['TTS_DAILY_QUOTE_FILE'] = config['TTS_DAILY_QUOTE_PATH'] + "daily_quote.mp3"
    
    
    #---------------------------------------------------------------------------------------------
    # Scenes to monitor, start if not running
    # Monitors running scens on fibaro system
    #---------------------------------------------------------------------------------------------
    config["ActiveScenesMonitorEnabled"] = True
    # List of scenes that should be monitored
    config['MONITOR_SCENES'] = {'32'} # Clock scene
    
    #---------------------------------------------------------------------------------------------
    # UPS Virtual device configuration
    #---------------------------------------------------------------------------------------------
    config["UpsEnabled"] = True
    # UPS virtual id on fibaro system
    config["UPS_VD_ID"] = "156"
    # 
    config["UPS_BUTTON_ID"] = "6"

    #---------------------------------------------------------------------------------------------
    # Internet speed test configuration
    #---------------------------------------------------------------------------------------------
    config["speedtestEnabled"]  = True
    config['SPEED_TEST_FILE']   = config["SERVICE_PATH"] + "speedtest/internet_speed_measure.sh"
    config['SPEED_TEST_RESULT'] = config['SERVICE_PATH'] + "speedtest/speedtest.txt"

    #---------------------------------------------------------------------------------------------
    # Audio service configuration
    #---------------------------------------------------------------------------------------------
    config["AudioServiceEnabled"]   = True
    config['RECEIVER_TURN_ON']      = "onkyo --host 192.168.2.218 PWR01"
    config['RECEIVER_TURN_OFF']     = "onkyo --host 192.168.2.218 PWR00"
    config['RECEIVER_SELECT_INPUT'] = "onkyo --host 192.168.2.218 SLI02"
    config['RECEIVER_SET_VOLUME']   = "onkyo --host 192.168.2.218 MVL25"
    config["CHROMECAST_NAME"]       = "ChromecastEntre"

    #---------------------------------------------------------------------------------------------
    # HTML Service configuration
    #---------------------------------------------------------------------------------------------
    config["HtmlServiceEnabled"] = True
    config["HTML_INDEX_FILE"] = config['SERVICE_PATH'] + "html/index_template.html"
    config["HTML_STYLE_FILE"] = config['SERVICE_PATH'] + "html/style.css"
    config["HTML_STATISTICS_FILE"]  = config['SERVICE_PATH'] + "html/statistics_template.html"
    config["HTML_SELECT_LOGFILE"] = config['SERVICE_PATH'] + "html/select_logfile.html"

    #---------------------------------------------------------------------------------------------
    # Sonos Service configuration
    #---------------------------------------------------------------------------------------------
    config["SonosServiceEnabled"] = False
    # Adress to Sonos speaker
    config['SONOS_SPEAKERS'] = [
        #Id,    |  Slogan       | Address     |  Default  | Play Announcement msg                         
        '0,        Livingroom,   192.168.2.108,  True,         False',
        '1,        Hallway,      192.168.2.108,  False,        False',
        '2,         All,         ,               False,        True',
    
    ]
    #---------------------------------------------------------------------------------------------
    # Weather Service configuration
    #---------------------------------------------------------------------------------------------
    config["WeatherEnabled"]     = False
    config["WEATHER_API_PATH"]   = "http://api.wunderground.com/api/"
    config["WEATHER_TOKEN"]      = secret_config.WEATHER_TOKEN
    config["WEATHER_STATION_ID"] = secret_config.WEATHER_STATION_ID
    config["WUNDERGROUND_PATH"]  = config["WEATHER_API_PATH"] + config["WEATHER_TOKEN"] + config["WEATHER_STATION_ID"]
    # Weather virtual id on fibaro system
    config["WEATHER_VD_ID"] = "79"
    # Weather button to push
    config["WEATHER_BUTTON_ID"] = "7"


    #---------------------------------------------------------------------------------------------
    # LightSchema Service configuration
    # deviceType 0=Onoff, 1=dimmer, 2=virtualdevice
    # Room, StartTime, StopTime, Interval(week/weekdays/weekend), lightLevel(0-100), deviceId, buttonId, randomTime, virtualDeviceUpdateId
    #---------------------------------------------------------------------------------------------
    config["LightSchemaServiceEnabled"] = True 
    config['LIGHT_SCHEMA'] = [
        #Room   | start | stop | Interval | deviceType | lightlevel | deviceId | labelid | random | virtualdevice | Only when armed 
        'Kitchen, 06:15,  08:30, weekdays,     1,           10,        65,         1,        15,        194,            0',
        'Kitchen, 16:15,  23:45, week,         1,           10,        65,         2,        1,         194,            0',
        'Uterum,  sunset,  23:45, week,        0,           -1,        192,        1,        10,        195,            0',
        'Outdoor, sunset, 23:40, week,         0,           -1,        191,        1,        20,        196,            0',
        'Farstukvist, sunset, 23:55, week,     0,           -1,        226,        1,        1,         227,            0',
        'Wilma,   06:30,  07:15, weekdays,     1,           20,        173,        1,        20,        197,            1',
        'Wilma,   sunset,  22:00, week,        1,           20,        173,        2,        20,        197,            1',
        'Viggo,   06:30,  07:15, weekdays,     1,           10,        177,        1,        15,        198,            1',
        'Viggo,   sunset,  21:00, week,        1,           10,        177,        1,        15,        198,            1',
        'Parkering, sunset, 23:55, week,       0,           -1,        276,        1,        1,         281,            0',
        'Datarum, 06:15,  08:30, week,         2,            1,        182,        1,        0,         304,            0',        
        'Datarum, 16:15,  23:42,  week,        2,            1,        182,        1,        0,         304,            0',
   ]
    config['LABEL_SCHEDULE'] = "ui.Schedule<BID>.value"

    #---------------------------------------------------------------------------------------------
    # ReceiverBot configuration
    #---------------------------------------------------------------------------------------------
    config["ReceiverBotServiceEnabled"] = True
    config["RECEIVER_BOT_TOKEN"] = secret_config.RECEIVER_BOT_TOKEN

    #---------------------------------------------------------------------------------------------
    # Roxcore speaker configuration
    #---------------------------------------------------------------------------------------------
    config["RoxcoreServiceEnabled"] = True
    config['ROXCORE_PORT_NR'] = "59152"
    config['ROXCORE_SPEAKERS'] = [
        #Id,    |  Slogan       | Address     |  Default  | Play Announcement msg                         
        '0,        Kitchen,      192.168.2.49,  True,         True',
        '1,        Hallway,      192.168.2.121, False,        False',
        '2,         All,            ,           False,        True',
    ]
    config['MESSAGE_ANNOUNCEMENT'] = "announcement.mp3"
    #---------------------------------------------------------------------------------------------
    # Announcement service
    #---------------------------------------------------------------------------------------------
    config["AnnouncementsServiceEnabled"] = True
    config["ANNOUNCEMENT_MENU_PATH"] = config["ROOT"] + "menu.txt"
    config["ANNOUNCEMENT_THEMEDAY_PATH"] = config["ROOT"] + "tema_dagar.txt"
    config["IDIOM_ANNOUNCEMENTS"] = config["ROOT"] + "idiomatisk.txt"
    config['ANNOUNCEMENTS_SCHEMA'] = [
        #Slogan          | Time, | Interval | | announcementname | speaker id | Text
        'SleepTime,        23:02,   weekdays,       night,           0,          Mia',
        'SleepTimeViggo,   20:30,   weekdays,       night,           0,          Viggo',
        'SleepTimeWilma,   21:30,   weekdays,       night,           0,          Wilma',
        'Morning,          06:30,   weekdays,       morning,         0,          -',
        'MorningWeekend,   09:00,   weekend,        morning,         0,          -',
        'WilmaBirthDay,    08:00,   02/06,          birthday,        0,          -',
        'ViggoBirthDay,    08:00,   20/06,          birthday,        0,          -',
        'MiaBirthDay,      08:00,   30/06,          birthday,        0,          -',
        'DavidBirthDay,    08:00,   08/07,          birthday,        0,          -',
        'RadioWeekdaysOn,  06:15,   weekdays,       radio,           0,          http://tx-bauerse.sharp-stream.com/http_live.php?i=mixmegapol_instream_se_mp3',
        #        'RadioWeekdaysOff, 08:30,   weekdays,       radio,           0,          stop',
#        'EveningWater,     22:00,   week,           water,           0',
   ]

    #---------------------------------------------------------------------------------------------
    # Calendar service
    #---------------------------------------------------------------------------------------------
    config['CalendarServiceEnabled'] = True
    config['GOOGLE_CALENDAR_TOKEN'] = secret_config.GOOGLE_CALENDAR_TOKEN

    #---------------------------------------------------------------------------------------------
    # Sun service
    #---------------------------------------------------------------------------------------------
    config['SunServiceEnabled'] = True

    #---------------------------------------------------------------------------------------------
    # Scale service
    #---------------------------------------------------------------------------------------------

    config['ScaleServiceEnabled'] = False
    config['CONSUMER_KEY']        = secret_config.NOKIA_CONSUMER_KEY
    config['CONSUMER_SECRET']     = secret_config.NOKIA_CONSUMER_SECRET
    config['OAUTH_VERIFIER']      = secret_config.NOKIA_OAUTH_VERIFIER
    config['ACCESS_TOKEN']        = secret_config.NOKIA_ACCESS_TOKEN
    config['ACCESS_TOKEN_SECRET'] = secret_config.NOKIA_ACCESS_TOKEN_SECRET
    config['NOKIA_USER_ID']       = secret_config.NOKIA_USER_ID
    

    #---------------------------------------------------------------------------------------------
    # TV service
    #---------------------------------------------------------------------------------------------
    config['TvServiceEnabled'] = True
    config['TvServiceTimeout'] = 300
    config['HARMONY_IP_ADRESS'] = '192.168.2.143'
    config['WATCH_TV_ACTIVITY'] = '26681450'
    
    #---------------------------------------------------------------------------------------------
    # Connectivity service
    # Check internet connectivity
    #---------------------------------------------------------------------------------------------
    config['ConnectivityServiceEnabled'] = True
    
    #---------------------------------------------------------------------------------------------
    # Fibaro service
    # Monitor Fibaro system alarm state.
    #---------------------------------------------------------------------------------------------
    config['FibaroServiceEnabled'] = True
    config['FibaroTimeout'] = 300
    config['FibaroVirtualDeviceId'] = "69"

    #---------------------------------------------------------------------------------------------
    # DishWashService
    # Determine when dishwascher is ready with a Fibaro power plug
    #---------------------------------------------------------------------------------------------
    config['DishWashServiceEnabled'] = True
    #---------------------------------------------------------------------------------------------
    # DepartureService
    # Fetch 
    #---------------------------------------------------------------------------------------------
    config['DepartureServiceEnabled'] = True
    config['DEPARTURE_SETTING'] = secret_config.SL_API_KEYS

    #---------------------------------------------------------------------------------------------
    # AlarmService
    # Keep a list of active alarms
    #---------------------------------------------------------------------------------------------
    config["AlarmServiceEnabled"] = True
    
    #---------------------------------------------------------------------------------------------
    # PowerUsageService
    # Measure usage time of certain devices with a Fibaro power plug. 
    #---------------------------------------------------------------------------------------------
    config["PowerUsageServiceEnabled"] = True

    #---------------------------------------------------------------------------------------------
    # PowerUsageService
    # Measure usage time of certain devices with a Fibaro power plug. 
    #---------------------------------------------------------------------------------------------
    config["TradfriServiceEnabled"] = True
    config['TRADFRI_GATEWAY_IP'] = "192.168.2.4"
    config['TRADFRI_ID'] = "tradfri-pi-bash" 
    config['TRADFRI_ID_KEY'] = secret_config.TRADFRI_KEYS

    config['TRADFRI_DEVICES'] = {
               # Name        :    ID
              'ViggoWindow'  :  '65539',
              'ViggoShelf'   :  '65540',
              'WilmaWindow'  :  '65541',
              'WilmaSlinga'  :  '65542',
              'Datarum'      :  '65544',
              'Extra1'       :  '65545',
              'Extra2'       :  '65546',
              'Extra3'       :  '65547'    
    }

def create(private_config_file="/home/pi/private_config.py", debugPrint=False):
    if (not private_config_file == None and len(private_config_file) > 0 and os.path.exists(private_config_file)):
        try:
            filename = os.path.basename(private_config_file)
            modulename = os.path.splitext(filename)[0]
            my_secrets = imp.load_source(modulename, private_config_file)
        except :
            print "Cannot import file " + private_config_file +" using default"
            import no_private_config
            my_secrets = no_private_config
    else:
        import no_private_config
        my_secrets = no_private_config
            
    config = dict()
    create_config(my_secrets, config)
    if debugPrint:
        common.debug_formated(config)
    return config

