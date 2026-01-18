import cv2
import random
import time
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


model_path = "gesture_recognizer.task"

BaseOptions = python.BaseOptions
GestureRecognizer = vision.GestureRecognizer
GestureRecognizerOptions = vision.GestureRecognizerOptions
VisionRunningMode = vision.RunningMode

options = GestureRecognizerOptions(
    base_options = BaseOptions(model_asset_path = model_path),
    running_mode = VisionRunningMode.VIDEO,
    num_hands =1
)

recognizer = GestureRecognizer.create_from_options(options)


# --- 1. FUNCTIONS (Knowledge & Logic Definitions) ---
def is_hit(cx, cy, target):
    dx = cx - target["x"]
    dy = cy - target["y"]
    return (dx*dx + dy*dy) ** 0.5 < target["r"]

def draw_target(frame, target):
    cv2.circle(frame, (target["x"], target["y"]), target["r"], (0, 0, 255), -1)

def spawn_target(w, h):
    return {
        "x": random.randint(50, w-50),
        "y": random.randint(50, h-50),
        "r": 30,  # <-- CHANGE RADIUS HERE (Requirement #2)
        "vx": random.choice([-100, -60, 60, 100]),
        "vy":random.choice([-100, -60, 60, 100])
    }


def update_target(target, dt, w, h):
    target['x'] += target['vx']*dt
    target['y'] += target['vy']*dt

    if target["x"] - target["r"] < 0 or target["x"] + target["r"] > w:
        target["vx"] *= -1  # Reverse horizontal direction
        # Keep target in bounds
        target["x"] = max(target["r"], min(target["x"], w - target["r"]))
    
    if target["y"] - target["r"] < 0 or target["y"] + target["r"] > h:
        target["vy"] *= -1  # Reverse vertical direction
        # Keep target in bounds
        target["y"] = max(target["r"], min(target["y"], h - target["r"]))
    
    # Keep coordinates as integers for OpenCV
    target["x"] = int(target["x"])
    target["y"] = int(target["y"])

# --- 2. SETUP ---
camera = cv2.VideoCapture(0)
ret, frame = camera.read()
h, w, c = frame.shape
cx, cy = w//2, h//2
score = 0
last_time = time.time()
speed =300
cool_down = 0.5
last_shot_time = 0


# Add 20 targets without duplicating logic (Requirement #1)
targets = [spawn_target(w, h) for _ in range(20)]

while True:
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    timestamp = int(time.time()*1000)
    ret, frame = camera.read()
    if not ret: break

    rgb =cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = recognizer.recognize_for_video(mp_image, timestamp)
    
    if result.hand_landmarks:
        hand_landmarks = result.hand_landmarks[0]
        index_tip =hand_landmarks[8]

        cx = int(index_tip.x *w)
        cy = int(index_tip.y *h)

    key = cv2.waitKey(1)
    if key == ord('q'): break
    

    for target in targets:
        update_target(target,dt, w, h) 

    # --- 3. THE "SHOOT" LOGIC ---
    shoot = False
    if shoot:
        hit_count = 0
        for target in targets[:]:
            if is_hit(cx, cy, target): # Using your function!
                targets.remove(target)
                targets.append(spawn_target(w, h)) # Using your function!
                score += 1
                hit_count += 1
        if hit_count >0:
            print(f'HIT! Score: {score} (+{hit_count})')
            
        else:
            print("MISS!")
    # --- 4. DRAWING ---

    # Crosshair & UI
    cv2.line(frame, (cx-20, cy), (cx+20, cy), (0,255,0), 2)
    cv2.line(frame, (cx, cy-20), (cx, cy+20), (0,255,0), 2)
    cv2.circle(frame, (cx, cy), 10, (0,255,0), -1)
    cv2.putText(frame, f'Score: {score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow("crosshair", frame)

camera.release()
cv2.destroyAllWindows()