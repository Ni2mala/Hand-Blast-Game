import cv2
import random
import time


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

# --- 2. SETUP ---
camera = cv2.VideoCapture(0)
ret, frame = camera.read()
h, w, c = frame.shape
cx, cy = w//2, h//2
score = 0
last_time = time.time()
speed =300

# Add 20 targets without duplicating logic (Requirement #1)
targets = [spawn_target(w, h) for _ in range(20)]

while True:
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    ret, frame = camera.read()
    if not ret: break
    
    key = cv2.waitKey(1)
    if key == ord('q'): break

    # Movement (State Mutation)
    if key == ord('d'): cx += speed *dt
    if key == ord('a'): cx -= speed *dt
    if key == ord('s'): cy += speed *dt
    if key == ord('w'): cy -= speed *dt
    
    # Boundary Checking
    cx = int(max(0, min(cx, w - 1)))
    cy = int(max(0, min(cy, h - 1)))

    # --- 3. THE "SHOOT" LOGIC ---
    if key == ord(' '):
        for target in targets[:]:
            if is_hit(cx, cy, target): # Using your function!
                targets.remove(target)
                targets.append(spawn_target(w, h)) # Using your function!
                score += 1

    # --- 4. DRAWING ---
    # To disable drawing (Requirement #3), just comment out this loop:
    for target in targets:
        draw_target(frame, target) # Using your function!

    # Crosshair & UI
    cv2.line(frame, (cx-20, cy), (cx+20, cy), (0, 255, 0), 2)
    cv2.line(frame, (cx, cy-20), (cx, cy+20), (0, 255, 0), 2)
    cv2.putText(frame, f'Score: {score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow("crosshair", frame)

camera.release()
cv2.destroyAllWindows()