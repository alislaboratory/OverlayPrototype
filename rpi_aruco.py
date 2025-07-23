import time
import cv2
from picamera2 import Picamera2

def main():
    # --- 1) Configure the CSI camera via Picamera2 ---
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"format": "RGB888", "size": (640, 480)}
    )
    picam2.configure(config)
    picam2.start()

    # --- 2) Setup ArUco detector (6×6_250) ---
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    prev_time = time.time()
    print("Press 'q' to quit.")

    while True:
        # --- 3) Capture a frame and convert to BGR for OpenCV ---
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # --- 4) Detect markers ---
        corners, ids, _ = detector.detectMarkers(frame)

        if ids is not None:
            # 5a) Draw thick green outlines
            for marker_corners in corners:
                pts = marker_corners.reshape((4, 2)).astype(int)
                for i in range(4):
                    pt1 = tuple(pts[i])
                    pt2 = tuple(pts[(i + 1) % 4])
                    cv2.line(frame, pt1, pt2, (0, 255, 0), thickness=4)
            # 5b) Label with marker ID
            for marker_corners, marker_id in zip(corners, ids.flatten()):
                x, y = marker_corners.reshape((4, 2)).astype(int)[0]
                cv2.putText(
                    frame,
                    str(int(marker_id)),
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )

        # --- 6) Compute & overlay FPS ---
        cur_time = time.time()
        fps = 1.0 / (cur_time - prev_time) if cur_time != prev_time else 0.0
        prev_time = cur_time
        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # --- 7) Show and handle quit ---
        cv2.imshow("Aruco Detection (RPi Camera)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # --- 8) Cleanup ---
    cv2.destroyAllWindows()
    picam2.stop()

if __name__ == "__main__":
    main()
