import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks import python

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("camera is not opened.")
    exit()

while True:
    ret, frame = camera.read()
    if not ret:
        print("frame is not captured properly")
        break
    h, w, c = frame.shape
    print(h, w, c)

    cx = w // 2
    cy = h // 2

    for x in range(0, w, 50):
        cv2.line(frame, (x, 0), (x, h), (50, 50, 50), 1)

    for y in range(0, h, 50):
        cv2.line(frame, (0, y), (w, y), (50, 50, 50), 1)

    # Vertical center line
    cv2.line(frame, (w//2, 0), (w//2, h), (0, 255, 0), 2)

    # Horizontal center line
    cv2.line(frame, (0, h//2), (w, h//2), (0, 255, 0), 2)
    import cv2
    # Draw a red crosshair at (x=100, y=50)
    cv2.drawMarker(frame, (100, 50), (0, 0, 255), cv2.MARKER_CROSS, markerSize=20, thickness=2)
    cx, cy =100, 100

    cv2.imshow("camera", frame)
    key = cv2.waitKey(1)
    if key ==ord("d"):
        cx +=10
    if key ==ord('a'):
        cx -= 10
    if key ==ord('s'):
        cx +=10
    if key ==ord('w'):
        cy -=10
    elif key ==ord('q'):
        break
    #draw crosshair at (cx, cy)
    cv2.line(frame, (cx-20, cy),(cx+20, cy), (0,255,0), 2)
    cv2.line(frame,(cx, cy-20),(cx, cy+20),(0,255,0),2)
    cv2.circle(frame, (cx, cy), 5, (0,255, 0), -1)
    #display position
    cv2.putText(frame, f"position:({cx},{cy})", (10,30), 
                cv2.FONT_HERSHEY_SIMPLEX,0.7, (0,255,0), 2)

    cv2.imshow("crosshair", frame)


    

camera.release()
cv2.destroyAllWindows()
