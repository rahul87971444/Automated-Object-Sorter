
from picamera2 import Picamera2
import cv2
import numpy as np
import time

# ================= CAMERA SETUP =================
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "BGR888", "size": (640, 480)}
)
picam2.configure(config)

picam2.set_controls({
    "AeEnable": True,
    "AwbEnable": True,
    "FrameRate": 20
})

picam2.start()
time.sleep(2)

# ================= ROI =================
ROI = 260

def detect_shape(frame):
    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2

    x1 = cx - ROI // 2
    y1 = cy - ROI // 2
    x2 = cx + ROI // 2
    y2 = cy + ROI // 2

    roi = frame[y1:y2, x1:x2].copy()

    # ================= WHITE MASK =================
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv,
        np.array([0, 0, 190]),
        np.array([180, 50, 255])
    )

    mask = cv2.GaussianBlur(mask, (9, 9), 2)

    # ================= CIRCLE DETECTION =================
    circles = cv2.HoughCircles(
        mask,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=100,
        param2=30,
        minRadius=20,
        maxRadius=120
    )

    shape = "No Object"

    if circles is not None:
        circles = np.uint16(np.around(circles))
        x, y, r = circles[0][0]
        cv2.circle(roi, (x, y), r, (0, 255, 0), 2)
        shape = "Circle"

    else:
        # ================= RECTANGLE DETECTION =================
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            cnt = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(cnt)

            if area > 4000:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)
                shape = "Rectangle"

    cv2.putText(
        roi, shape, (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 1,
        (0, 255, 0), 2
    )

    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
    frame[y1:y2, x1:x2] = roi

    return frame

# ================= MAIN LOOP =================
while True:
    frame = picam2.capture_array()
    output = detect_shape(frame)

    cv2.imshow("Shape Detection", output)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
