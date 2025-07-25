import cv2

def main():
    # 0 → first camera; change if your wide-angle is on a different index
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  

    # Try bumping up to 1280×720 or 1920×1080 (or whatever your cam supports)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    if not cap.isOpened():
        print("❌ Couldn't open camera")
        return

    # Read one frame to check size
    ret, frame = cap.read()
    if not ret:
        print("❌ Couldn't read frame")
        return

    h, w = frame.shape[:2]
    print(f"✅ Capturing at resolution: {w}×{h}")

    cv2.namedWindow("Wide-angle Feed", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Wide-angle Feed", w//2, h//2)  # start half-size

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Wide-angle Feed", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):  # ESC or 'q' to quit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
