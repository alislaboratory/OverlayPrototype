#!/usr/bin/env python3
import cv2
from picamera2 import Picamera2

# === CONFIGURATION ===
FRONT_CAMERA_INDEX    = 0      # CSI port for your wide-angle “front” camera
OBSERVER_CAMERA_INDEX = 1      # CSI port for your normal “observer” camera

# Desired resolutions (you can tweak these)
FRONT_WIDTH, FRONT_HEIGHT   = 1280, 720
OBS_WIDTH, OBS_HEIGHT       = 1280, 720
# ======================

# Initialize both Picamera2 instances
front_cam = Picamera2(camera_num=FRONT_CAMERA_INDEX)
obs_cam   = Picamera2(camera_num=OBSERVER_CAMERA_INDEX)

# Configure each for video capture
front_config = front_cam.create_video_configuration(
    main={"size": (FRONT_WIDTH, FRONT_HEIGHT), "format": "RGB888"}
)
obs_config = obs_cam.create_video_configuration(
    main={"size": (OBS_WIDTH, OBS_HEIGHT), "format": "RGB888"}
)
front_cam.configure(front_config)
obs_cam.configure(obs_config)

# Start streaming
front_cam.start()
obs_cam.start()

# Create resizable OpenCV windows
cv2.namedWindow("Front Camera",    cv2.WINDOW_NORMAL)
cv2.resizeWindow("Front Camera",    FRONT_WIDTH//2, FRONT_HEIGHT//2)
cv2.namedWindow("Observer Camera", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Observer Camera", OBS_WIDTH//2,   OBS_HEIGHT//2)

print("Streaming both cameras. Press Q or ESC to quit.")

try:
    while True:
        # Grab frames
        front_frame = front_cam.capture_array("main")
        obs_frame   = obs_cam.capture_array("main")

        # Flip both 180° (upside-down → right-side-up)
        front_frame = cv2.rotate(front_frame, cv2.ROTATE_180)
        obs_frame   = cv2.rotate(obs_frame,   cv2.ROTATE_180)

        # Show them
        cv2.imshow("Front Camera",    front_frame)
        cv2.imshow("Observer Camera", obs_frame)

        # Exit if user presses ESC or 'q'
        if cv2.waitKey(1) & 0xFF in (27, ord('q')):
            break

finally:
    front_cam.stop()
    obs_cam.stop()
    cv2.destroyAllWindows()
