# ------------------------- DEFINE IMPORTS ---------------------------
from __future__ import print_function
from datetime import datetime, time
from lifxlan import LifxLAN
from time import sleep

import sys
import argparse
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

# ------------------------- DEFINE ARGUMENTS -------------------------
# argParser.add_argument("-a", "--min-area", type=int, default=500, help="Minimum area size before motion detection")
#argParser.add_argument('--ononly', dest='ononly', action='store_true', help="Disable turning lights off command")
#argParser.add_argument('--remote', dest='interactive', action='store_false', help="Disable Pi hardware specific functions")
#argParser.set_defaults(interactive=True)

argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--pin-sensor", type=int, default=37, help="Board GPIO pin that sensor is connected to.")
argParser.add_argument("-o", "--open-time", type=int, default=15, help="Number of seconds since door open event to ignore lights off.")
argParser.add_argument('--quiet', dest='quiet', action='store_true', help="Disable logging")
argParser.add_argument('--debug', dest='debug', action='store_true', help="Disable light actions")
argParser.add_argument('--file', dest='file', action='store_true', help="Log to file instead of console.")

argParser.set_defaults(quiet=False)
argParser.set_defaults(debug=False)
argParser.set_defaults(file=False)

args = vars(argParser.parse_args())
sensorPin = args["pin_sensor"]
openTime = args["open_time"]
quiet = args["quiet"]
debug = args["debug"]
file = args["file"]

# ------------------------- DEFINE GLOBALS ---------------------------
isDoorOpen = False
lastOpen = None
lastClosed = None

lifx = None
officeLights = None
officeLightGroup = None
officeOne = None
officeTwo = None
officeThree = None

WARM_WHITE = [58112, 0, 65535, 2500]
DAYLIGHT = [58112, 0, 65535, 5500]

# ------------------------- DEFINE FUNCTIONS -------------------------
def log(text, displayWhenQuiet = False):
    if displayWhenQuiet or not quiet:
        now = datetime.now().strftime("%H:%M:%S")
        message = f"{now}: {text}"
        if file:
            with open("/home/pi/Desktop/OfficeSensor/sensor.log", "a") as fout:
                fout.write(f"{message}\n")
        else:
            print(message)

def brightnessByPercent(percent):
    return 65535 * percent

def lightOnSequence():
    if debug: return

    try:
        if datetime.now().time() <= time(20, 0, 0, 0):
            officeLightGroup.set_brightness(brightnessByPercent(1))
        else:
            officeLightGroup.set_brightness(brightnessByPercent(0.25))

        sleep(0.5)
        officeOne.set_power("on", duration=5000)
        sleep(1)
        officeTwo.set_power("on", duration=4000)
        sleep(1)
        officeThree.set_power("on", duration=3000)
    except:
        log("Exception occurred during light on command!", True)

def lightOffSequence():
    if debug: return

    try:
        officeThree.set_power("off", duration=5000)
        sleep(1)
        officeTwo.set_power("off", duration=4000)
        sleep(1)
        officeOne.set_power("off", duration=3000)
    except:
        log("Exception occurred during light on command!", True)

def handleOpen():
    log("Open:High")
    now = datetime.now()

    global lastOpen
    lastOpen = now

    log("Turn on lights!", True)
    lightOnSequence()

def handleClose():
    log("Closed:Low")
    now = datetime.now()

    global lastClosed
    lastClosed = now

    timeSinceOpen = now - lastOpen
    if timeSinceOpen.seconds > openTime: 
        # Some time has passed since the door opened, turn off lights
        log("Turn off lights!", True)
        lightOffSequence()
    else:
        log(f"Not enough time ({timeSinceOpen.seconds}s) has passed to take action on CLOSE event.", True)

# ------------------------- DEFINE INITIALIZE ------------------------
log("Initializing...", displayWhenQuiet = True)
log(f"Args: {args}", displayWhenQuiet=True)
lifx = LifxLAN(7)
officeLightGroup = lifx.get_devices_by_group("Office")
officeLights = officeLightGroup.get_device_list()
officeOne = lifx.get_devices_by_name("Office One")
officeTwo = lifx.get_devices_by_name("Office Two")
officeThree = lifx.get_devices_by_name("Office Three")

if len(officeLights) < 3 or officeOne == None or officeTwo == None or officeThree == None :
    log(f"Did not discover all office lights! ({len(officeLights)} of 3)", displayWhenQuiet = True)
    devices = lifx.get_lights()
    print("\nFound {} light(s):\n".format(len(devices)))
    for d in devices:
        try:
        	print(d)
        except:
            pass
    sys.exit(-1)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

isDoorOpen = GPIO.input(sensorPin)
if isDoorOpen:
    lastOpen = datetime.now()
    log("Door initialized as OPEN!")
else:
    lastClosed = datetime.now()
    log("Door initialized as CLOSED!")


# ------------------------- DEFINE RUN -------------------------------
log("Initialized!", displayWhenQuiet = True)
log("Running...", displayWhenQuiet = True)
try:
    while True:
        lastState = isDoorOpen
        isDoorOpen = GPIO.input(sensorPin)

        if lastState != isDoorOpen:
            if(isDoorOpen):
                handleOpen()
            else:
                handleClose()
except KeyboardInterrupt:
    log("KeyboardInterrupt caught! Cleaning up...")
    GPIO.cleanup()
    log("GPIO.cleanup() called!")