import os
import io
import pandas as pd
from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# ==============================
# DATABASE CONFIG (RENDER SAFE)
# ==============================
database_url = os.environ.get("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==============================
# DATABASE MODEL
# ==============================
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
    reasons = db.Column(db.Text)

with app.app_context():
    db.drop_all()
    db.create_all()


# ==============================
# LOAD DATASET
# ==============================
df = pd.read_csv("data/final/ml_dataset.csv")

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

    if request.method == "POST":

        item = request.form["item"]
        weight = float(request.form["weight"])
        units = int(request.form["units"])
        fragility = request.form["fragility"]

        max_cost = df["Cost_per_kg"].max()
        max_co2 = df["CO2_Emission_kg"].max()

        fragility_factor = {"L": 1, "M": 1.5, "H": 2}
        factor = fragility_factor.get(fragility, 1)

        results = []

        for _, row in df.iterrows():

            if pd.isna(row["Tensile_Strength_MPa"]):
                continue

            required_strength = weight * 5 * factor
            material_strength = row["Tensile_Strength_MPa"]
            strength_score = min(material_strength / required_strength, 1)

            eco_score = 1 - (row["CO2_Emission_kg"] / max_co2)
            cost_score = 1 - (row["Cost_per_kg"] / max_cost)
            biodeg_score = 1 if row["Biodegradable"] == "Yes" else 0.5

            final_score = round(
                (eco_score * 0.3 +
                 cost_score * 0.25 +
                 biodeg_score * 0.2 +
                 strength_score * 0.25) * 100, 2)

            total_cost = round(row["Cost_per_kg"] * weight * units, 2)
            total_co2 = round(row["CO2_Emission_kg"] * weight * units, 2)

            # WHY RECOMMENDED
            reasons = []

            if row["Biodegradable"] == "Yes":
                reasons.append("Biodegradable and eco-friendly")

            if eco_score > 0.7:
                reasons.append("Very low carbon footprint")

            if cost_score > 0.7:
                reasons.append("Cost efficient option")

            if strength_score > 0.8:
                reasons.append("High structural strength")

            if final_score > 85:
                reasons.append("Excellent sustainability performance")

            if not reasons:
                reasons.append("Balanced cost, strength and environmental impact")

            results.append({
                "Material": row["Material_Name"],
                "Cost": total_cost,
                "CO2": total_co2,
                "Strength": material_strength,
                "Score": final_score,
                "Reasons": ", ".join(reasons)
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
                total_cost=best["Cost"],
                total_co2=best["CO2"],
                strength=best["Strength"],
                sustainability_score=best["Score"],
                reasons=best["Reasons"]
            )

            db.session.add(new_entry)
            db.session.commit()

    return render_template("index.html", top5=top5, best=best)

# ==============================
# EXPORT EXCEL
# ==============================
@app.route("/export_excel")
def export_excel():

    data = Recommendation.query.all()

    rows = []
    for r in data:
        rows.append([
            r.item,
            r.best_material,
            r.total_cost,
            r.total_co2,
            r.strength,
            r.sustainability_score,
            r.reasons
        ])

    df_export = pd.DataFrame(rows, columns=[
        "Item", "Material", "Cost", "CO2",
        "Strength (MPa)", "Score", "Why Recommended"
    ])

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df_export.to_excel(writer, index=False)
    writer.close()
    output.seek(0)

    return send_file(
        output,
        download_name="sustainability_report.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==============================
# EXPORT PDF
# ==============================
@app.route("/export_pdf")
def export_pdf():

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Sustainability Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    table_data = [["Item", "Material", "Cost", "CO2",
                   "Strength", "Score", "Why Recommended"]]

    data = Recommendation.query.all()
    for r in data:
        table_data.append([
            r.item,
            r.best_material,
            r.total_cost,
            r.total_co2,
            r.strength,
            r.sustainability_score,
            r.reasons
        ])

    table = Table(table_data)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        download_name="sustainability_report.pdf",
        as_attachment=True,
        mimetype="application/pdf"
    )

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run()
