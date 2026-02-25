import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

print("Training Started")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "dataset", "students_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")
MODEL_PATH = os.path.join(MODEL_DIR, "student_model.pkl")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError("students_data.csv not found inside dataset folder")

df = pd.read_csv(DATA_PATH)

print("Columns found:", df.columns.tolist())

required_columns = [
    "attendance",
    "OS_internal", "OS_assignment",
    "WT_internal", "WT_assignment",
    "DA_internal", "DA_assignment",
    "Java_internal", "Java_assignment",
    "Compiler_internal", "Compiler_assignment",
    "final_score"
]

for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

X = df.drop("final_score", axis=1)
y = df["final_score"]

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42
)

model.fit(X, y)

os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(model, MODEL_PATH)

print("✅ Model trained successfully.")
print("✅ Model saved at:", MODEL_PATH)
