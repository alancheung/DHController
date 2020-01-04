from collections import deque
import numpy as np
import cv2
import imutils

kernel = np.ones((5,5),np.uint8)
pts = deque(maxlen=64)

# initialize camera and size window size as 640px by 480px
camera = cv2.VideoCapture(0)
camera.set(3, 640)
camera.set(4, 480)

thresh = 40

def detectShape(c):
    # initialize the shape name and approximate the contour
    shape = "unidentified"
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.04 * peri, True)
    # if the shape is a triangle, it will have 3 vertices
    if len(approx) == 3:
        shape = "triangle"

        # if the shape has 4 vertices, it is either a square or
        # a rectangle
    elif len(approx) == 4:
        # compute the bounding box of the contour and use the
        # bounding box to compute the aspect ratio
        (x, y, w, h) = cv2.boundingRect(approx)
        ar = w / float(h)

        # a square will have an aspect ratio that is approximately
        # equal to one, otherwise, the shape is a rectangle
        shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
 
    # if the shape is a pentagon, it will have 5 vertices
    elif len(approx) == 5:
        shape = "pentagon"
    
    # otherwise, we assume the shape is a circle
    else:
        shape = "circle"

    # return the name of the shape
    return shape

while 1:
    (grabbed, frame) = camera.read()
    frame = imutils.rotate(frame, angle=180)

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.equalizeHist(frame_gray)
    #frame_gray = cv2.resize(frame_gray, (120, 120), interpolation = cv2.INTER_CUBIC)

    # find the point by looking for pixels >40
    th, frame_gray = cv2.threshold(frame_gray, thresh, 255, cv2.THRESH_BINARY)

    # make the dot bigger
    frame_gray = cv2.dilate(frame_gray, kernel, iterations = 3)
 
    # find contours in the mask and initialize the current
	# (x, y) center of the ball
    cnts = cv2.findContours(frame_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
 
	# only proceed if at least one contour was found
    if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # find spell?????
        shape = detectShape(c)
        print shape

	# update the points queue
    pts.appendleft(center)

    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        cv2.line(frame_gray, pts[i - 1], pts[i], (255, 0, 0), thickness = 10)

    # loop and show frame
    cv2.imshow('raw', frame)
    cv2.imshow('raw-grey', frame_gray)
    keyPressed = cv2.waitKey(1) & 0xFF
    if keyPressed == ord('q'):
        break
    # increase threshold if 't' is pressed, decrease for 'g'
    elif keyPressed == ord('t'):
        thresh = thresh + 10
        print 'Threshold:' + str(thresh)
    elif keyPressed == ord('g'):
        thresh = thresh - 10
        print 'Threshold:' + str(thresh)

    
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
