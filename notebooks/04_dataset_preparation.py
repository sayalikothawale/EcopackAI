import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ===============================
# PATH SETUP
# ===============================
PROCESSED_PATH = "../data/processed"
FINAL_PATH = "../data/final"
os.makedirs(FINAL_PATH, exist_ok=True)

# ===============================
# LOAD FEATURE-ENGINEERED DATA
# ===============================
file_path = f"{PROCESSED_PATH}/engineered_materials.csv"

if not os.path.exists(file_path):
    raise FileNotFoundError(
        "engineered_materials.csv not found. Run 03_feature_engineering.py first."
    )

materials = pd.read_csv(file_path)

print("\n✅ Feature-Engineered Dataset Loaded")
print("Dataset Shape:", materials.shape)

# ===============================
# ENCODE SHIPPING CATEGORY
# ===============================
category_encoder = LabelEncoder()
materials["Category_Encoded"] = category_encoder.fit_transform(
    materials["Category"]
)

# ===============================
# ML FEATURE SELECTION
# ===============================
# As per PDF:
# Material Safety      → Material_Suitability_Score
# Strength             → Tensile_Strength_MPa
# Shipping Category    → Category_Encoded

features = [
    "Material_Suitability_Score",
    "Tensile_Strength_MPa",
    "Category_Encoded"
]

X = materials[features]

# ===============================
# TARGET VARIABLES
# ===============================
y_cost = materials["Cost_per_kg"]          # Cost Prediction
y_co2 = materials["CO2_Emission_kg"]        # CO₂ Impact Prediction

# ===============================
# DATA SCALING PIPELINE
# ===============================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ===============================
# TRAIN / TEST SPLIT
# ===============================
X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X_scaled,
    y_cost,
    test_size=0.2,
    random_state=42
)

_, _, y_co2_train, y_co2_test = train_test_split(
    X_scaled,
    y_co2,
    test_size=0.2,
    random_state=42
)

# ===============================
# DISPLAY SPLIT DETAILS
# ===============================
print("\n📊 TRAIN–TEST SPLIT SUMMARY")
print("Training Feature Shape :", X_train.shape)
print("Testing Feature Shape  :", X_test.shape)

print("\n🎯 Sample Cost Targets (Train):")
print(y_cost_train.head())

print("\n🎯 Sample CO₂ Targets (Train):")
print(y_co2_train.head())

# ===============================
# SAVE FINAL DATASET
# ===============================
materials.to_csv(
    f"{FINAL_PATH}/ml_dataset.csv",
    index=False
)

print("\n✅ Module 3 Dataset Preparation Completed Successfully")
