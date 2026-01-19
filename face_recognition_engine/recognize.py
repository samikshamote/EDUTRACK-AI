import cv2
import face_recognition
import pickle
import numpy as np
from datetime import datetime
import os

recognized_file = "face_recognition_engine/recognized_today.txt"

# Ensure file exists
open(recognized_file, "a").close()

# Load encodings
with open("face_recognition_engine/encodings.pkl", "rb") as f:

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

    output_file = "face_recognition_engine/recognized_today.txt"

    # Create file if not exists
    if not os.path.exists(output_file):
        open(output_file, "w").close()

    with open(output_file, "r") as f:
        names = f.read().splitlines()

    if name not in names:
        with open(output_file, "a") as f:
            f.write(name + "\n")

        print(f"✔ Recognized: {name}")


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
