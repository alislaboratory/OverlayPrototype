# 1. Find the 3D coordinates of the center of the arUco code relative to the front-facing camera.
# 2. Find the 3D coordinates of the center of the arUco code relative to the observer camera.
# 3. Find the point of intersection between display and this vector.
# 4. Draw a pixel at the point of intersection.

from picamera2 import Picamera2
import cv2
import numpy as np
import time

# Initialize Picamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

# Allow camera to warm up
time.sleep(1)

# Load ArUco dictionary and parameters (legacy API)
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters_create()

print("Press 'q' to quit...")

while True:
    # Capture a frame
    frame = picam2.capture_array()
    frame = cv2.rotate(frame, cv2.ROTATE_180)

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Detect ArUco markers
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        # Draw the marker outlines
        # cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # For each marker, compute and draw its center point
        for marker_corners, marker_id in zip(corners, ids.flatten()):
            # marker_corners is an array of shape (1, 4, 2); reshape to (4,2)
            pts = marker_corners.reshape((4, 2))
            # Compute the midpoint
            center = pts.mean(axis=0).astype(int)
            cx, cy = center

            # Draw a filled circle at the center
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

            
            


    # Show the image
    cv2.imshow("ArUco Detection", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cv2.destroyAllWindows()
picam2.stop()
