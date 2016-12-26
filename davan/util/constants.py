'''
Created on 27 okt. 2016

@author: Wilma
'''
RESPONSE_OK = 200
RESPONSE_NOT_OK = 401
RESPONSE_FILE_NOT_FOUND = "File not found"
RESPONSE_EMPTY_MSG = ""

HUMIDITY_HIGH = "[<room_name>] Luftfuktigheten är för hög, sätt på fläkten"
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
MP3_SERVICE_NAME = "mp3"
SONOS_SERVICE_NAME = "Sonos"
WEATHER_SERVICE = "Weather"

KEYPAD_SERVICE_NAME = "KeypadAliveService"

UPS_BATTERY_MODE = "BatteryMode"
UPS_POWER_MODE = "PowerMode"
UPS_STATUS_REQ = "Status"

HTML_EXTENSION = ".html"
CSS_EXTENSION = ".css"


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