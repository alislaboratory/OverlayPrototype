# Calibrate Picamera2 with flipped, high-FPS video stream

import cv2
import numpy as np
from picamera2 import Picamera2
import time

# === CONFIGURATION ===
PATTERN_SIZE   = (9, 6)    # inner corners per row, column
SQUARE_SIZE_MM = 28.2      # size of a chessboard square in millimeters
NUM_FRAMES     = 20        # number of successful boards to capture
WIDTH, HEIGHT  = 1280, 720 # capture resolution
CAMERA_INDEX   = 0         # 0 or 1 for CSI ports
# ======================

def main():
    # Prepare object points
    objp = np.zeros((PATTERN_SIZE[0] * PATTERN_SIZE[1], 3), np.float32)
    objp[:, :2] = (np.mgrid[0:PATTERN_SIZE[0], 0:PATTERN_SIZE[1]].T
                   .reshape(-1, 2) * SQUARE_SIZE_MM)

    objpoints, imgpoints = [], []

    # Initialize PiCamera2 in video mode for higher FPS
    picam2 = Picamera2(camera_num=CAMERA_INDEX)
    video_config = picam2.create_video_configuration(
        main={"size": (WIDTH, HEIGHT), "format": "RGB888"}
    )
    picam2.configure(video_config)
    picam2.start()
    time.sleep(2)  # warm-up

    # Sub-pixel refinement criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                30, 0.001)

    cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Calibration", WIDTH // 2, HEIGHT // 2)
    print(f"Press 'c' to capture when board is detected. Need {NUM_FRAMES} frames.")

    while len(objpoints) < NUM_FRAMES:
        frame = picam2.capture_array("main")
        # Flip 180°
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        found, corners = cv2.findChessboardCorners(
            gray, PATTERN_SIZE,
            flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        )

        disp = frame.copy()
        if found:
            cv2.drawChessboardCorners(disp, PATTERN_SIZE, corners, found)

        cv2.putText(disp,
                    f"Captured: {len(objpoints)}/{NUM_FRAMES}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow("Calibration", disp)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c') and found:
            corners2 = cv2.cornerSubPix(
                gray, corners, winSize=(11,11), zeroZone=(-1,-1),
                criteria=criteria
            )
            objpoints.append(objp.copy())
            imgpoints.append(corners2)
            print(f"? Frame {len(objpoints)}/{NUM_FRAMES}")
        elif key in (27, ord('q')):
            print("Aborted by user.")
            picam2.stop()
            cv2.destroyAllWindows()
            return

    picam2.stop()
    cv2.destroyAllWindows()

    # Calibration
    ret, K, dist, _, _ = cv2.calibrateCamera(
        objpoints, imgpoints, (WIDTH, HEIGHT), None, None
    )
    print(f"\nReprojection error: {ret:.4f}")
    print("Intrinsic matrix K:\n", K)
    print("Distortion coeffs:\n", dist.ravel())

    np.save("wide_K.npy", K)
    np.save("wide_dist.npy", dist)
    print("\nSaved wide_K.npy & wide_dist.npy")

if __name__ == "__main__":
    main()

