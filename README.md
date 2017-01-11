# DavanServer
DavanServer is an application server executing home automation services, connected to a Fibaro HC2 system.

Although the Fibaro HC2 is really good and fulfills most of my needs there were some features I was missing and it 
was difficult to implement on HC2. So the idea was to create a small applicationserver that could execute services 
that was not possible on HC2 and also to offload HC2 with tasks that could be performed a raspberry pi. 

The server has only been tested on a raspberry pi running raspbian. The server provides a HTTP interface from where services can be invoked
or information fetched. This makes it easy to communicate with a HC2.<br>
The server also provides a simple webinterface to be able to check running services, read logfiles, and a simple statistics page.

Current available services:<br>
- TtsService: Receives a text string via HTTP interface, performs text to speach translation on the text string using voicerss service and
finally play the mp3 through raspberry pi (to which I have a couple of speakers connected.) <br>
- UpsService: Monitors the status of an APC ups. The ups is connected via usb to the raspberry pi. When there is a power outage the UpsService 
is notified via HTTP interface and will notify the change via telegram. It also provides possibility for HC2 to get ups status information 
to display in a virtual device.<br>
- WeatherService: Fetches weather information from wunderground. Provides the weather infomation to a virtual device in HC2 
- TelldusService: Proxy between HC2 and Telldus Live service. Makes it possible to turn on/off lights controlled by a tellstick .Net 
with HC2
- TelldusSensorService: Proxy between HC2 and Telldus Live service. Fetches sensor values from devices controlled by a tellstick .Net and 
pushes the values via HTTP to HC2.
- SpeedtestService: Peforms internet speed test measurements, possible to forward measurements to thingspeak service.
- PresenceService: The purpose of the service is to try to determine when anyone in the family arrives or leaves home and then update a 
virtual device with the status and also send telegram notifications. 
The service is based on the presence of mobile phones connected to a wifi network. 
There are currently 2 different presence services, one that relies arp requests(however in later android and ios versions it is not really reliable) 
the other service fetches device status from my local internet router. It has only been tested with Asus router though, but sofar it seems 
to work ok.
-PictureService: Invoked on a received picture request, it will take pictures from ip cameras and push the pictures via telegram to
all configured receivers 
- KeypadAliveService: Detect status of my android smarthome alarm controller app running on an old android phone that is wallmounted in my house.
In case alarm controller app stops responding a telegram message is sent.
- ActiveScenesMonitorService: Verifies that active scenes on HC2 is still running and restart the scenes if it stops. I have had some problems
with active scenes on HC2 being stopped.
- LogReceiverService: Receives log items via HTTP from HC2 and store it in logfile. Kind of simple log collecting service
- Mp3ProviderService: Handles HTTP requests for mp3 files stored on raspberry pi. Used to get a chromecast to play particular mp3 files 
(normally) text to speach mp3s.
- HtmlService: Small HTML server that can perform a few simple tasks
- DailyQuote: Fetches a daily quote from a webservice, perfoms tts and plays the mp3 on a onkyo receiver via chromecast. 
- AudioService: Make it possible to play mp3 on onkyo receiver using chromecast.
- AuthenticationService: Simple service that can arm/disarm the alarm system on HC2. 
