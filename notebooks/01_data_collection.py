import pandas as pd
import os

RAW_PATH = "../data/raw"
os.makedirs(RAW_PATH, exist_ok=True)

materials = pd.read_excel("../data/raw/materials_database_600.xlsx")
packaging = pd.read_excel("../data/raw/real_packaging_history.xlsx")

print("✅ Dataset Loaded Successfully")
print("Materials Shape:", materials.shape)
print("Packaging Shape:", packaging.shape)

print("\nMaterials Columns:\n", materials.columns)
print("\nPackaging Columns:\n", packaging.columns)
