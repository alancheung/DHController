from __future__ import print_function
from datetime import datetime
from lifxlan import LifxLAN

import argparse
import time
import numpy as np
import cv2
import imutils

# Get arguments
argParser = argparse.ArgumentParser()
argParser.add_argument("-a", "--min-area", type=int, default=500, help="Minimum area size before motion detection")
argParser.add_argument("-r", "--refresh-time", type=int, default=60, help="Amount of seconds before static image refresh")
argParser.add_argument("-m", "--motion-time", type=int, default=300, help="Amount of seconds after last motion event to still be considered active")
argParser.add_argument("-t", "--threshold", type=int, default=40, help="Amount of difference between images")
argParser.add_argument('--show', dest='interactive', action='store_true', help="Display debugging windows")
argParser.add_argument('--remote', dest='interactive', action='store_false', help="Disable Pi hardware specific functions")
argParser.set_defaults(interactive=True)

args = vars(argParser.parse_args())
min_area = args["min_area"]
refresh_time = args["refresh_time"]
img_threshold = args["threshold"]
interactive = args["interactive"]
motion_time = args["motion_time"]
print(f"Args: {args}")

# ------------------------- DEFINE GLOBALS -------------------------
firstFrame = None
staticImgLastRefresh = datetime.now()
lastMotionDetectionEvent = datetime.now()

# ------------------------- DEFINE FUNCTIONS -------------------------
# Process the initial image frame from the camera
def processFrame(frame):
    frame = imutils.resize(frame, width=500)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, ksize=(21, 21), sigmaX=0)
    return frame

# Print message to console with timestamp
def timestampDebug(text):
    curr_time = datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
    print (curr_time + ": " + text)

def shouldUpdateStaticImage(updated_frame, now):
    if firstFrame is None:
        return True
    
    lastUpdateDelta = now - staticImgLastRefresh
    if lastUpdateDelta.seconds >= refresh_time:
        return True

    return False

def getMotionStatusString(motionDelta, loopMotion):
    if loopMotion:
        return "Occupied"
    elif lastMotionDelta.seconds <= motion_time:
        return f"Occupied (Stale: {lastMotionDelta.seconds}seconds)"
    else:
        return "Unoccupied"

# ------------------------- DEFINE INITIALIZE -------------------------
# Init camera with camera warmup
timestampDebug("Initializing...")
camera = cv2.VideoCapture(0)
time.sleep(2)
timestampDebug("Initialized.")
timestampDebug("Running...")

# ------------------------- DEFINE RUN -------------------------
while True:
    loopStart = datetime.now()
    (okFrame, frame) = camera.read()
    p_frame = processFrame(frame)

    if shouldUpdateStaticImage(p_frame, loopStart):
        timestampDebug("Static background updated!")
        staticImgLastRefresh = loopStart
        firstFrame = p_frame

    frameDelta = cv2.absdiff(firstFrame, p_frame)
    threshold = cv2.threshold(frameDelta, img_threshold, 255, cv2.THRESH_BINARY)[1]

    # Dilate movement areas
    threshold = cv2.dilate(threshold, None, iterations=2)
    contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    # Check to see if motion has occurred
    loopMotion = False
    for c in contours:
        # Motion detected but not triggered
        motionSize = cv2.contourArea(c)
        if motionSize < min_area:
            #timestamp('Ignored motion with size (' + str(motionSize) + ')')
            continue

        # motion dectected.
        timestampDebug('Detected motion!')
        loopMotion = True
        lastMotionDetectionEvent = loopStart
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)

    # Update feed!
    lastMotionDelta = loopStart - lastMotionDetectionEvent
    cv2.putText(frame, "Status: {}".format(getMotionStatusString(motionDelta=lastMotionDelta, loopMotion=loopMotion)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    if (interactive):
        cv2.imshow('Feed', frame)
        #cv2.imshow('Threshold', threshold)
        #cv2.imshow('Delta', frameDelta)
        #cv2.imshow('Static', firstFrame)

    keyPressed = cv2.waitKey(1) & 0xFF
    if keyPressed == ord('q'): 
        break
    elif keyPressed == ord('r'):
        firstFrame = None

camera.release()
cv2.destroyAllWindows()