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

def log(text, displayWhenQuiet = False):
    if displayWhenQuiet or not quiet:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"{now}: {text}")

# ------------------------- DEFINE ARGUMENTS -------------------------
# argParser.add_argument("-a", "--min-area", type=int, default=500, help="Minimum area size before motion detection")
#argParser.add_argument('--ononly', dest='ononly', action='store_true', help="Disable turning lights off command")
#argParser.add_argument('--remote', dest='interactive', action='store_false', help="Disable Pi hardware specific functions")
#argParser.set_defaults(interactive=True)

argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--pin-sensor", type=int, default=37, help="Board GPIO pin that sensor is connected to.")
argParser.add_argument("-o", "--open-time", type=int, default=30, help="Number of seconds since door open event to ignore lights off.")
argParser.add_argument("-i", "--ignore-time", type=int, default=7, help="Number of seconds to ignore since last input event.")
argParser.add_argument('--quiet', dest='quiet', action='store_true', help="Disable logging")
argParser.add_argument('--debug', dest='debug', action='store_true', help="Disable light actions")
argParser.add_argument('--file', dest='file', action='store_true', help="Log to file instead of console.")

argParser.set_defaults(quiet=False)
argParser.set_defaults(debug=False)
argParser.set_defaults(file=False)

args = vars(argParser.parse_args())
sensorPin = args["pin_sensor"]
openTime = args["open_time"]
ignoreTime = args["ignore_time"]
quiet = args["quiet"]
debug = args["debug"]
file = args["file"]
log(f"Args: {args}", displayWhenQuiet=True)
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

    if datetime.now().time() <= time(20, 0, 0, 0):
        officeLightGroup.set_brightness(brightnessByPercent(1), rapid=True)
    else:
        officeLightGroup.set_brightness(brightnessByPercent(0.25), rapid=True)

    sleep(0.5)
    officeOne.set_power("on", duration=5000, rapid=True)
    sleep(1)
    officeTwo.set_power("on", duration=4000, rapid=True)
    sleep(1)
    officeThree.set_power("on", duration=3000, rapid=True)

def lightOffSequence():
    if debug: return
    officeThree.set_power("off", duration=5000, rapid=True)
    sleep(1)
    officeTwo.set_power("off", duration=4000, rapid=True)
    sleep(1)
    officeOne.set_power("off", duration=3000, rapid=True)

def handleOpen():
    log("Open:High")
    now = datetime.now()

    global lastOpen
    lastOpen = now

    if lastClosed is None:
        log("OPEN event received, but no corresponding CLOSE event!", True)
    else:
        timeSinceClose = now - lastClosed
        if timeSinceClose.seconds > ignoreTime:
            log(f"{timeSinceClose.seconds}s has passed from last door close. Turn on lights!", True)
            lightOnSequence()
        else:
            log(f"Not enough time ({timeSinceClose.seconds}s) has passed to take action on open event.", True)


def handleClose():
    log("Closed:Low")
    now = datetime.now()

    global lastClosed
    lastClosed = now

    if lastOpen is None:
        log("CLOSE event received, but no corresponding OPEN event!", True)
    else:
        timeSinceOpen = now - lastOpen
        # No need to check ignore time since openTime >= ignoreTime
        if timeSinceOpen.seconds > openTime: 
            # Some time has passed since the door opened, turn off lights
            log(f"{timeSinceOpen.seconds}s has passed from last door open. Turn off lights!", True)
            lightOffSequence()
        else:
            log(f"Not enough time ({timeSinceOpen.seconds}s) has passed to take action on close event.", True)

# ------------------------- DEFINE INITIALIZE ------------------------
log("Initializing...", displayWhenQuiet = True)

lifx = LifxLAN(7)
officeLightGroup = lifx.get_devices_by_group("Office")
officeLights = officeLightGroup.get_device_list()

if len(officeLights) < 3:
    log(f"Did not discover all office lights! ({len(officeLights)} of 3)")
    sys.exit(-1)

officeOne = next(filter(lambda l: l.get_label() == "Office One", officeLights), None)
officeTwo = next(filter(lambda l: l.get_label() == "Office Two", officeLights), None)
officeThree = next(filter(lambda l: l.get_label() == "Office Three", officeLights), None)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

isDoorOpen = GPIO.input(sensorPin)
if isDoorOpen:
    lastOpen = datetime.now()
    log("Door initialized as OPEN!", displayWhenQuiet = True)
else:
    lastClosed = datetime.now()
    log("Door initialized as CLOSED!", displayWhenQuiet = True)

# Make sure time makes sense
if ignoreTime > openTime: 
    openTime = ignoreTime

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