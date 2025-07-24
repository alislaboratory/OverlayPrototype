from picamera2 import Picamera2
import cv2
import numpy as np
import time
from transparent_display import TransparentDisplay

# Initialize Picamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

display = TransparentDisplay()

# Allow camera to warm up
time.sleep(1)

# Load ArUco dictionary and parameters (legacy API)
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters_create()

print("Press 'q' to quit...")

while True:
    # Capture a frame
    frame = picam2.capture_array()

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Detect ArUco markers
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    ###### DRAWING TO DISPLAY ######
    print(corners)

    #######

    # If markers are found, draw them
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    # Show the image
    cv2.imshow("ArUco Detection", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cv2.destroyAllWindows()
picam2.stop()
