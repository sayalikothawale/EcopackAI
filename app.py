import os
from io import BytesIO
import pandas as pd
from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# =====================================================
# DATABASE CONFIG (Render Production Safe)
# =====================================================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    DATABASE_URL = "sqlite:///local.db"  # fallback for local testing

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =====================================================
# DATABASE MODEL
# =====================================================
class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100))
    weight = db.Column(db.Float)
    units = db.Column(db.Integer)
    fragility = db.Column(db.String(10))
    best_material = db.Column(db.String(200))
    total_cost = db.Column(db.Float)
    total_co2 = db.Column(db.Float)
    strength = db.Column(db.Float)
    sustainability_score = db.Column(db.Float)

with app.app_context():
    db.create_all()

# =====================================================
# LOAD DATASET (Safe for Render)
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "data", "final", "ml_dataset.csv")

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)

    df["Cost_per_kg"] = pd.to_numeric(df["Cost_per_kg"], errors="coerce")
    df["CO2_Emission_kg"] = pd.to_numeric(df["CO2_Emission_kg"], errors="coerce")
    df["Tensile_Strength_MPa"] = pd.to_numeric(df["Tensile_Strength_MPa"], errors="coerce")
else:
    df = pd.DataFrame()

# =====================================================
# HOME ROUTE
# =====================================================
@app.route("/", methods=["GET", "POST"])
def home():

    top5 = None
    best = None
    error = None

    if request.method == "POST":

        if df.empty:
            error = "Dataset file not found."
            return render_template("index.html", error=error)

        try:
            item = request.form.get("item")
            weight = float(request.form.get("weight"))
            units = int(request.form.get("units"))
            fragility = request.form.get("fragility")

            max_cost = df["Cost_per_kg"].max()
            max_co2 = df["CO2_Emission_kg"].max()

            fragility_factor = {"L": 1, "M": 1.5, "H": 2}
            f_factor = fragility_factor.get(fragility, 1)

            results = []

            for _, row in df.iterrows():

                if pd.isna(row["Tensile_Strength_MPa"]):
                    continue

                required_strength = weight * 5 * f_factor
                strength_score = min(row["Tensile_Strength_MPa"] / required_strength, 1)

                eco_score = 1 - (row["CO2_Emission_kg"] / max_co2)
                cost_score = 1 - (row["Cost_per_kg"] / max_cost)
                biodeg_score = 1 if row["Biodegradable"] == "Yes" else 0.5

                sustainability_score = round(
                    (eco_score * 0.3 +
                     cost_score * 0.25 +
                     biodeg_score * 0.2 +
                     strength_score * 0.25) * 100, 2)

                total_cost = round(row["Cost_per_kg"] * weight * units, 2)
                total_co2 = round(row["CO2_Emission_kg"] * weight * units, 2)

                results.append({
                    "Material": row["Material_Name"],
                    "Total_Cost": total_cost,
                    "Total_CO2": total_co2,
                    "Strength": row["Tensile_Strength_MPa"],
                    "Score": sustainability_score
                })

            results = sorted(results, key=lambda x: x["Score"], reverse=True)

            if results:
                top5 = results[:5]
                best = top5[0]

                new_entry = Recommendation(
                    item=item,
                    weight=weight,
                    units=units,
                    fragility=fragility,
                    best_material=best["Material"],
                    total_cost=best["Total_Cost"],
                    total_co2=best["Total_CO2"],
                    strength=best["Strength"],
                    sustainability_score=best["Score"]
                )

                db.session.add(new_entry)
                db.session.commit()

        except Exception as e:
            error = str(e)

    return render_template("index.html", top5=top5, best=best, error=error)

# =====================================================
# EXPORT EXCEL (100% Render Safe)
# =====================================================
@app.route("/export_excel")
def export_excel():

    try:
        data = Recommendation.query.all()

        rows = []
        for r in data:
            rows.append([
                r.item,
                r.weight,
                r.units,
                r.fragility,
                r.best_material,
                r.total_cost,
                r.total_co2,
                r.strength,
                r.sustainability_score
            ])

        df_export = pd.DataFrame(rows, columns=[
            "Item",
            "Weight",
            "Units",
            "Fragility",
            "Best Material",
            "Total Cost",
            "Total CO2",
            "Strength",
            "Sustainability Score"
        ])

        output = BytesIO()
        df_export.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)

        return send_file(
            output,
            download_name="sustainability_report.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return f"Excel Export Error: {str(e)}"

# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    app.run()
