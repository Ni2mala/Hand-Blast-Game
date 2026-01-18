import cv2
import random
import time
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- Setup ---
model_path = "gesture_recognizer.task" # Ensure you have this file!
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = vision.GestureRecognizer
GestureRecognizerOptions = vision.GestureRecognizerOptions
VisionRunningMode = vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE
)
# Fix: create_from_options must be lowercase
recognizer = GestureRecognizer.create_from_options(options)

WIDTH, HEIGHT = 640, 480
circles = []
score = 0
last_shot_time = 0
SHOT_COOLDOWN = 0.5 

def spawn_circle():
    return {
        'x': random.randint(50, WIDTH - 50),
        'y': random.randint(50, HEIGHT - 50),
        'r': random.randint(20, 35),
        'vx': random.choice([-3, -2, 2, 3]),
        'vy': random.choice([-3, -2, 2, 3])
    }

for _ in range(5):
    circles.append(spawn_circle())

cap = cv2.VideoCapture(0)
# Initialize cursor at center
cx, cy = WIDTH // 2, HEIGHT // 2

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = recognizer.recognize(mp_image)
    
    shoot = False
    if result.gestures and result.hand_landmarks:
        gesture_name = result.gestures[0][0].category_name
        
        # Get Index Finger Tip (Landmark 8) for the crosshair
        # We use hand_landmarks[0] for the first hand detected
        idx_tip = result.hand_landmarks[0][8]
        cx, cy = int(idx_tip.x * WIDTH), int(idx_tip.y * HEIGHT)

        # Trigger Action: Pointing_Up
        if gesture_name == "Pointing_Up":
            if time.time() - last_shot_time > SHOT_COOLDOWN:
                shoot = True
                last_shot_time = time.time()
        
        cv2.putText(frame, f"Gesture: {gesture_name}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Draw Crosshair at finger position
    cross_color = (0, 0, 255) if shoot else (0, 255, 0)
    cv2.circle(frame, (cx, cy), 10, cross_color, -1)

    # Update and Draw circles
    for circle in circles[:]:
        circle['x'] += circle['vx']
        circle['y'] += circle['vy']

        # Bouncing (Fix: VX to vx)
        if circle['x'] - circle['r'] < 0 or circle['x'] + circle['r'] > WIDTH:
            circle['vx'] *= -1
        if circle['y'] - circle['r'] < 0 or circle['y'] + circle['r'] > HEIGHT:
            circle['vy'] *= -1

        # Hit detection
        if shoot:
            dist = np.sqrt((circle['x'] - cx)**2 + (circle['y'] - cy)**2)
            if dist < circle['r']:
                circles.remove(circle)
                circles.append(spawn_circle())
                score += 1
                continue

        cv2.circle(frame, (int(circle['x']), int(circle['y'])), 
                   circle['r'], (255, 0, 0), 3)

    cv2.putText(frame, f"Score: {score}", (WIDTH-150, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow("Hand Shooting Game", frame)
    if cv2.waitKey(1) & 0xFF == 27: # ESC key
        break

cap.release()
cv2.destroyAllWindows()