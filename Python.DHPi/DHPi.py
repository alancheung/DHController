from __future__ import print_function
import argparse
from datetime import datetime
import time
import numpy as np
import cv2
import imutils

# Get arguments
argParser = argparse.ArgumentParser()
argParser.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
argParser.add_argument("-r", "--refresh-time", type=int, default=30, help="amount time before static image refresh")
argParser.add_argument("-t", "--threshold", type=int, default=50, help="amount of difference between images")
argParser.add_argument('--interactive', dest='interactive', action='store_true', help="running on Pi hardware")
argParser.add_argument('--remote', dest='interactive', action='store_false', help="running remotely")
argParser.set_defaults(interactive=True)

args = vars(argParser.parse_args())
min_area = args["min_area"]
refresh_time = args["refresh_time"]
img_threshold = args["threshold"]
interactive = args["interactive"]
print(args)

# ------------------------- DEFINE GLOBALS -------------------------
firstFrame = None
staticImgLastRefresh = datetime.now()


# ------------------------- DEFINE FUNCTIONS -------------------------
# Process the initial image frame from the camera
def processFrame(frame):
    frame = imutils.resize(frame, width=500)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, ksize=(21, 21), sigmaX=0)
    return frame

# Print message to console with timestamp
def timestamp(text):
    curr_time = datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
    print (curr_time + ": " + text)







# ------------------------- DEFINE RUN -------------------------
# Init camera with camera warmup
camera = cv2.VideoCapture(0)
time.sleep(2)

# Run
while True:
    (okFrame, frame) = camera.read()
    p_frame = processFrame(frame)

    if firstFrame is None:
        firstFrame = p_frame

    frameDelta = cv2.absdiff(firstFrame, p_frame)
    threshold = cv2.threshold(frameDelta, img_threshold, 255, cv2.THRESH_BINARY)[1]

    # Dilate movement areas
    threshold = cv2.dilate(threshold, None, iterations=2)
    contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    motionStatus = "Unoccupied"
    # Check to see if motion has occurred
    for c in contours:
        # Motion detected but not triggered
        motionSize = cv2.contourArea(c)
        if motionSize < min_area:
            #timestamp('Ignored motion with size (' + str(motionSize) + ')')
            continue

        # motion dectected.
        timestamp('Detected motion!')
        motionStatus = "Occupied"
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)

    # Update feed!
    cv2.putText(frame, "Status: {}".format(motionStatus), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    #cv2.putText(frame, 
    #            datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), 
    #            (10, frame.shape[0] - 10), 
    #            cv2.FONT_HERSHEY_SIMPLEX,
    #            0.35,
    #            (0, 0, 255),
    #            1)

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