import cv2
import random
import time
import numpy as np
import mediapipe as mp

# --- Setup MediaPipe Tasks ---
model_path = "gesture_recognizer.task"
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE
)
recognizer = GestureRecognizer.create_from_options(options)

# --- Game Variables ---
WIDTH, HEIGHT = 640, 480
circles = []
score = 0
last_shot_time = 0
SHOT_COOLDOWN = 0.4 

def spawn_circle():
    return {
        'x': random.randint(50, WIDTH - 50),
        'y': random.randint(50, HEIGHT - 50),
        'r': random.randint(20, 35),
        'vx': random.choice([-4, -2, 2, 4]),
        'vy': random.choice([-4, -2, 2, 4]),
        'color': (random.randint(50, 255), random.randint(50, 255), 255) # Random neon colors
    }

for _ in range(6): # Start with 6 targets
    circles.append(spawn_circle())

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    # AI Detection
    result = recognizer.recognize(mp_image)
    
    # CREATE BLACK BACKGROUND
    canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    
    shoot = False
    cx, cy = 0, 0 # Crosshair coordinates

    if result.hand_landmarks:
        # AIMING: Follow the Index Finger (Landmark 8)
        hand = result.hand_landmarks[0]
        idx_tip = hand[8]
        thmb_tip = hand[4]
        
        cx, cy = int(idx_tip.x * WIDTH), int(idx_tip.y * HEIGHT)
        tx, ty = int(thmb_tip.x * WIDTH), int(thmb_tip.y * HEIGHT)

        # SHOOTING: Distance calculation for "Thumb Pull"
        dist = np.sqrt((cx - tx)**2 + (cy - ty)**2)
        
        # If thumb is close to index (pinching/pulling trigger)
        if dist < 40: 
            if time.time() - last_shot_time > SHOT_COOLDOWN:
                shoot = True
                last_shot_time = time.time()

    # --- DRAWING ON THE BLACK CANVAS ---
    # 1. Update and Draw Filled Targets
    for circle in circles[:]:
        circle['x'] += circle['vx']
        circle['y'] += circle['vy']

        # Bounce Logic
        if circle['x'] - circle['r'] < 0 or circle['x'] + circle['r'] > WIDTH:
            circle['vx'] *= -1
        if circle['y'] - circle['r'] < 0 or circle['y'] + circle['r'] > HEIGHT:
            circle['vy'] *= -1

        # Hit Detection
        if shoot:
            target_dist = np.sqrt((circle['x'] - cx)**2 + (circle['y'] - cy)**2)
            if target_dist < circle['r']:
                circles.remove(circle)
                circles.append(spawn_circle())
                score += 1
                continue

        # Draw FILLED Circle (thickness = -1)
        cv2.circle(canvas, (int(circle['x']), int(circle['y'])), 
                   circle['r'], circle['color'], -1)

    # 2. Draw Crosshair
    if result.hand_landmarks:
        color = (0, 0, 255) if shoot else (0, 255, 0)
        cv2.circle(canvas, (cx, cy), 15, color, 2) # Outer ring
        cv2.line(canvas, (cx-10, cy), (cx+10, cy), color, 2) # Cross
        cv2.line(canvas, (cx, cy-10), (cx, cy+10), color, 2)

    # 3. Add UI
    cv2.putText(canvas, f"SCORE: {score}", (20, 40), 
                cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Blackout Shooter", canvas)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()