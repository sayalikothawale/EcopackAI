import pandas as pd
import numpy as np
import os
from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# ==============================
# DATABASE CONFIG
# ==============================

DATABASE_URL = os.environ.get("DATABASE_URL")

# Fix for Render postgres URL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==============================
# DATABASE MODEL
# ==============================

class Recommendation(db.Model):
    __tablename__ = "recommendation"

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

# ==============================
# LOAD DATASET
# ==============================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
csv_path = os.path.join(BASE_DIR, "data", "final", "ml_dataset.csv")

df = pd.read_csv(csv_path)

df["Cost_per_kg"] = pd.to_numeric(df["Cost_per_kg"], errors="coerce")
df["CO2_Emission_kg"] = pd.to_numeric(df["CO2_Emission_kg"], errors="coerce")
df["Tensile_Strength_MPa"] = pd.to_numeric(df["Tensile_Strength_MPa"], errors="coerce")

# ==============================
# HOME ROUTE
# ==============================

@app.route("/", methods=["GET", "POST"])
def home():

    top5 = None
    best = None
    form_data = None

    if request.method == "POST":

        try:
            item = request.form.get("item")
            weight = float(request.form.get("weight"))
            units = int(request.form.get("units"))
            fragility = request.form.get("fragility")
        except:
            return "Invalid form input", 400

        form_data = request.form

        max_cost = float(df["Cost_per_kg"].max())
        max_co2 = float(df["CO2_Emission_kg"].max())

        fragility_factor = {"L": 1, "M": 1.5, "H": 2}
        f_factor = fragility_factor.get(fragility, 1)

        results = []

        for _, row in df.iterrows():

            if pd.isna(row["Tensile_Strength_MPa"]):
                continue

            material_strength = float(row["Tensile_Strength_MPa"])
            required_strength = weight * 5 * f_factor

            strength_score = min(material_strength / required_strength, 1)

            eco_score = 1 - (float(row["CO2_Emission_kg"]) / max_co2)
            cost_score = 1 - (float(row["Cost_per_kg"]) / max_cost)
            biodeg_score = 1 if row["Biodegradable"] == "Yes" else 0.5

            sustainability_score = float(round(
                (eco_score * 0.3 +
                 cost_score * 0.25 +
                 biodeg_score * 0.2 +
                 strength_score * 0.25) * 100, 2))

            total_cost = float(round(float(row["Cost_per_kg"]) * weight * units, 2))
            total_co2 = float(round(float(row["CO2_Emission_kg"]) * weight * units, 2))

            # ==============================
            # WHY RECOMMENDED LOGIC
            # ==============================

            reasons = []

            if row["Biodegradable"] == "Yes":
                reasons.append("Biodegradable and eco-friendly")

            if eco_score > 0.7:
                reasons.append("Very low carbon footprint")

            if cost_score > 0.7:
                reasons.append("Cost efficient option")

            if strength_score > 0.8:
                reasons.append("High structural strength")

            if sustainability_score > 85:
                reasons.append("Excellent sustainability performance")

            if not reasons:
                reasons.append("Balanced cost, strength and environmental impact")

            results.append({
                "Material": str(row["Material_Name"]),
                "Total_Cost": total_cost,
                "Total_CO2": total_co2,
                "Strength": material_strength,
                "Score": sustainability_score,
                "Reasons": ", ".join(reasons)
            })

        results = sorted(results, key=lambda x: x["Score"], reverse=True)

        if results:
            top5 = results[:5]
            best = top5[0]

            # Save ONLY core values to DB
            new_entry = Recommendation(
                item=str(item),
                weight=float(weight),
                units=int(units),
                fragility=str(fragility),
                best_material=str(best["Material"]),
                total_cost=float(best["Total_Cost"]),
                total_co2=float(best["Total_CO2"]),
                strength=float(best["Strength"]),
                sustainability_score=float(best["Score"])
            )

            db.session.add(new_entry)
            db.session.commit()

    return render_template("index.html", top5=top5, best=best, form_data=form_data)

# ==============================
# EXPORT EXCEL
# ==============================

@app.route("/export_excel")
def export_excel():

    data = Recommendation.query.all()

    rows = [[
        r.item,
        r.best_material,
        r.total_cost,
        r.total_co2,
        r.strength,
        r.sustainability_score
    ] for r in data]

    df_export = pd.DataFrame(rows, columns=[
        "Item", "Material", "Cost", "CO2",
        "Strength (MPa)", "Score"
    ])

    file_path = "sustainability_report.xlsx"
    df_export.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

# ==============================
# EXPORT PDF
# ==============================

@app.route("/export_pdf")
def export_pdf():

    data = Recommendation.query.all()

    file_path = "sustainability_report.pdf"
    doc = SimpleDocTemplate(file_path)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Sustainability Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    table_data = [["Item", "Material", "Cost", "CO2", "Strength", "Score"]]

    for r in data:
        table_data.append([
            r.item,
            r.best_material,
            r.total_cost,
            r.total_co2,
            r.strength,
            r.sustainability_score
        ])

    table = Table(table_data)
    elements.append(table)

    doc.build(elements)

    return send_file(file_path, as_attachment=True)

# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
