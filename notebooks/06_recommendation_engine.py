import os
import pandas as pd
import joblib
import numpy as np

# ===============================
# PATH SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Possible CSV locations (now using ml_dataset.csv)
POSSIBLE_CSV_PATHS = [
    os.path.join(BASE_DIR, "..", "data", "processed", "ml_dataset.csv"),
    os.path.join(BASE_DIR, "..", "data", "final", "ml_dataset.csv")
]

# Find the CSV
for path in POSSIBLE_CSV_PATHS:
    if os.path.exists(path):
        DATA_PATH = path
        print(f"✅ Found materials CSV at: {DATA_PATH}")
        break
else:
    print("❌ ERROR: Could not find ml_dataset.csv in 'processed' or 'final' folders.")
    exit(1)

# Model paths
COST_MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "cost_model.pkl")
CO2_MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "co2_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "..", "models", "scaler.pkl")
CATEGORY_ENCODER_PATH = os.path.join(BASE_DIR, "..", "models", "category_encoder.pkl")

# ===============================
# LOAD DATA & MODELS
# ===============================
try:
    materials = pd.read_csv(DATA_PATH)
except Exception as e:
    print(f"❌ ERROR: Failed to load materials CSV: {e}")
    exit(1)

try:
    cost_model = joblib.load(COST_MODEL_PATH)
    co2_model = joblib.load(CO2_MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    category_encoder = joblib.load(CATEGORY_ENCODER_PATH)
    print("✅ Models and encoders loaded successfully")
except FileNotFoundError as e:
    print(f"❌ ERROR: Could not find a model or encoder: {e}")
    exit(1)

# ===============================
# USER INPUT
# ===============================
print("\n🔹 ENTER PRODUCT DETAILS")
item_name = input("Item Name: ")
fragility = input("Fragility (Low / Medium / High): ").strip().lower()
weight = float(input("Weight of ONE unit (kg, decimal allowed): "))
units = int(input("Number of units: "))

# ===============================
# FRAGILITY → MIN STRENGTH
# ===============================
if fragility == "high":
    min_strength = 70
elif fragility == "medium":
    min_strength = 50
else:
    min_strength = 30

total_weight = weight * units
print(f"\n📦 Total Shipment Weight: {total_weight} kg")

# ===============================
# FILTER MATERIALS BASED ON STRENGTH
# ===============================
filtered_materials = materials[materials["Tensile_Strength_MPa"] >= min_strength].copy()

if filtered_materials.empty:
    print("⚠️ No materials meet the strength requirement. Try a lower fragility level.")
    exit(1)

# ===============================
# ENCODE CATEGORY
# ===============================
filtered_materials["Category_Encoded"] = category_encoder.transform(filtered_materials["Category"])

# ===============================
# FEATURE MATRIX
# ===============================
features = ["Material_Suitability_Score", "Tensile_Strength_MPa", "Category_Encoded"]
X = filtered_materials[features]
X_scaled = scaler.transform(X)

# ===============================
# ML PREDICTIONS
# ===============================
filtered_materials["Predicted_Cost_per_kg"] = cost_model.predict(X_scaled)
filtered_materials["Predicted_CO2_per_kg"] = co2_model.predict(X_scaled)

# ===============================
# TOTAL IMPACT CALCULATION
# ===============================
filtered_materials["Total_Cost"] = filtered_materials["Predicted_Cost_per_kg"] * total_weight
filtered_materials["Total_CO2"] = filtered_materials["Predicted_CO2_per_kg"] * total_weight

# ===============================
# FINAL RANKING SCORE
# ===============================
filtered_materials["Final_Score"] = (
    (1 / filtered_materials["Total_Cost"]) * 0.5 +
    (1 / filtered_materials["Total_CO2"]) * 0.5
)

# ===============================
# TOP 5 RECOMMENDATIONS
# ===============================
top_5 = filtered_materials.sort_values("Final_Score", ascending=False).head(5)

# ===============================
# DISPLAY RESULTS
# ===============================
print("\n🌱 TOP 5 SUSTAINABLE PACKAGING RECOMMENDATIONS")
print("For Item:", item_name)
print(top_5[["Material_Name", "Total_Cost", "Total_CO2", "Material_Suitability_Score"]].round(3))
print("\n✅ Recommendation Generated Successfully")
