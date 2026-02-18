import pandas as pd
import os

RAW_PATH = "../data/raw"
PROCESSED_PATH = "../data/processed"
os.makedirs(PROCESSED_PATH, exist_ok=True)

# ===============================
# LOAD DATASETS
# ===============================
materials = pd.read_excel(f"{RAW_PATH}/materials_database_600.xlsx")
packaging = pd.read_excel(f"{RAW_PATH}/real_packaging_history.xlsx")

print("\n================ DATASET OVERVIEW ================\n")

# ===============================
# BEFORE CLEANING
# ===============================
print("📌 BEFORE CLEANING\n")

print("Materials Dataset Shape:", materials.shape)
print("Packaging Dataset Shape:", packaging.shape)

print("\n🔍 Missing Values (Materials):")
print(materials.isnull().sum())

print("\n🔍 Missing Values (Packaging):")
print(packaging.isnull().sum())

print("\n🔁 Duplicate Rows (Materials):", materials.duplicated().sum())
print("🔁 Duplicate Rows (Packaging):", packaging.duplicated().sum())

# ===============================
# CLEANING PROCESS
# ===============================
materials_cleaned = materials.drop_duplicates()
packaging_cleaned = packaging.drop_duplicates()

materials_cleaned.fillna(materials_cleaned.median(numeric_only=True), inplace=True)
packaging_cleaned.fillna(packaging_cleaned.median(numeric_only=True), inplace=True)

# ===============================
# AFTER CLEANING
# ===============================
print("\n================ AFTER CLEANING ================\n")

print("Materials Dataset Shape:", materials_cleaned.shape)
print("Packaging Dataset Shape:", packaging_cleaned.shape)

print("\n🔍 Remaining Missing Values (Materials):")
print(materials_cleaned.isnull().sum())

print("\n🔍 Remaining Missing Values (Packaging):")
print(packaging_cleaned.isnull().sum())

# ===============================
# SAVE CLEANED DATA
# ===============================
materials_cleaned.to_csv(
    f"{PROCESSED_PATH}/cleaned_materials.csv", index=False
)

packaging_cleaned.to_csv(
    f"{PROCESSED_PATH}/cleaned_packaging_history.csv", index=False
)

print("\n✅ Data Cleaning Completed Successfully")
