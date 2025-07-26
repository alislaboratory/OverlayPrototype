from picamera2 import Picamera2
import cv2
import numpy as np
import time

# --- USER SETUP: adjust these paths & values ---
CALIB_YAML    = "camera_calibration.yaml"  # your YAML file
MARKER_LENGTH = 0.05                 # marker side length in meters
# ----------------------------------------------

# Load camera calibration from YAML
fs = cv2.FileStorage(CALIB_YAML, cv2.FILE_STORAGE_READ)
if not fs.isOpened():
    raise IOError(f"Cannot open calibration file: {CALIB_YAML}")
camera_matrix = fs.getNode("camera_matrix").mat()
dist_coeffs   = fs.getNode("distortion_coefficients").mat()
fs.release()

# Initialize Picamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size   = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()
time.sleep(1)

# Prepare ArUco detector
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
params     = cv2.aruco.DetectorParameters_create()

print("Press 'q' to quit...")

while True:
    # Capture & preprocess
    frame = picam2.capture_array()
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    gray  = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Detect markers
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=params)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # Estimate pose
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            corners, MARKER_LENGTH, camera_matrix, dist_coeffs
        )

        for i, marker_id in enumerate(ids.flatten()):
            rvec = rvecs[i][0]
            tvec = tvecs[i][0]  # (x, y, z) in meters

            # Draw the 3D axes using drawFrameAxes instead
            cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs,
                              rvec, tvec, MARKER_LENGTH * 0.5)

            # Overlay the 3D coords on screen
            x, y, z = tvec
            text = f"ID {marker_id}: x={x:.3f}, y={y:.3f}, z={z:.3f} m"
            corner_pt = tuple(corners[i][0][0].astype(int))
            cv2.putText(frame, text, (corner_pt[0], corner_pt[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Print to console
            print(f"Marker {marker_id} → (x,y,z)=({x:.3f},{y:.3f},{z:.3f}) m")

    # Show result
    cv2.imshow("ArUco 3D Pose", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cv2.destroyAllWindows()
picam2.stop()
