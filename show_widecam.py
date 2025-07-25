#!/usr/bin/env python3
import cv2
from picamera2 import Picamera2, Preview

def main():
    # 1. Initialize Picamera2
    picam2 = Picamera2()

    # 2. Configure for video capture at your desired resolution
    video_config = picam2.create_video_configuration(
        main={"size": (1920, 1080), "format": "RGB888"}
    )
    picam2.configure(video_config)

    # 3. Start the camera
    picam2.start()

    # 4. Create an OpenCV window
    cv2.namedWindow("CSI Camera", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("CSI Camera", 960, 540)  # start at half size

    try:
        while True:
            # 5. Capture a frame as a numpy array
            frame = picam2.capture_array("main")

            # 6. Show it in OpenCV
            cv2.imshow("CSI Camera", frame)

            # 7. Quit on 'q' or ESC
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord('q')):
                break

    finally:
        # 8. Clean up
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
