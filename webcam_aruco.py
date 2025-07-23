import cv2
import time

def main():
    # 1) Open the default webcam (change 0 if you have multiple cameras)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # 2) Load the 6×6_250 ArUco dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

    # 3) Create detector parameters (use defaults, but you can tweak fields on this object)
    parameters = cv2.aruco.DetectorParameters()

    # 4) Build the detector
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    prev_time = time.time()

    print("Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # 5) Detect markers (works on color or grayscale internally)
        corners, ids, rejected = detector.detectMarkers(frame)

        # 6) If any markers found, draw outlines and IDs
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids, borderColor=(0,255,0))
        
        cur_time = time.time()
        dt = cur_time - prev_time
        prev_time = cur_time
        fps = 1.0 / dt if dt > 0 else 0.0
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

        # 7) Show the annotated frame
        cv2.imshow('Aruco Detection (OpenCV 4.12.0)', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 8) Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
