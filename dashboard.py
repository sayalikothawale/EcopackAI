import os
import pandas as pd
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, send_file
from sqlalchemy import create_engine
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from openpyxl import Workbook

dashboard = Blueprint("dashboard", __name__)

# Database connection
engine = create_engine("postgresql://postgres:MySQL123@localhost/ecopack_db")

REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)


# ==========================================
# LOAD DATA
# ==========================================
def load_data():
    df = pd.read_sql("SELECT * FROM recommendation", engine)
    return df


# ==========================================
# CO2 REDUCTION %
# ==========================================
def calculate_co2_reduction(df):
    baseline = df["total_co2"].max()
    current = df["total_co2"].mean()

    reduction = ((baseline - current) / baseline) * 100 if baseline > 0 else 0
    return round(reduction, 2)


# ==========================================
# COST SAVINGS %
# ==========================================
def calculate_cost_savings(df):
    baseline = df["total_cost"].max()
    current = df["total_cost"].mean()

    savings = ((baseline - current) / baseline) * 100 if baseline > 0 else 0
    return round(savings, 2)


# ==========================================
# MATERIAL USAGE TREND CHART
# ==========================================
def generate_material_trend_chart(df):

    material_counts = df["best_material"].value_counts().head(10)

    plt.figure()
    material_counts.plot(kind="bar")
    plt.title("Top 10 Material Usage Trends")
    plt.xlabel("Material")
    plt.ylabel("Usage Count")

    chart_path = os.path.join(REPORT_FOLDER, "material_trend.png")
    plt.savefig(chart_path)
    plt.close()

    return chart_path


# ==========================================
# PDF EXPORT
# ==========================================
def export_pdf_report(df, co2_reduction, cost_savings):

    file_path = os.path.join(REPORT_FOLDER, "sustainability_report.pdf")
    doc = SimpleDocTemplate(file_path)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph("Sustainability Business Intelligence Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"CO2 Reduction: {co2_reduction}%", styles["Normal"]))
    elements.append(Paragraph(f"Cost Savings: {cost_savings}%", styles["Normal"]))
    elements.append(Spacer(1, 12))

    summary_data = [
        ["Metric", "Value"],
        ["Total Records", str(len(df))],
        ["Average Sustainability Score", str(round(df["sustainability_score"].mean(), 2))]
    ]

    table = Table(summary_data)
    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ])

    elements.append(table)
    doc.build(elements)

    return file_path


# ==========================================
# EXCEL EXPORT
# ==========================================
def export_excel_report(df):

    file_path = os.path.join(REPORT_FOLDER, "sustainability_report.xlsx")
    wb = Workbook()
    ws = wb.active
    ws.title = "Sustainability Data"

    ws.append(list(df.columns))

    for _, row in df.iterrows():
        ws.append(list(row))

    wb.save(file_path)
    return file_path


# ==========================================
# DASHBOARD ROUTE
# ==========================================
@dashboard.route("/dashboard")
def show_dashboard():

    df = load_data()

    if df.empty:
        return render_template("dashboard.html", empty=True)

    co2_reduction = calculate_co2_reduction(df)
    cost_savings = calculate_cost_savings(df)
    chart_path = generate_material_trend_chart(df)

    return render_template(
        "dashboard.html",
        empty=False,
        co2_reduction=co2_reduction,
        cost_savings=cost_savings,
        chart_path=chart_path
    )


# ==========================================
# EXPORT ROUTES
# ==========================================
@dashboard.route("/export/pdf")
def export_pdf():

    df = load_data()
    co2_reduction = calculate_co2_reduction(df)
    cost_savings = calculate_cost_savings(df)

    file_path = export_pdf_report(df, co2_reduction, cost_savings)
    return send_file(file_path, as_attachment=True)


@dashboard.route("/export/excel")
def export_excel():

    df = load_data()
    file_path = export_excel_report(df)
    return send_file(file_path, as_attachment=True)
