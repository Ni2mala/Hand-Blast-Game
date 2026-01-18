import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks import python
max_value = 255

low_H =0
low_S =30
low_V =60

high_H=20
high_S=150
high_V=max_value
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("camera is not opened.")
    exit()

while True:
    ret, frame = camera.read()
    if not ret:
        print("frame is not captured properly")
        break
    hsv= cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    frame_threshold = cv2.inRange(hsv, (low_H,low_S, low_V), (high_H, high_S, high_V))
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    cleaned_mask = cv2.morphologyEx(frame_threshold,cv2.MORPH_OPEN, kernel)
    cv2.imshow("camera", frame)
    cv2.imshow("hsv frame", frame_threshold)
    cv2.imshow("cleaned_mask", cleaned_mask)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
