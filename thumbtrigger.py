import cv2
import time
import random
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# =========================
# MediaPipe Gesture Setup
# =========================
model_path = "gesture_recognizer.task"

BaseOptions = python.BaseOptions
GestureRecognizer = vision.GestureRecognizer
GestureRecognizerOptions = vision.GestureRecognizerOptions
VisionRunningMode = vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

recognizer = GestureRecognizer.create_from_options(options)


# =========================
# Utility Functions
# =========================
def finger_distance(lm1, lm2, w, h):
    x1, y1 = lm1.x * w, lm1.y * h
    x2, y2 = lm2.x * w, lm2.y * h
    return math.hypot(x1 - x2, y1 - y2)


def is_hit(cx, cy, target):
    dx = cx - target["x"]
    dy = cy - target["y"]
    return math.hypot(dx, dy) < target["r"]


def spawn_target(w, h):
    return {
        "x": random.randint(50, w - 50),
        "y": random.randint(50, h - 50),
        "r": 30,
        "vx": random.choice([-120, -80, 80, 120]),
        "vy": random.choice([-120, -80, 80, 120])
    }


def update_target(target, dt, w, h):
    target["x"] += target["vx"] * dt
    target["y"] += target["vy"] * dt

    if target["x"] < target["r"] or target["x"] > w - target["r"]:
        target["vx"] *= -1
    if target["y"] < target["r"] or target["y"] > h - target["r"]:
        target["vy"] *= -1

    target["x"] = int(target["x"])
    target["y"] = int(target["y"])


# =========================
# Game Setup
# =========================
camera = cv2.VideoCapture(0)
ret, frame = camera.read()
h, w, _ = frame.shape

cx, cy = w // 2, h // 2
smooth_cx, smooth_cy = cx, cy
SMOOTHING = 0.25

targets = [spawn_target(w, h) for _ in range(15)]
score = 0

TRIGGER_DISTANCE = 35       # pinch sensitivity (pixels)
SHOT_COOLDOWN = 0.4
last_shot_time = 0
previous_trigger = False

last_time = time.time()


# =========================
# Main Loop
# =========================
while True:
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    ret, frame = camera.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = recognizer.recognize_for_video(mp_image, int(current_time * 1000))

    trigger_pressed = False
    shoot = False

    if result.hand_landmarks:
        hand = result.hand_landmarks[0]

        index_tip = hand[8]
        thumb_tip = hand[4]

        # Aim (index finger)
        raw_cx = index_tip.x * w
        raw_cy = index_tip.y * h
        smooth_cx = SMOOTHING * raw_cx + (1 - SMOOTHING) * smooth_cx
        smooth_cy = SMOOTHING * raw_cy + (1 - SMOOTHING) * smooth_cy

        cx = int(smooth_cx)
        cy = int(smooth_cy)

        # Trigger (thumb pinch)
        dist = finger_distance(index_tip, thumb_tip, w, h)
        trigger_pressed = dist < TRIGGER_DISTANCE

        # Edge-triggered firing
        if (
            trigger_pressed
            and not previous_trigger
            and current_time - last_shot_time > SHOT_COOLDOWN
        ):
            shoot = True
            last_shot_time = current_time

        previous_trigger = trigger_pressed

        # Debug line between fingers
        p1 = (int(index_tip.x * w), int(index_tip.y * h))
        p2 = (int(thumb_tip.x * w), int(thumb_tip.y * h))
        cv2.line(frame, p1, p2, (255, 255, 0), 2)

    # Shooting logic
    if shoot:
        for target in targets[:]:
            if is_hit(cx, cy, target):
                targets.remove(target)
                targets.append(spawn_target(w, h))
                score += 1

    # Update targets
    for target in targets:
        update_target(target, dt, w, h)
        cv2.circle(frame, (target["x"], target["y"]), target["r"], (0, 0, 255), -1)

    # Crosshair color
    if shoot:
        color = (0, 0, 255)        # fired
    elif trigger_pressed:
        color = (0, 255, 255)      # armed
    else:
        color = (0, 255, 0)        # idle

    # Crosshair
    cv2.line(frame, (cx - 20, cy), (cx + 20, cy), color, 2)
    cv2.line(frame, (cx, cy - 20), (cx, cy + 20), color, 2)
    cv2.circle(frame, (cx, cy), 8, color, -1)

    # UI
    cv2.putText(frame, f"Score: {score}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.putText(frame,
                f"Trigger: {'PRESSED' if trigger_pressed else 'OPEN'}",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("Crosshair Shooter", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


camera.release()
cv2.destroyAllWindows()
