'''
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Very important: download the .task model file first!
# https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models
# Recommended: hand_landmarker.task (full model)

BaseOptions = python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

model_path = "gesture_recognizer.task"

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,   # or IMAGE / LIVE_STREAM
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

landmarker = HandLandmarker.create_from_options(options)

# Example usage in video loop
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Convert to RGB (MediaPipe expects RGB)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    # Timestamp in milliseconds (very important for VIDEO mode!)
    timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

    detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

    # Now you can draw landmarks...
    # (use detection_result.hand_landmarks, .handedness, etc)

    # For drawing you can use the new drawing functions or write your own
    cv2.imshow("MediaPipe Hands - New API", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''

import cv2
import random
import time
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


#mediappipe gesture setup

model_path = "gesture_recognizer.task"
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = vision.GestureRecognizer
GestureRecognizerOptions = vision.GestureRecognizerOptions
VisionRunningMode = vision.RunningMode

options = GestureRecognizerOptions(
    base_options = BaseOptions(model_asset_path= model_path),
    running_mode = VisionRunningMode.IMAGE
)
recognizer = GestureRecognizer.create_from_options(options)

#game setup

WIDTH, HEIGHT = 640, 480
circles=[]
score =0
last_shot_time =0
SHOT_COOLDOWN =0.6

def spawn_circle():
    return{
    'x': random.randint(50, WIDTH - 50),
    'y' : random.randint(50, HEIGHT - 50),
    'r': random.randint(20,35),
    'vx':random.choice([-3,-2,-1,1,2,3]),
    'vy':random.choice([-3,-2,-1,1,2,3])
    }

for _ in range(5):
    circles.append(spawn_circle())


#webcam
cap = cv2.VideoCapture(0)
cap.set(3, WIDTH)
cap.set(4,HEIGHT)
print("open palm = AIM, fist = SHOOT")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame =cv2.flip(frame, 1)
    rgb=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = recognizer.recognize(mp_image)
    gesture = "No gesture"
    if result.gestures:
        gesture_name = result.gestures[0][0].category_name
        cv2.putText(frame, f"Gesture: {gesture_name}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
#SHOOTING LOGIC
shoot = False
if gesture_name =="Closed_Fist":
    if time.time() - last_shot_time > SHOT_COOLDOWN:
        shoot = True
        last_Shot_time = time.time()

#center crosshair
cx, cy = WIDTH //2, HEIGHT //2
cv2.CIRCLE(frame, (cx, cy), 5, (0,255,0), -1)

#update and draw circles
for circle in circles[:]:
    circle["x"] += circle["vx"]
    circle["y"] += circle["vy"]

    if circle['x']<0 or circle['x']>WIDTH:
        circle['VX']*+ -1
    if circle['y']<0 or circle['y']>HEIGHT:
        circle['vy']*=-1

    #hit detection
    if shoot:
        dist = np.sqrt((circle['x'] - cx)**2 + (circle['y'] - cy)**2)
        if dist< circle['r']:
            circles.remove(circle)
            circles.append(spawn_circle())
            score += 1
            continue

    cv2,circle(frame,
               (circle['x'], circle['y']),
               circle['r'],
               (255, 0, 0), 3)

    cv2.imshow("hand shooting game", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
   





    