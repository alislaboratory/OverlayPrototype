import cv2
from picamera2 import Picamera2

# === CONFIGURE THIS ===
CAMERA_INDEX = 1    # 0 = wide-angle CSI port, 1 = normal CSI port
WIDTH, HEIGHT = 1280, 720
# ======================

# Initialize PiCamera2 on the selected CSI port
picam2 = Picamera2(camera_num=CAMERA_INDEX)

# Configure for video capture
video_config = picam2.create_video_configuration(
    main={"size": (WIDTH, HEIGHT), "format": "RGB888"}
)
picam2.configure(video_config)
picam2.start()

# Set up an OpenCV window
cv2.namedWindow("CSI Camera", cv2.WINDOW_NORMAL)
cv2.resizeWindow("CSI Camera", WIDTH // 2, HEIGHT // 2)

print(f"Streaming CSI-{CAMERA_INDEX} at {WIDTH}×{HEIGHT}. Press Q or ESC to quit.")

try:
    while True:
        frame = picam2.capture_array("main")
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        cv2.imshow("CSI Camera", frame)
        if cv2.waitKey(1) & 0xFF in (27, ord('q')):
            break
finally:
    picam2.stop()
    cv2.destroyAllWindows()
