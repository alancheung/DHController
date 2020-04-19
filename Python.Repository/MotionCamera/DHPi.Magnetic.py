# ------------------------- DEFINE IMPORTS ---------------------------
from __future__ import print_function
from datetime import datetime, time
from lifxlan import LifxLAN
from time import sleep
import json

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

timestones = None
work_start = None
work_end = None
afternoon_dimmer = None

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

def err(text):
    log(text, True)

def is_between_time(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]

def convert_time(timestring):
    return datetime.strptime(timestring, "%H:%M").time()

def brightnessByPercent(percent):
    return 65535 * percent

def DAYLIGHT(brightness):
    return [58112, 0, brightness, 5500]

def WARM_WHITE(brightness):
    return [58112, 0, brightness, 2500]

def lightOnSequence():
    if debug: return

    now = datetime.now()

    # Determine brightness by configurable time
    # TODO make dynamic from sunset.
    brightness = None
    if now.time() <= afternoon_dimmer:
        brightness = brightnessByPercent(1)
    else:
        brightness = brightnessByPercent(0.45)

    # If we're in the office for work then set correct color
    # Weekday Monday(0) - Sunday(6)
    if now.weekday() < 5 and is_between_time(now.time(), (work_start, work_end)):
        officeLightGroup.set_color(DAYLIGHT(brightness), rapid = True)
        sleep(0.5)
        # Leave OfficeOne off because Kelly.
        officeTwo.set_power("on", duration=4000, rapid = True)
        sleep(1)
        officeThree.set_power("on", duration=3000, rapid = True)
    else:
        officeLightGroup.set_color(WARM_WHITE(brightness), rapid = True)
        sleep(0.5)
        officeOne.set_power("on", duration=5000, rapid = True)
        sleep(1)
        officeTwo.set_power("on", duration=4000, rapid = True)
        sleep(1)
        officeThree.set_power("on", duration=3000, rapid = True)

def lightOffSequence():
    if debug: return

    officeLightGroup.set_power("off", rapid = True)

    # Make sure lights are off
    sleep(0.5)
    officeLightGroup.set_power("off", rapid = True)

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
officeOne = lifx.get_devices_by_name("Office One")
log(f"officeOne({officeOne is not None}) initialized!")
officeTwo = lifx.get_devices_by_name("Office Two")
log(f"officeTwo({officeTwo is not None}) initialized!")
officeThree = lifx.get_devices_by_name("Office Three")
log(f"officeThree({officeThree is not None}) initialized!")

if officeOne == None or officeTwo == None or officeThree == None:
    log(f"Did not discover all office lights! OfficeOne({officeOne is not None}), OfficeTwo({officeTwo is not None}), OfficeThree({officeThree is not None})", displayWhenQuiet = True)
    devices = lifx.get_lights()
    print("\nFound {} light(s):\n".format(len(devices)))
    for d in devices:
        try:
        	print(d)
        except:
            pass
    sys.exit(-1)

try:
    with open("/home/pi/Desktop/OfficeSensor/timestones.json") as timestoneFile:
        timestones = json.load(timestoneFile)
        log("File loaded!")
except FileNotFoundError:
    err("'/home/pi/Desktop/OfficeSensor/timestones.json' could not be found!")
    sys.exit(-1)
log(f"Timestones: {timestones}", displayWhenQuiet=True)

work_start = convert_time(timestones["work_start"])
work_end = convert_time(timestones["work_end"])
afternoon_dimmer = convert_time(timestones["afternoon_dimmer"])
log("timestones converted!")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
log("GPIO initialized!")

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
    err("KeyboardInterrupt caught!")
except:
    err("Unhandled exception caught!")
finally:
    err("Cleaning up...")
    GPIO.cleanup()
    err("GPIO.cleanup() called!")