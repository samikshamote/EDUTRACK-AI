import face_recognition
import os
import pickle

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "face_recognition_engine", "dataset")

known_encodings = []
known_names = []

for student_name in os.listdir(DATASET_PATH):

    student_folder = os.path.join(DATASET_PATH, student_name)

    if not os.path.isdir(student_folder):
        continue

    for image_name in os.listdir(student_folder):

        # ✅ Only allow image files
        if not image_name.lower().endswith((".jpg", ".jpeg", ".png", ".jfif")):
            continue

        image_path = os.path.join(student_folder, image_name)

        print("Processing:", image_path)

        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(student_name)

data = {
    "encodings": known_encodings,
    "names": known_names
}

with open(os.path.join(BASE_DIR, "face_recognition_engine", "encodings.pkl"), "wb") as f:
    pickle.dump(data, f)

print("✅ Training completed successfully")
