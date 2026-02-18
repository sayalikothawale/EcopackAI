import pandas as pd
import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from xgboost import XGBRegressor

# ===============================
# PATH SETUP
# ===============================
FINAL_PATH = "../data/final"
MODEL_PATH = "../models"
os.makedirs(MODEL_PATH, exist_ok=True)

# ===============================
# LOAD FINAL DATASET
# ===============================
data = pd.read_csv(f"{FINAL_PATH}/ml_dataset.csv")

print("\n✅ Final ML Dataset Loaded")
print("Dataset Shape:", data.shape)

# ===============================
# ENCODE CATEGORY
# ===============================
encoder = LabelEncoder()
data["Category_Encoded"] = encoder.fit_transform(data["Category"])

# ===============================
# FEATURE SELECTION
# ===============================
features = [
    "Material_Suitability_Score",
    "Tensile_Strength_MPa",
    "Category_Encoded"
]

X = data[features]
y_cost = data["Cost_per_kg"]
y_co2 = data["CO2_Emission_kg"]

# ===============================
# SCALING
# ===============================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ===============================
# TRAIN / TEST SPLIT
# ===============================
X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X_scaled, y_cost, test_size=0.2, random_state=42
)

_, _, y_co2_train, y_co2_test = train_test_split(
    X_scaled, y_co2, test_size=0.2, random_state=42
)

# ===============================
# COST PREDICTION MODEL
# ===============================
cost_model = RandomForestRegressor(
    n_estimators=150,
    random_state=42
)

cost_model.fit(X_train, y_cost_train)
cost_pred = cost_model.predict(X_test)

rmse_cost = np.sqrt(mean_squared_error(y_cost_test, cost_pred))
mae_cost = mean_absolute_error(y_cost_test, cost_pred)
r2_cost = r2_score(y_cost_test, cost_pred)

print("\n📊 COST PREDICTION MODEL PERFORMANCE")
print("RMSE:", round(rmse_cost, 3))
print("MAE :", round(mae_cost, 3))
print("R²  :", round(r2_cost, 3))

# ===============================
# CO₂ IMPACT PREDICTION MODEL
# ===============================
co2_model = XGBRegressor(
    n_estimators=150,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)

co2_model.fit(X_train, y_co2_train)
co2_pred = co2_model.predict(X_test)

rmse_co2 = np.sqrt(mean_squared_error(y_co2_test, co2_pred))
mae_co2 = mean_absolute_error(y_co2_test, co2_pred)
r2_co2 = r2_score(y_co2_test, co2_pred)

print("\n📊 CO₂ IMPACT PREDICTION MODEL PERFORMANCE")
print("RMSE:", round(rmse_co2, 3))
print("MAE :", round(mae_co2, 3))
print("R²  :", round(r2_co2, 3))

# ===============================
# SAVE MODELS
# ===============================
joblib.dump(cost_model, f"{MODEL_PATH}/cost_model.pkl")
joblib.dump(co2_model, f"{MODEL_PATH}/co2_model.pkl")
joblib.dump(scaler, f"{MODEL_PATH}/scaler.pkl")
joblib.dump(encoder, f"{MODEL_PATH}/category_encoder.pkl")

print("\n✅ Models Trained and Saved Successfully")
