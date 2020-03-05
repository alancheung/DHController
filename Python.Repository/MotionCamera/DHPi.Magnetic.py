# ------------------------- DEFINE IMPORTS ---------------------------
from __future__ import print_function
from datetime import datetime
from lifxlan import LifxLAN
from time import sleep

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
argParser.add_argument("-o", "--open-time", type=int, default=3000, help="Number of seconds since door open event to ignore lights off.")
argParser.add_argument('--quiet', dest='quiet', action='store_true', help="Disable logging")

argParser.set_defaults(quiet=False)

args = vars(argParser.parse_args())
sensorPin = args["pin_sensor"]
openTime = args["open_time"]
quiet = args["quiet"]
print(f"Args: {args}")
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
        print(f"{now}: {text}")

def lightOnSequence():
    officeOne.set_power("on", duration=5000)
    sleep(1)
    officeTwo.set_power("on", duration=4000)
    sleep(1)
    officeThree.set_power("on", duration=3000)

def lightOffSequence():
    officeThree.set_power("off", duration=5000)
    sleep(1)
    officeTwo.set_power("off", duration=4000)
    sleep(1)
    officeOne.set_power("off", duration=3000)

def handleOpen():
    log("Open:High")
    now = datetime.now()

    global lastOpen
    lastOpen = now

    if lastClosed is None:
        log("OPEN event received, but no corresponding CLOSE event!", True)
    else:
        timeSinceClose = now - lastClosed
        log(f"{timeSinceClose.seconds}s has passed from last door close. Turn on lights!", True)
        lightOnSequence()


def handleClose():
    log("Closed:Low")
    now = datetime.now()

    global lastClosed
    lastClosed = now

    if lastOpen is None:
        log("CLOSE event received, but no corresponding OPEN event!", True)
    else:
        timeSinceOpen = now - lastOpen
        if timeSinceOpen.seconds > openTime: 
            # Some time has passed since the door opened, turn off lights
            log(f"{timeSinceOpen.seconds}s has passed from last door open. Turn off lights!", True)
            lightOffSequence()
        else:
            log(f"Not enough time ({timeSinceOpen.seconds}s) has passed to take action.", True)

    # record last off event
    

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
    print("KeyboardInterrupt caught! Cleaning up...")
    GPIO.cleanup()
    print("GPIO.cleanup() called!")