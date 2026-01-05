import cv2
import face_recognition
import pickle
import numpy as np
from datetime import datetime
import os

# Load encodings
with open("encodings.pkl", "rb") as f:
    data = pickle.load(f)

# Handle dictionary or tuple format
if isinstance(data, dict):
    known_encodings = data["encodings"]
    known_names = data["names"]
elif isinstance(data, tuple):
    known_encodings, known_names = data
else:
    raise ValueError("Unknown encodings format!")

print("✔ Encodings loaded")
print("Starting camera...")

# Attendance marking function
def mark_attendance(name):
    if name == "Unknown":
        return

    file_exists = os.path.isfile("attendance.csv")

    # Create file with header if not exists
    if not file_exists:
        with open("attendance.csv", "w") as f:
            f.write("Name,Date,Time\n")

    # Read existing lines
    with open("attendance.csv", "r") as f:
        lines = f.readlines()

    today = datetime.now().strftime("%Y-%m-%d")

    # Check if already marked today
    for line in lines[1:]:  # skip header
        entry = line.strip().split(",")
        if entry[0] == name and entry[1] == today:
            return  # already marked

    # Append new entry
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    with open("attendance.csv", "a") as f:
        f.write(f"{name},{today},{time}\n")
    print(f"✔ Attendance marked: {name}")

# Start webcam
video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    if not ret:
        break

    # Resize for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert BGR to RGB
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect all faces
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []

    for face_encoding in face_encodings:
        # Compare face with known encodings
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]

        face_names.append(name)
        mark_attendance(name)  # Marks attendance for every detected face

    # Draw rectangles and names
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("Smart Attendance - Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
