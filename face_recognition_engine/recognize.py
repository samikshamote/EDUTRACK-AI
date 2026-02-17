import cv2
import face_recognition
import pickle
import numpy as np
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENCODINGS_PATH = os.path.join(BASE_DIR, "face_recognition_engine", "encodings.pkl")
RECOGNIZED_FILE = os.path.join(BASE_DIR, "face_recognition_engine", "recognized_today.txt")

# Clear file at start
open(RECOGNIZED_FILE, "w").close()

with open(ENCODINGS_PATH, "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]

print("✔ Encodings loaded")
print("📷 Camera started")

def mark_attendance(name):
    if name == "Unknown":
        return

    with open(RECOGNIZED_FILE, "r") as f:
        existing_names = f.read().splitlines()

    if name not in existing_names:
        with open(RECOGNIZED_FILE, "a") as f:
            f.write(name + "\n")
        print(f"✔ Recognized: {name}")

video = cv2.VideoCapture(0)

start_time = time.time()
DURATION = 20   # 🔥 Camera runs for 20 seconds only

while True:
    ret, frame = video.read()
    if not ret:
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small)
    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
        name = "Unknown"

        distances = face_recognition.face_distance(known_encodings, face_encoding)
        if len(distances) > 0:
            best_match = np.argmin(distances)
            if matches[best_match]:
                name = known_names[best_match]

        mark_attendance(name)

    cv2.imshow("Smart Attendance", frame)

    # 🔥 Auto close after 20 seconds
    if time.time() - start_time > DURATION:
        break

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()

print("✅ Camera closed automatically")
