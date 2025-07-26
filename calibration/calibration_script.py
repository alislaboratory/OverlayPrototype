#!/usr/bin/env python3
import cv2
import numpy as np
import time
from picamera2 import Picamera2

# === CONFIGURATION ===
PATTERN_SIZE   = (9, 6)     # inner corners
SQUARE_SIZE_MM = 28.2       # mm per square
NUM_FRAMES     = 20         # captures needed
WIDTH, HEIGHT  = 640, 480   # preview resolution
FPS            = 30         # target frame rate
CAMERA_INDEX   = 0          # CSI port index
# ======================

def main():
    # prepare object points
    objp = np.zeros((PATTERN_SIZE[0]*PATTERN_SIZE[1],3),np.float32)
    objp[:,:2] = (np.mgrid[0:PATTERN_SIZE[0],0:PATTERN_SIZE[1]].T
                   .reshape(-1,2) * SQUARE_SIZE_MM)
    objpoints, imgpoints = [], []

    # init Picamera2 in fast preview (YUV420 planar)
    picam2 = Picamera2(camera_num=CAMERA_INDEX)
    preview_cfg = picam2.create_preview_configuration(
        main={"size": (WIDTH, HEIGHT), "format": "YUV420"},
        controls={"FrameRate": FPS}
    )
    picam2.configure(preview_cfg)
    picam2.start()
    time.sleep(1)  # let exposure settle

    cv2.namedWindow("Calib", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Calib", WIDTH//2, HEIGHT//2)
    print(f"Press 'c' when checkerboard is detected. Need {NUM_FRAMES} captures.")

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    captured = 0
    t0 = time.time()

    while captured < NUM_FRAMES:
        # grab the YUV420 frame (shape will be (HEIGHT*3/2, WIDTH))
        frame_yuv = picam2.capture_array("main")
        # flip entire buffer so the Y plane is also rotated
        frame_yuv = cv2.rotate(frame_yuv, cv2.ROTATE_180)

        # extract Y (luma) plane: first HEIGHT rows
        gray = frame_yuv[:HEIGHT, :]

        # detect corners on the gray image
        found, corners = cv2.findChessboardCorners(
            gray, PATTERN_SIZE,
            flags=cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
        )

        # for display, convert gray?BGR so we can draw colored overlays
        disp = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        if found:
            cv2.drawChessboardCorners(disp, PATTERN_SIZE, corners, found)

        cv2.putText(disp, f"{captured}/{NUM_FRAMES}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow("Calib", disp)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c') and found:
            corners2 = cv2.cornerSubPix(
                gray, corners, (11,11), (-1,-1), criteria
            )
            objpoints.append(objp.copy())
            imgpoints.append(corners2)
            captured += 1
            print(f"? Captured {captured}/{NUM_FRAMES}")
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
    print(f"\nReprojection error: {ret:.4f}")
    print("Intrinsic matrix K:\n", K)
    print("Distortion coeffs:\n", dist.ravel())

    np.save("wide_K.npy", K)
    np.save("wide_dist.npy", dist)
    print("\nSaved wide_K.npy & wide_dist.npy")

if __name__ == "__main__":
    main()
