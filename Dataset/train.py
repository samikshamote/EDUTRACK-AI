import os
import cv2
import face_recognition
import pickle

dataset_path = "."

encodings = []
names = []

print("Starting training...")

for student_name in os.listdir(dataset_path):
    student_path = os.path.join(dataset_path, student_name)

    if not os.path.isdir(student_path):
        continue

    print(f"Processing folder: {student_name}")

    for img_name in os.listdir(student_path):
        img_path = os.path.join(student_path, img_name)

        image = cv2.imread(img_path)
        if image is None:
            continue

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb)

        if len(boxes) == 0:
            print(f"⚠ No face detected in: {img_name}")
            continue

        encoding = face_recognition.face_encodings(rgb, boxes)[0]

        encodings.append(encoding)
        names.append(student_name)

        print(f"✔ Encoded: {img_name}")

# Save encodings
with open("encodings.pkl", "wb") as f:
    pickle.dump(
        {"encodings": encodings, "names": names},
        f
    )

print("\nTraining Complete!")
print("Encodings saved in encodings.pkl")
