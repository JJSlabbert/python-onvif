#Pan Tilt application for ONVIF devices
#Modifications was done from https://github.com/quatanium/python-onvif
#WSDiscovery from #https://pypi.org/project/WSDiscovery/1.1.2/
#WSDiscovery only available on Raspberry PI, not windows

from time import sleep
from onvif import ONVIFCamera
from wsdiscovery import WSDiscovery, QName, Scope

#WSDiscovery part____________________________________________________
print('Scanning for potential Sonoff WiFi camers (Model GK-200MP2B)....')
print('Other WSDiscovery devices may be identified')
wsd = WSDiscovery()
wsd.start()

ttype = QName("abc", "def")

ttype1 = QName("namespace", "myTestService")

# Note: some devices scope services using onvif:// scheme, not http://
scope1 = Scope("http://myscope")
ttype2 = QName("namespace", "myOtherTestService_type1")
scope2 = Scope("http://other_scope")

xAddr = "localhost:8080/abc"
wsd.publishService(types=[ttype], scopes=[scope2], xAddrs=[xAddr])

#ret = wsd.searchServices(scopes=[scope1], timeout=10)
ret = wsd.searchServices()

for service in ret:
    print('Potential Sonoff Cameras: '+service.getEPR() + ":" + service.getXAddrs()[0])

wsd.stop()
#WSDiscovery part End_____________________________________________

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1

ip=raw_input('Provide camera IP: ')
username=raw_input('Provide camera username: ')
password=raw_input('Provide camera password: ')

print('Your RTSP URL is: rtsp://'+username+':'+password+'@'+ip+':554/av_stream/ch0')
print('Open vlc and enter the above URL in the menu MEDIA>Open Network Stream')

def perform_move(ptz, request, timeout):
    # Start continuous move
    ptz.ContinuousMove(request)
    # Wait a certain time
    sleep(timeout)
    # Stop continuous move
    ptz.Stop({'ProfileToken': request.ProfileToken})

def move_up(ptz, request, timeout=1):
    print 'move up...'
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)

def move_down(ptz, request, timeout=1):
    print 'move down...'
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)

def move_right(ptz, request, timeout=1):
    print 'move right...'
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)

def move_left(ptz, request, timeout=1):
    print 'move left...'
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)

def continuous_move():
    mycam = ONVIFCamera(ip, 80, username, password)
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    media_profile = media.GetProfiles()[0];

    # Get PTZ configuration options for getting continuous move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration._token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = media_profile._token

    ptz.Stop({'ProfileToken': media_profile._token})

    # Get range of pan and tilt
    # NOTE: X and Y are velocity vector
    global XMAX, XMIN, YMAX, YMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

    #PT control
    var=1
    while var==1: #Create infinite loop
        direction=raw_input('Type the direction that you want to pan/tilt: \n Pan Right:6 or r \n Pan Left: 4 or l \n Tilt Up: 8 or u \n Tilt Down: 2 or d \nProvide Direction:')
        print direction
        if direction=='6'or direction=='r':
            move_right(ptz, request)
        if direction=='4' or direction== 'l':
            move_left(ptz, request)
        if direction=='8' or direction== 'u':
            move_up(ptz, request)
        if direction=='2' or direction== 'd':
            move_down(ptz, request)
        #Double Moves
        if direction=='66' or direction== 'rr':
            move_right(ptz, request)
            move_right(ptz, request)
        if direction=='44' or direction== 'll':
            move_left(ptz, request)
            move_left(ptz, request)
        if direction=='88' or direction== 'uu':
            move_up(ptz, request)
            move_up(ptz, request)
        if direction=='22' or direction== 'dd':
            move_down(ptz, request)
            move_down(ptz, request)

        #Tripple Moves
        if direction=='666' or direction== 'rrr':
            move_right(ptz, request)
            move_right(ptz, request)
            move_right(ptz, request)
        if direction=='444'or direction== 'lll':
            move_left(ptz, request)
            move_left(ptz, request)
            move_left(ptz, request)
        if direction=='888' or direction== 'uuu':
            move_up(ptz, request)
            move_up(ptz, request)
            move_up(ptz, request)
        if direction=='222' or direction== 'ddd':
            move_down(ptz, request)
            move_down(ptz, request)
            move_down(ptz, request)
            
if __name__ == '__main__':
    continuous_move()
