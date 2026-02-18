import pandas as pd

# ===============================
# LOAD CLEANED DATA
# ===============================
materials = pd.read_csv("../data/processed/cleaned_materials.csv")

print("\n================ DATA QUALITY CHECK (BEFORE) ================\n")

# Summary statistics before feature engineering
print(materials.describe())

# ===============================
# FEATURE ENGINEERING
# ===============================
# Normalize CO2 Emission
materials["CO2_Impact_Index"] = (
    materials["CO2_Emission_kg"] / materials["CO2_Emission_kg"].max()
)

# Cost efficiency (lower cost = higher score)
materials["Cost_Efficiency_Index"] = (
    materials["Cost_per_kg"].min() / materials["Cost_per_kg"]
)

# Material Suitability Score (Weighted Formula)
materials["Material_Suitability_Score"] = (
    0.4 * materials["Tensile_Strength_MPa"] +
    0.3 * materials["Cost_Efficiency_Index"] +
    0.3 * (1 - materials["CO2_Impact_Index"])
)

# ===============================
# DATA QUALITY VALIDATION (AFTER)
# ===============================
print("\n================ DATA QUALITY CHECK (AFTER) ================\n")

# Summary statistics after feature engineering
print(materials[
    [
        "CO2_Impact_Index",
        "Cost_Efficiency_Index",
        "Material_Suitability_Score"
    ]
].describe())

# ===============================
# CHECK FOR INVALID VALUES
# ===============================
print("\n================ DATA VALIDATION CHECKS ================\n")

print("Null Values Check:")
print(materials[
    [
        "CO2_Impact_Index",
        "Cost_Efficiency_Index",
        "Material_Suitability_Score"
    ]
].isnull().sum())

print("\nNegative Values Check:")
print((materials["Material_Suitability_Score"] < 0).sum())

# ===============================
# SAVE ENGINEERED DATA
# ===============================
materials.to_csv(
    "../data/processed/engineered_materials.csv",
    index=False
)

print("\n✅ Feature Engineering & Data Validation Completed Successfully")
