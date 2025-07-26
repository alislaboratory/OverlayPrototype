#!/usr/bin/env python3
import cv2
import numpy as np
import time
from picamera2 import Picamera2

# === CONFIGURATION ===
PATTERN_SIZE   = (9, 6)     # inner corners
SQUARE_SIZE_MM = 28.2       # mm per square
NUM_FRAMES     = 20         # captures needed
WIDTH, HEIGHT  = 640, 480   # preview resolution for speed
FPS            = 30         # target frame-rate
CAMERA_INDEX   = 0          # CSI port
# ======================

def main():
    # prepare object points
    objp = np.zeros((PATTERN_SIZE[0]*PATTERN_SIZE[1],3),np.float32)
    objp[:,:2] = (np.mgrid[0:PATTERN_SIZE[0],0:PATTERN_SIZE[1]].T
                   .reshape(-1,2) * SQUARE_SIZE_MM)
    objpoints, imgpoints = [], []

    # init camera in preview mode (fast)
    picam2 = Picamera2(camera_num=CAMERA_INDEX)
    preview_cfg = picam2.create_preview_configuration(
        main={"size": (WIDTH, HEIGHT), "format": "YUV420"},
        controls={"FrameRate": FPS}
    )
    picam2.configure(preview_cfg)
    picam2.start()
    time.sleep(1)  # let AE settle

    cv2.namedWindow("Calib", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Calib", WIDTH//2, HEIGHT//2)
    print(f"Press 'c' when checkerboard is detected.  Need {NUM_FRAMES} captures.")

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                30, 0.001)
    captured = 0
    t0 = time.time()

    while captured < NUM_FRAMES:
        frame = picam2.capture_array("main")
        frame = cv2.rotate(frame, cv2.ROTATE_180)  # flip
        gray = cv2.cvtColor(frame, cv2.COLOR_YUV2GRAY_YUV420)
        found, corners = cv2.findChessboardCorners(
            gray, PATTERN_SIZE,
            flags=cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
        )

        disp = frame.copy()
        if found:
            cv2.drawChessboardCorners(disp, PATTERN_SIZE, corners, found)
        cv2.putText(disp,
                    f"{captured}/{NUM_FRAMES}",
                    (10,30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0,255,0), 2)
        cv2.imshow("Calib", disp)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c') and found:
            corners2 = cv2.cornerSubPix(
                gray, corners, (11,11), (-1,-1), criteria
            )
            objpoints.append(objp.copy())
            imgpoints.append(corners2)
            captured += 1
            print(f"Captured {captured}/{NUM_FRAMES}")
        elif key in (27, ord('q')):
            print("Aborting.")
            picam2.stop()
            cv2.destroyAllWindows()
            return

    fps = captured / (time.time() - t0)
    print(f"Effective capture rate: {fps:.1f} FPS")

    picam2.stop()
    cv2.destroyAllWindows()

    # calibrate
    ret, K, dist, _, _ = cv2.calibrateCamera(
        objpoints, imgpoints, (WIDTH, HEIGHT), None, None
    )
    print(f"Reproj error: {ret:.4f}")
    print("K =\n", K)
    print("dist =\n", dist.ravel())
    np.save("wide_K.npy", K)
    np.save("wide_dist.npy", dist)
    print("Saved wide_K.npy & wide_dist.npy")

if __name__ == "__main__":
    main()
