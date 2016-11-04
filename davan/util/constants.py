'''
Created on 27 okt. 2016

@author: Wilma
'''
RESPONSE_OK = 200
RESPONSE_NOT_OK = 401

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
PRESENCE_SERVICE_NAME = "presence"

UPS_BATTERY_MODE = "BatteryMode"
UPS_POWER_MODE = "PowerMode"
UPS_STATUS_REQ = "Status"

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
