'''
@author: davandev 
sys.setdefaultencoding('latin-1')
'''

RESPONSE_OK = 200
RESPONSE_NOT_OK = 401
RESPONSE_FILE_NOT_FOUND = "File not found"
RESPONSE_EMPTY_MSG = ""

TURN_ON = "turnOn"
TURN_OFF ="turnOff"

HUMIDITY_HIGH = "Fuktigt i badrummet, var god ventilera!"
KEYPAD_NOT_ANSWERING = "Alarm Keypad har slutat svara"
KEYPAD_ANSWERING = "Alarm Keypad har startats"

UPS_SERVICE_NAME = "Ups"
AUTH_SERVICE_NAME = "authenticate"
AUDIO_SERVICE_NAME = "AudioService"
SPEEDTEST_SERVICE_NAME = "speedtest"
TTS_SERVICE_NAME =  "tts"
QUOTE_SERVICE_NAME = "DailyQuote"
HTML_SERVICE_NAME = "HtmlService"
ACTIVE_SCENES_SERVICE_NAME = "ActiveScenesMonitor"
TELLDUS_SENSOR_SERVICE = "TelldusSensorService"
TELLDUS_SERVICE_NAME = "telldus"
PRESENCE_SERVICE_NAME = "presence"
DEVICE_PRESENCE_SERVICE_NAME = "DevicePresenceService"
MP3_SERVICE_NAME = "mp3"
SONOS_SERVICE_NAME = "Sonos"
WEATHER_SERVICE = "Weather"
LIGHTSCHEMA_SERVICE = "LightSchemaService"

KEYPAD_SERVICE_NAME = "KeypadAliveService"

UPS_BATTERY_MODE = "BatteryMode"
UPS_POWER_MODE = "PowerMode"
UPS_STATUS_REQ = "Status"

HTML_EXTENSION = ".html"
CSS_EXTENSION = ".css"
MP3_EXTENSION = ".mp3"

MIME_TYPE_HTML = 'text/html'
MIME_TYPE_CSS = 'text/css'
MIME_TYPE_MP3 = 'audio/mpeg'

HTML_TABLE_END = "</table>"
HTML_TABLE_START = """<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style><table> <tr>
    <th>Service</th>
    <th>Successful</th> 
    <th>Error</th>
  </tr>"""

COLUMN_TAG="""
    <div id="column<COLUMN_ID>">
    <h3><SERVICE_NAME></h3>
    <ul>
    <SERVICE_VALUE>
    </ul>
    </div>
"""
