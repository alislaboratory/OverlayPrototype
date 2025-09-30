# 1. Find the 3D coordinates of the center of the arUco code relative to the front-facing camera. ----- DONE!
# 2. Find the 3D coordinates of the center of the arUco code relative to the observer camera.
# 3. Find the point of intersection between display and this vector.
# 4. Draw a pixel at the point of intersection.
from picamera2 import Picamera2
import cv2
import numpy as np
import time
import hardware
import subprocess
import threading

# ------------------------------------------------------------
# Observer camera launcher (runs rpicam-hello in a safe thread)
# ------------------------------------------------------------
class _CameraProcessThread:
    """
    Runs a long-lived camera command (rpicam-hello) in a background thread
    and shuts it down cleanly on request.
    """
    def __init__(self, cmd):
        self.cmd = cmd
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._proc = None

    def start(self):
        self._thread.start()

    def _run(self):
        try:
            # Start the camera process
            self._proc = subprocess.Popen(self.cmd)
            # Periodically check for stop signal or unexpected exit
            while not self._stop_event.is_set():
                if self._proc.poll() is not None:
                    # Process exited unexpectedly; leave thread
                    break
                time.sleep(0.2)
        finally:
            # Ensure process is terminated on exit
            self._terminate_proc()

    def _terminate_proc(self):
        if self._proc is not None and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            except Exception:
                # Last-resort kill if anything else goes wrong
                try:
                    self._proc.kill()
                except Exception:
                    pass
        self._proc = None

    def stop(self):
        # Signal the thread to stop and wait a moment
        self._stop_event.set()
        self._thread.join(timeout=5)
        # Double-ensure the process is gone
        self._terminate_proc()

def start_observer_camera():
    """
    Public helper that starts the observer camera preview in a background thread.
    Returns a controller with .stop() to shut it down.
    """
    cmd = ["rpicam-hello", "--camera", "1", "--vflip", "--timeout", "0"]
    controller = _CameraProcessThread(cmd)
    controller.start()
    print("OverlayPT: Observer camera started in a background thread.")
    return controller
# ------------------------------------------------------------

# ADJUSTMENTS - all in meters
CALIB_YAML    = "calibration/camera_calibration.yaml"  
MARKER_LENGTH = 0.1               # marker side length in meters
OBSERVER_FROM_FF = np.array([0.0383,0,0.0436]) # this is the observer camera from the front-facing in meters
DISPLAY_FROM_OBSERVER = np.array([-0.005,0,0.0383]) # how far the center of the display is from the camera
SCREEN_ACTIVE_AREA = np.array([0.04204, 0.02722]) # how large the screen size is
DISPLAY_RESOLUTION = (128,56) # transparent pixels of the screen (some are cut off - true size is 64 pixels vertically)
# ----------------------------------------------

# Load camera calibration from YAML
fs = cv2.FileStorage(CALIB_YAML, cv2.FILE_STORAGE_READ)
if not fs.isOpened():
    raise IOError(f"OverlayPT: Cannot open calibration file: {CALIB_YAML}")
camera_matrix = fs.getNode("camera_matrix").mat()
dist_coeffs   = fs.getNode("distortion_coefficients").mat()
fs.release()

# Initialise Picamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size   = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()
time.sleep(1)

# Initialise the display
display = hardware.TransparentDisplay()

# Prepare ArUco detector
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
params     = cv2.aruco.DetectorParameters_create()

# --- Start observer camera (background rpicam-hello) ---
observer_cam = start_observer_camera()

print("OverlayPT: Camera thread running")
print("Press 'q' to quit...")

try:
    while True:
        # Capture & preprocess
        frame = picam2.capture_array()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        gray  = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # clear the display
        display.clear()

        # Detect markers
        corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=params)

        if ids is not None:
            # Estimate pose
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, MARKER_LENGTH, camera_matrix, dist_coeffs
            )

            for i, marker_id in enumerate(ids.flatten()):
                rvec = rvecs[i][0]
                tvec = tvecs[i][0]  # (x, y, z) in meters

                x, y, z = tvec # Here are our 3D coords
                corner_pt = tuple(corners[i][0][0].astype(int))

                ##### Overlay Code #######
                aruco_from_observer = hardware.from_observer(np.array([x,y,z]), OBSERVER_FROM_FF) # this will give us the aruco code's position relative to the observer
                print(f"OverlayPT: Aruco's position from observer cam: f{aruco_from_observer}")
                pixel_x, pixel_y = hardware.intersect_display(DISPLAY_FROM_OBSERVER, SCREEN_ACTIVE_AREA[0], SCREEN_ACTIVE_AREA[1], DISPLAY_RESOLUTION, aruco_from_observer) # this gives us the pixel that the observer sees which will be the midpoint of the code from their perspective
                display.point(np.array([128-pixel_x, pixel_y])) # Draw the point on the dispaly

        # Show result
        cv2.imshow("ArUco 3D Pose", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("OverlayPT: Exiting")
            break

finally:
    # Cleanup in a predictable order
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
    try:
        picam2.stop()
    except Exception:
        pass
    try:
        observer_cam.stop()   # <— shuts down rpicam-hello cleanly
    except Exception:
        pass
