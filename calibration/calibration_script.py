import cv2
import numpy as np
import time
from picamera2 import Picamera2
import os

# === Configuration ===
CHECKERBOARD = (9, 6)
SQUARE_SIZE = 28.2  # mm
NUM_IMAGES = 15
DELAY_BETWEEN_CAPTURES = 2  # seconds

SAVE_FILE = "camera_calibration.yaml"
CAPTURE_DIR = "captured_images"

# === Setup output directory ===
os.makedirs(CAPTURE_DIR, exist_ok=True)

# === Prepare object points ===
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

objpoints = []  # 3D points
imgpoints = []  # 2D points

# === Initialize camera ===
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
time.sleep(2)  # Allow warm-up

print("Starting image capture for calibration...")

captured = 0
while captured < NUM_IMAGES:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        print(f"[{captured + 1}/{NUM_IMAGES}] Checkerboard found. Capturing...")

        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1),
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        imgpoints.append(corners2)

        img_with_corners = cv2.drawChessboardCorners(frame.copy(), CHECKERBOARD, corners2, ret)
        filename = os.path.join(CAPTURE_DIR, f"img_{captured+1:02d}.jpg")
        cv2.imwrite(filename, img_with_corners)

        cv2.imshow('Captured', img_with_corners)
        cv2.waitKey(500)

        captured += 1
        time.sleep(DELAY_BETWEEN_CAPTURES)
    else:
        print("Checkerboard not detected. Try adjusting position...")
        cv2.imshow('Preview', frame)
        cv2.waitKey(100)

cv2.destroyAllWindows()
picam2.stop()

# === Calibration ===
print("Calibrating camera...")
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

print("Calibration complete.")
print("Camera matrix:\n", camera_matrix)
print("Distortion coefficients:\n", dist_coeffs)

# === Save calibration ===
fs = cv2.FileStorage(SAVE_FILE, cv2.FILE_STORAGE_WRITE)
fs.write("camera_matrix", camera_matrix)
fs.write("distortion_coefficients", dist_coeffs)
fs.write("reprojection_error", ret)
fs.release()

print(f"Calibration data saved to '{SAVE_FILE}'")
