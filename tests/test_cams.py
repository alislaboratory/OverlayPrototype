from picamera2 import Picamera2
import cv2
import time

# Initialize both cameras
picam0 = Picamera2(0)
picam1 = Picamera2(1)

picam0.configure("preview")
picam1.configure("preview")

picam0.start()
picam1.start()
time.sleep(1)

while True:
    frame0 = picam0.capture_array()
    frame1 = picam1.capture_array()

    # Display both side-by-side
    cv2.imshow("Camera 0", frame0)
    cv2.imshow("Camera 1", frame1)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
picam0.stop()
picam1.stop()
