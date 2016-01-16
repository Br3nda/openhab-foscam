Although there is openHAB binding for Foscam IP cameras, there are many ways to
interact with them from an openHAB server. This wiki page describes some of the
techniques shared by openHAB users (edited).

Contents:
* [Displaying Video in Sitemap](#displaying-streaming-video-in-sitemap)
* [Motion Alarms](#motion-alarms)
* [General API Access](#general-api-access)
* [Related Discussions](#related-discussions)

## Displaying Streaming Video in SiteMap

One of the camera substreams can be configured to to stream MJPEG (replaces existing
substream video).

From [Kimberly Fischer](https://community.openhab.org/users/kfischer628):

> I was originally told that the H.264 cameras cannot be show live in the UI. 
> Not true. My solution was to turn one of the streams to mjpeg and then the 
> video widget works great. I don't know if its a good as the HD stream but 
> it does work flawlessly in the UI without any plugins. Make sure the firmware 
> is up to date and you use the mjpeg option in your sitemap item.
>
>     http://ip address:port/cgi-bin/CGIProxy.fcgi?cmd=setSubStreamFormat&format=1&usr=xxxx&pwd=xxxxx</strong>
>
> will set the substream to mjpeg. I have 5 foscam FI9853EP HD POE cameras that I 
> can view in the openhab ui. Works from the internet too. Also works in HABDroid 
> as well. [I can also] view my h.264 cams in chrome from the address bar.

From [Nicholas Waterton](https://community.openhab.org/users/Nicholas_Waterton):

> I have 4 foscams displayed in 4 quadrants using the webview sitemap item. You make 
> a simple web page with four image items. I have individual web pages for each camera, 
> and made each image a link to/from the main 4up page.
>
> This now means that you can display all 4 cameras at once (in quadrants), 
> then touching (or clicking) on an image zooms it up to full screen. Touching 
> it again goes back to quadrants again.
>
> You have to have an http server (Apache2 I'm using) you can serve the web 
> pages from. The pages are very simple, just a few lines each. This works 
> independently of how many people are using openhab, and in a browser 
> it's just a web page.

## Motion Alarms

Some versions of Foscam cameras provide a motion detection callback (models?), 
but the newer HD cameras do not. Users have proposed several techniques for
obtaining Foscam camera motion alarms in openHAB.

## Poll Camera Device State (H.264 camera API)

The Foscam HD camera API supports retrieval of the device state which includes the
motion alarm status. This status is changed for a brief time after motion is detected
and then it resets itself. Polling is required to detect the motion alarms.

From [mstormi](https://community.openhab.org/users/mstormi):

> I'm polling [with]:

>     String Foscam_Detect "Bewegungserkennung Aussenkamera [MAP(foscam.map):%s]" <camera> (Status,Test) { http="<[http://foscam:88/cgi-bin/CGIProxy.fcgi?cmd=getDevState&usr=USER&pwd=PASSWORD:4000:REGEX(.*?<motionDetectAlarm>(.*?)</motionDetectAlarm>.*)]" }

> Not the most elegant solution, and specific to Foscam, but it works and it's 
> fast to react, almost as good as a PIR sensor.

## Poll Camera Log (H.264 camera API)

From [Steve Bate](https://community.openhab.org/users/steve1):

> The camera log can be polled to retrieve motion alarms events. This has the advantage
> that no events will be lost and analysis can be performed on event timing and frequency
> and so on. The log access would be difficult to do directly with a http binding, so I
> recommend using a script to retrieve and process the log. I use the foscam-python-library
> and JSR223 Jython rules and scripts. I also use the log analysis to determine who
> is logging into my camera (user names and IP addresses) for security monitoring.

See also: [General API Access](#general-api-access)

### Use Motion Alarm Callback (older camera API)

From [watou]():

> Here is some sample code adapted from one of my rule files that demonstrates 
> instructing two different Foscam model cameras to enable or disable motion detection, 
> based on the switch state of the Present item. When the switch changes to OFF, it 
> sends HTTP commands to each camera (IP addresses ending in .14 and .15) to enable 
> motion detection, and in the case of the model that supports callbacks on motion, 
> tells it to callback to the openHAB server (IP address ending in .10) to flip a 
> Switch item. When the Present switch is set to ON, it disables motion detection 
> on all cameras.
> ```
> import org.openhab.core.library.types.*
> import java.util.HashMap
> import java.util.LinkedHashMap
> 
> val HashMap<String, LinkedHashMap<String, Object>> cameras =
>     newLinkedHashMap(
>     "entrance-cam" -> (newLinkedHashMap(
> 		"snap_url" -> "http://192.168.1.14/snapshot.cgi?user=admin&pwd=password",
> 		"enable_motion_url" -> "http://192.168.1.14/set_alarm.cgi?motion_armed=1&motion_sensitivity=5&motion_compensation=1&mail=1&upload_interval=34463&http=1&http_url=http%3A%2F%2F192.168.1.10%3A8080%2FCMD%3FEntranceMotion%3DON&schedule_enable=0&user=admin&pwd=password",
>		"disable_motion_url" -> "http://192.168.1.14/set_alarm.cgi?motion_armed=0&user=admin&pwd=password")
>            as LinkedHashMap<String, Object>),
>	"kitchen-cam" -> (newLinkedHashMap(
>		"snap_url" -> "http://192.168.1.15:88/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=admin&pwd=password",
>		"enable_motion_url" -> "http://192.168.1.15:88/cgi-bin/CGIProxy.fcgi?cmd=setMotionDetectConfig&isEnable=1&linkage=7&snapInterval=2&sensitivity=1&triggerInterval=5&schedule0=1023&schedule1=1023&schedule2=1023&schedule3=1023&schedule4=1023&schedule5=1023&schedule6=1023&area0=1023&area1=1023&area2=1023&area3=1023&area4=1023&area5=1023&area6=1023&area7=1023&area8=1023&area9=1023&usr=admin&pwd=password",
>		"disable_motion_url" -> "http://192.168.1.15:88/cgi-bin/CGIProxy.fcgi?cmd=setMotionDetectConfig&isEnable=0&usr=admin&pwd=password")
>	    as LinkedHashMap<String, Object>)
>    )
>
> rule PresenceChanged
> when
> 	Item Present changed
> then
> 	switch Present.state {
> 		case OFF : cameras.values.forEach [ camera | sendHttpGetRequest(camera.get("enable_motion_url")) ]
> 		case ON : cameras.values.forEach [ camera | sendHttpGetRequest(camera.get("disable_motion_url")) ]
>	}
> end
> ```

### Use inotify to monitor new recordings or snapshots (Linux-specific)

The Foscam cameras can be configured to transmit recordings and snapshots to an FTP
server. The Linux inotify tools can be used to monitor for new files and then inject
an item state change into openHAB using the REST API. The advantage is that openHAB
polling for motion alarms is not required.

From [marco_anderheyden](https://community.openhab.org/users/marco_anderheyden):

> I've created a bash-script which detects a motion and send it to openHAB. 
> This is done by inotify-tools. Inotify "subscribes" a record folder, and when the 
> camera is storing a video or image, i invokes another bash-script which is 
> doing a curl http request to openHAB's rest service.

> I've also completed a short bash script, which can extract a snapshot for 
> example every minute, and save it to the harddisk and could also upload it to an 
> ftp server. This can also placed into the sitemap, of course.

#### Resources

* [How to use inotify-tools to trigger scripts on filesystem events](http://techarena51.com/index.php/inotify-tools-example/)
* [Windows port of inotify](https://github.com/thekid/inotify-win)
* [Is there a command like “watch” or “inotifywait” on the Mac?](http://stackoverflow.com/questions/1515730/is-there-a-command-like-watch-or-inotifywait-on-the-mac)

### Use Motion to process video streams

Motion is a program that monitors the video signal from cameras. 
It is able to detect if a significant part of the picture has changed; 
in other words, it can detect motion. 
Some openHAB users stream video to the Motion application and then inject motion triggers
into openHAB using itsp [ReST API](https://github.com/openhab/openhab/wiki/REST-API).

From [Ben Jones](https://community.openhab.org/users/ben_jones12):
 
> This is very easy to setup and works well with all sorts of different IP/USB cameras. 
> There is a nice simple REST API for enabling/disabling motion detection and it 
> provides a mechanism for calling out to custom scripts and programs on various events.

> For example I have 4 cameras (all different types) dotted around the house all 
> being monitoring by one instance of motion on my home server. I can view the 
> camera streams via the motion web server, arm/disarm motion detection via a 
> simple HTTP binding in openHAB, and then call out to a python script which 
> updates another Camera_MotionDetection item in openHAB via the REST API.

> I also have another script which posts the motion snapshot to a private Slack 
> channel so I can quickly monitor from my phone when away from home.

> ... [T]he only thing it can handle is the arm/disarm logic.

From [Nicholas Waterton](https://community.openhab.org/users/Nicholas_Waterton):
 
> I use the HD low level protocol for Foscam, to get the video and motion triggers 
> (you can get audio also, but it's a pain). I built the low level protocol into 
> a modified version of motion (plus HD motion tracking for the pan/tilt cameras), 
> and have a python program to trap low level motion triggers. The low level 
> protocol is much faster than using the URL interface (but it's not published 
> anywhere, so it's deciphered by trial and error).

> Normally you would use rtsp to get the camera image, but it has horrible lag on it, 
> and distorts frequently. The low level protocol pulls the H.264 feed directly from 
> the camera, with little delay, and I decode it using the ffmpeg decoder libraries 
> (libavdecode). You can do this in motion or python, it's pushing it to try 
> decoding mainstream HD video at 30 fps in python though. substream video 
> or snapshots work OK.
> 
> You need the latest version of "motion" the earlier ones did not support RTSP, 
> and you need FFMPEG as well (motion uses FFMPEG libraries to decode the 
> H.264 video stream).
 
#### Resources

* [Motion Wiki](http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome)
* [pyh264decode](https://github.com/tzwenn/pyh264decode) - This is a small Python module 
to decode raw H.264 packets with external avcC extra data.

## General API Access

The Foscam HD API is exposed as an HTTP API. This can be accessed directly using the
openHAB HTTP binding but it can also be accessed using wrapper libraries for various
programming languages.

### JSR223 and Jython

From [Steve Bate](https://community.openhab.org/users/steve1):

> The foscam-python-lib (see link below) is compatible with Jython and can be used with
> the openHAB [JSR223 binding](https://github.com/openhab/openhab/wiki/Jsr223-Script-Engine) and Jython rules to access Foscam HD cameras. The 
> library supports most of the Foscam CGI API. The library is useful because some of 
> the CGI functionality is not practical to use with just an HTTP binding. For example, 
> to enable or disable motion control, the current motion detect config must be retrieved 
> and merged with the enabled/disable value. Otherwise, all the other motion 
> detection configurations will be reset.
>
> The library can also be used with CPython outside of openHAB and then use the openhab 
> [ReST API](https://github.com/openhab/openhab/wiki/REST-API) to inject state changes and the exec binding to invoke external CPython
> scripts.

#### API Wrapper Libraries

Language      | Library       | Notes
------------- | ------------- | -----------
Python | [foscam-python-lib](https://github.com/quatanium/foscam-python-lib) | Jython compatible, H.264
Javascript | [foscam-javascript-lib](https://github.com/quatanium/foscam-javascript-lib) | H.264
Javascript | [foscamhd-client](https://www.npmjs.com/package/foscamhd-client) | Node.js, H.264
Python        | [ipcam](http://gitlab.clicknweb.com/eric/ipcam/tree/master)
.NET          | [Foscon](https://github.com/balassy/Foscon)

#### Resources

* [Foscam IPCamera CGI User Guide](https://github.com/balassy/Foscon/blob/master/FosconSolution/Doc/Foscam%20IPCamera%20CGI%20User%20Guide-3518%20Ver.1.0.8.pdf)

## Related Discussions

* https://community.openhab.org/t/idea-for-foscam-camera-binding/4857/9
* https://community.openhab.org/t/security-camera-recommendations/3616/9
* [Forum Query: Foscam](https://community.openhab.org/search?q=foscam)





