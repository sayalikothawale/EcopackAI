import pandas as pd
import numpy as np
from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# ==============================
# DATABASE CONFIG
# ==============================
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:MySQL123@localhost/ecopack_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==============================
# DATABASE MODEL
# ==============================
class Recommendation(db.Model):
    __tablename__ = "recommendation"   # Uses public.recommendation

    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100))
    weight = db.Column(db.Float)
    units = db.Column(db.Integer)
    fragility = db.Column(db.String(10))
    category = db.Column(db.String(50))
    best_material = db.Column(db.String(200))
    total_cost = db.Column(db.Float)
    total_co2 = db.Column(db.Float)
    sustainability_score = db.Column(db.Float)


# ==============================
# LOAD DATASET
# ==============================
df = pd.read_csv("data/final/ml_dataset.csv")

# ==============================
# HOME ROUTE
# ==============================
@app.route("/", methods=["GET", "POST"])
def home():

    top5 = None
    best = None

    if request.method == "POST":

        item = request.form.get("item")
        weight = float(request.form.get("weight"))
        units = int(request.form.get("units"))
        fragility = request.form.get("fragility")

        # CATEGORY DETECTION
        item_lower = item.lower()

        if any(w in item_lower for w in ["apple", "mango", "fruit"]):
            category = "food"
        elif any(w in item_lower for w in ["laptop", "mobile"]):
            category = "electronics"
        else:
            category = "general"

        max_cost = float(df["Cost_per_kg"].max())
        max_co2 = float(df["CO2_Emission_kg"].max())

        results = []

        for _, row in df.iterrows():

            eco_score = 1 - (float(row["CO2_Emission_kg"]) / max_co2)
            cost_score = 1 - (float(row["Cost_per_kg"]) / max_cost)
            biodeg_score = 1 if row["Biodegradable"] == "Yes" else 0.5

            sustainability_score = (
                eco_score * 0.4 +
                cost_score * 0.3 +
                biodeg_score * 0.3
            )

            sustainability_score = float(round(sustainability_score * 100, 2))

            total_cost = float(round(float(row["Cost_per_kg"]) * weight * units, 2))
            total_co2 = float(round(float(row["CO2_Emission_kg"]) * weight * units, 2))

            results.append({
                "Material": str(row["Material_Name"]),
                "Total_Cost": total_cost,
                "Total_CO2": total_co2,
                "Score": sustainability_score
            })

        results = sorted(results, key=lambda x: x["Score"], reverse=True)
        top5 = results[:5]

        if top5:
            best = top5[0]

            # SAVE TO DATABASE (All converted to Python types)
            try:
                new_entry = Recommendation(
                    item=str(item),
                    weight=float(weight),
                    units=int(units),
                    fragility=str(fragility),
                    category=str(category),
                    best_material=str(best["Material"]),
                    total_cost=float(best["Total_Cost"]),
                    total_co2=float(best["Total_CO2"]),
                    sustainability_score=float(best["Score"])
                )

                db.session.add(new_entry)
                db.session.commit()

            except Exception as e:
                db.session.rollback()
                print("Database Error:", e)

    return render_template("index.html", top5=top5, best=best)



# ==============================
# EXPORT EXCEL
# ==============================
@app.route('/export_excel')
def export_excel():

    data = Recommendation.query.all()

    rows = []
    for r in data:
        rows.append({
            "Item": r.item,
            "Weight": r.weight,
            "Units": r.units,
            "Fragility": r.fragility,
            "Category": r.category,
            "Best Material": r.best_material,
            "Total Cost": r.total_cost,
            "Total CO2": r.total_co2,
            "Sustainability Score": r.sustainability_score
        })

    df_export = pd.DataFrame(rows)

    file_path = "sustainability_report.xlsx"
    df_export.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)


# ==============================
# EXPORT PDF
# ==============================
@app.route('/export_pdf')
def export_pdf():

    data = Recommendation.query.all()

    file_path = "sustainability_report.pdf"
    doc = SimpleDocTemplate(file_path)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Sustainability Report", styles['Title']))
    elements.append(Spacer(1, 20))

    table_data = [[
        "Item",
        "Category",
        "Material",
        "Cost",
        "CO2",
        "Score"
    ]]

    for r in data:
        table_data.append([
            r.item,
            r.category,
            r.best_material,
            r.total_cost,
            r.total_co2,
            r.sustainability_score
        ])

    table = Table(table_data)
    elements.append(table)

    doc.build(elements)

    return send_file(file_path, as_attachment=True)


# ==============================
# RUN APP
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
