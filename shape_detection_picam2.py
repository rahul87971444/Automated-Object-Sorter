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

# ? KEEP AUTO EXPOSURE (CRITICAL FOR LOW LIGHT)
picam2.set_controls({
    "AeEnable": True,
    "AwbEnable": True
})

picam2.start()
time.sleep(2)

print("? Camera running in AUTO mode (low light safe)")

# ================= ROI SETTINGS =================
ROI_WIDTH = 260
ROI_HEIGHT = 260

# ================= SHAPE DETECTION =================
def detect_shape_roi(frame):
    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2

    x1 = max(0, cx - ROI_WIDTH // 2)
    y1 = max(0, cy - ROI_HEIGHT // 2)
    x2 = min(w, cx + ROI_WIDTH // 2)
    y2 = min(h, cy + ROI_HEIGHT // 2)

    roi = frame[y1:y2, x1:x2].copy()

    # --------- PREPROCESSING ----------
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # Boost contrast for low light
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=20)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # ? ADAPTIVE threshold (LOW LIGHT SAFE)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    shape = "No Object"

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)

        if area > 3000:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)

            if len(approx) == 4:
                x, y, w2, h2 = cv2.boundingRect(approx)
                ratio = w2 / float(h2)
                shape = "Square" if 0.9 < ratio < 1.1 else "Rectangle"
            else:
                circularity = 4 * np.pi * area / (peri * peri)
                shape = "Circle" if circularity > 0.75 else "Unidentified"

            cv2.drawContours(roi, [approx], -1, (0, 255, 0), 2)
            cv2.putText(
                roi, shape, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (0, 255, 0), 2
            )

    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
    frame[y1:y2, x1:x2] = roi

    return frame, shape

# ================= MAIN LOOP =================
print("? Low-light WHITE object detection | Press Q to quit")

while True:
    frame = picam2.capture_array()
    output, detected_shape = detect_shape_roi(frame)
    cv2.imshow("White Object Shape Detection (Low Light)", output)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
