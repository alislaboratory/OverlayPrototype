#!/usr/bin/env python3
import cv2
import numpy as np
from picamera2 import Picamera2
import time

# === CONFIGURATION ===
PATTERN_SIZE   = (9, 6)    # inner corners per row, column
SQUARE_SIZE_MM = 28.2      # size of a chessboard square in millimeters
NUM_FRAMES     = 20        # number of successful boards to capture
WIDTH, HEIGHT  = 1280, 720 # capture resolution
# ======================

def main():
    # Prepare object points in real-world space: (0,0,0), (28.2,0,0), (56.4,0,0), ...
    objp = np.zeros((PATTERN_SIZE[0]*PATTERN_SIZE[1], 3), np.float32)
    objp[:, :2] = (np.mgrid[0:PATTERN_SIZE[0], 0:PATTERN_SIZE[1]].T
                   .reshape(-1, 2) * SQUARE_SIZE_MM)

    objpoints = []  # 3D points
    imgpoints = []  # 2D points

    # Initialize PiCamera2
    picam2 = Picamera2(camera_num=0)  # change to 1 if using CSI-1
    config = picam2.create_still_configuration(main={"size": (WIDTH, HEIGHT), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    time.sleep(2)  # let auto-exposure settle

    cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Calibration", WIDTH//2, HEIGHT//2)
    print(f"Press 'c' to capture board when it's fully visible. Need {NUM_FRAMES} frames.")

    while len(objpoints) < NUM_FRAMES:
        frame = picam2.capture_array("main")
        gray  = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        found, corners = cv2.findChessboardCorners(
            gray, PATTERN_SIZE,
            flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        )

        display = frame.copy()
        if found:
            cv2.drawChessboardCorners(display, PATTERN_SIZE, corners, found)

        cv2.putText(display,
                    f"Captured: {len(objpoints)}/{NUM_FRAMES}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow("Calibration", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c') and found:
            # Refine and store points
            corners2 = cv2.cornerSubPix(
                gray, corners, winSize=(11,11), zeroZone=(-1,-1),
                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                          30, 0.001)
            )
            objpoints.append(objp.copy())
            imgpoints.append(corners2)
            print(f"✔ Captured frame {len(objpoints)}/{NUM_FRAMES}")
        elif key in (27, ord('q')):
            print("Calibration aborted by user.")
            picam2.stop()
            cv2.destroyAllWindows()
            return

    picam2.stop()
    cv2.destroyAllWindows()

    # Perform calibration
    ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, (WIDTH, HEIGHT), None, None
    )

    print(f"\nReprojection error: {ret:.4f} pixels")
    print("Intrinsic matrix K:")
    print(K)
    print("Distortion coefficients:")
    print(dist.ravel())

    # Save results
    np.save("wide_K.npy", K)
    np.save("wide_dist.npy", dist)
    print("\nSaved wide_K.npy and wide_dist.npy")

if __name__ == "__main__":
    main()
