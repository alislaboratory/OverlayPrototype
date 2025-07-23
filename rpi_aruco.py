import time
import cv2
from picamera2 import Picamera2

def main():
    # --- 1) Configure the Pi Camera ---
    picam2 = Picamera2()
    cfg = picam2.create_preview_configuration(
        main={"format": "RGB888", "size": (640, 480)}
    )
    picam2.configure(cfg)
    picam2.start()

    # --- 2) Prepare ArUco dictionary & detector parameters ---
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    params     = cv2.aruco.DetectorParameters()  # default tuning

    prev_time = time.time()
    print("Press 'q' to quit.")

    while True:
        # --- 3) Capture a frame & convert to BGR ---
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # --- 4) Detect markers via the functional API ---
        corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=params)

        # --- 5) If found, draw thick outlines + label them ---
        if ids is not None:
            for pts in corners:
                pts = pts.reshape((4, 2)).astype(int)
                for i in range(4):
                    pt1 = tuple(pts[i])
                    pt2 = tuple(pts[(i + 1) % 4])
                    cv2.line(frame, pt1, pt2, (0, 255, 0), thickness=4)
            for pts, mid in zip(corners, ids.flatten()):
                x, y = pts.reshape((4, 2)).astype(int)[0]
                cv2.putText(
                    frame,
                    str(int(mid)),
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

        # --- 6) Compute & overlay FPS ---
        now = time.time()
        fps = 1.0 / (now - prev_time) if now != prev_time else 0.0
        prev_time = now
        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        # --- 7) Display & quit on 'q' ---
        cv2.imshow("Aruco Detection (Pi Camera)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # --- 8) Cleanup ---
    cv2.destroyAllWindows()
    picam2.stop()

if __name__ == "__main__":
    main()
