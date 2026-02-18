import os
import io
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

# =========================
# DATABASE CONFIG
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# DATABASE MODEL
# =========================
class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100))
    weight = db.Column(db.Float)
    units = db.Column(db.Integer)
    fragility = db.Column(db.String(10))
    best_material = db.Column(db.String(100))
    total_cost = db.Column(db.Float)
    total_co2 = db.Column(db.Float)
    strength = db.Column(db.Float)
    sustainability_score = db.Column(db.Float)
    reasons = db.Column(db.Text)

with app.app_context():
    db.create_all()

# =========================
# MATERIAL DATA
# =========================
materials = pd.DataFrame({
    "Material": [
        "Recycled Jute Burlap",
        "Corrugated Cardboard",
        "Recycled Paper Pulp",
        "Biodegradable Plastic"
    ],
    "Cost_per_unit": [2.22, 3.10, 2.80, 3.50],
    "CO2_per_unit": [0.618, 1.10, 0.95, 1.20],
    "Strength": [27.84, 35.00, 30.00, 40.00],
    "Biodegradable": [1, 1, 1, 0]
})

# =========================
# HOME ROUTE
# =========================
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        item = request.form["item"]
        weight = float(request.form["weight"])
        units = int(request.form["units"])
        fragility = request.form["fragility"]

        df = materials.copy()

        df["Total_Cost"] = df["Cost_per_unit"] * units
        df["Total_CO2"] = df["CO2_per_unit"] * units

        max_co2 = np.max(df["Total_CO2"])
        max_cost = np.max(df["Total_Cost"])
        max_strength = np.max(df["Strength"])

        df["Eco_Score"] = 1 - (df["Total_CO2"] / max_co2)
        df["Cost_Score"] = 1 - (df["Total_Cost"] / max_cost)
        df["Strength_Score"] = df["Strength"] / max_strength
        df["Biodeg_Score"] = df["Biodegradable"]

        df["Score"] = (
            df["Eco_Score"] * 0.3 +
            df["Cost_Score"] * 0.25 +
            df["Biodeg_Score"] * 0.2 +
            df["Strength_Score"] * 0.25
        ) * 100

        best = df.sort_values(by="Score", ascending=False).iloc[0]

        # Convert ALL numpy values to float
        total_cost = float(best["Total_Cost"])
        total_co2 = float(best["Total_CO2"])
        strength = float(best["Strength"])
        score = float(best["Score"])

        reasons = []
        if best["Biodegradable"] == 1:
            reasons.append("Biodegradable and eco-friendly")
        if total_co2 == float(df["Total_CO2"].min()):
            reasons.append("Very low carbon footprint")
        if total_cost == float(df["Total_Cost"].min()):
            reasons.append("Cost efficient option")
        if strength >= float(df["Strength"].mean()):
            reasons.append("High structural strength")
        if score >= 80:
            reasons.append("Excellent sustainability performance")

        reason_text = ", ".join(reasons)

        new_record = Recommendation(
            item=item,
            weight=weight,
            units=units,
            fragility=fragility,
            best_material=best["Material"],
            total_cost=total_cost,
            total_co2=total_co2,
            strength=strength,
            sustainability_score=score,
            reasons=reason_text
        )

        db.session.add(new_record)
        db.session.commit()

        return render_template("index.html", result={
            "item": item,
            "best_material": best["Material"],
            "total_cost": round(total_cost, 2),
            "total_co2": round(total_co2, 2),
            "score": round(score, 2),
            "reasons": reason_text
        })

    return render_template("index.html")

# =========================
# EXPORT EXCEL
# =========================
@app.route("/export_excel")
def export_excel():

    last = Recommendation.query.order_by(Recommendation.id.desc()).first()
    if not last:
        return "No data available"

    output = io.BytesIO()

    df = pd.DataFrame([{
        "Item": last.item,
        "Best Material": last.best_material,
        "Total Cost": last.total_cost,
        "Total CO2": last.total_co2,
        "Strength": last.strength,
        "Sustainability Score": last.sustainability_score,
        "Reasons": last.reasons
    }])

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Recommendation")

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="EcoPackAI_Recommendation.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# =========================
# EXPORT PDF (REPORTLAB)
# =========================
@app.route("/export_pdf")
def export_pdf():

    last = Recommendation.query.order_by(Recommendation.id.desc()).first()
    if not last:
        return "No data available"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>EcoPackAI Recommendation Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    data = [
        ["Item", last.item],
        ["Best Material", last.best_material],
        ["Total Cost", str(last.total_cost)],
        ["Total CO2", str(last.total_co2)],
        ["Strength", str(last.strength)],
        ["Sustainability Score", str(last.sustainability_score)],
        ["Reasons", last.reasons]
    ]

    table = Table(data, colWidths=[2.5 * inch, 3.5 * inch])
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="EcoPackAI_Recommendation.pdf",
        mimetype="application/pdf"
    )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
