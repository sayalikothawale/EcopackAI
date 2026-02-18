<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/861d4c9d-65da-4bf9-8b57-bd464bb8c30f" />EcoPack AI 🌱
AI-Powered Sustainable Packaging recommendation System

## 🔗 Live Deployment
https://ecopackai-s2mq.onrender.com

---

## 📌 Project Overview

EcoPackAI is a full-stack AI-powered web application designed to recommend sustainable packaging materials based on product characteristics, environmental impact, and cost efficiency.

The system evaluates packaging materials using sustainability metrics such as:

- CO₂ Emission
- Cost Efficiency
- Biodegradability
- Material Strength
- Environmental Impact Score

It helps businesses transition toward eco-friendly packaging solutions while maintaining durability and cost-effectiveness.

# 🎯 Problem Statement

Traditional packaging relies heavily on non-biodegradable materials that:

- Increase environmental damage
- Raise carbon footprint
- Increase long-term operational costs
- Lack intelligent decision-support systems

EcoPackAI solves this by providing AI-driven packaging recommendations with sustainability analytics.

# 🏗️ System Architecture

The system follows a modular full-stack architecture:

┌──────────────────────────────────────────────────────────
─────┐
│                    🌱 EcoPackAI System                       │
└───────────────────────────────────────────────────────────────┘

┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│   Frontend       │◄──────►│   Flask Backend  │◄──────►│   MySQL DB      │
│ HTML/CSS/JS      │  HTTP  │   (Port 5000)    │  TCP   │  (Port 3306)    │
│ localhost:3000   │        │                  │        │                  │
└──────────────────┘        └─────────┬────────┘        └─────────┬────────┘
                                      │                            │
                         ┌────────────┼────────────┐               │
                         │            │            │               │
                   ┌─────▼─────┐ ┌────▼─────┐ ┌────▼─────┐       │
                   │ Session   │ │ ML Model  │ │ History  │       │
                   │ Management│ │ (.pkl)    │ │  Saver   │       │
                   └───────────┘ └───────────┘ └──────────┘       │
                                      │                            │
                                      └──────────────┬─────────────┘
                                                     │
                                              ┌──────▼──────┐
                                              │  Report      │
                                              │ Generator    │
                                              │ (PDF/Excel)  │
                                              └──────┬──────┘
                                                     │
                                              ┌──────▼──────┐
                                              │ PowerBI     │
                                              │ Dashboard   │
                                              │ (Analytics) │
                                              └─────────────┘


## 🔗 Live Deployment
https://ecopackai-s2mq.onrender.com

---
## 📌 Project Overview

EcopackAI-main/
│
├── app.py                              # Main Flask Application
├── dashboard.py                        # Dashboard backend logic
├── models.py                           # Database models
├── config.py                           # Configuration settings
├── seed.py                             # Database seeding script
│
├── Procfile                            # Render deployment config
├── requirements.txt                    # Python dependencies
├── README.md                           # Project documentation
├── LICENSE
├── .gitignore
│
├── EcoPack_AI_Dashboard.pbix           # PowerBI Dashboard file
│
├── models/                             # Trained ML Models
│   ├── category_encoder.pkl
│   ├── co2_model.pkl
│   ├── cost_model.pkl
│   ├── material_recommendation_model.pkl
│   ├── scaler.pkl
│
├── data/
│   ├── raw/
│   │   ├── materials_database_600.xlsx
│   │   ├── real_packaging_history.xlsx
│   │
│   ├── processed/
│   │   ├── cleaned_materials.csv
│   │   ├── cleaned_packaging_history.csv
│   │
│   ├── final/
│   │   ├── ml_dataset.csv
│
├── notebooks/                          # ML Development Steps
│   ├── 01_data_collection.py
│   ├── 02_data_cleaning.py
│   ├── 03_feature_engineering.py
│   ├── 04_dataset_preparation.py
│   ├── 05_model_training.py
│   ├── 06_recommendation_engine.py
│
├── templates/                          # Frontend HTML
│   ├── index.html
│   ├── result.html
│   ├── dashboard.html
│
├── static/
│   ├── style.css
│
├── dashboard/
│   └── reports/
│       ├── sustainability_report.xlsx
│       ├── sustainability_report.pdf
│
└── .vscode/
    └── settings.json


EcoPackAI is a full-stack AI-powered web application designed to recommend sustainable packaging materials based on product characteristics, environmental impact, and cost efficiency.

The system evaluates packaging materials using sustainability metrics such as:

- CO₂ Emission
- Cost Efficiency
- Biodegradability
- Material Strength
- Environmental Impact Score

It helps businesses transition toward eco-friendly packaging solutions while maintaining durability and cost-effectiveness.

---

# 🎯 Problem Statement

Traditional packaging relies heavily on non-biodegradable materials that:

- Increase environmental damage
- Raise carbon footprint
- Increase long-term operational costs
- Lack intelligent decision-support systems

EcoPackAI solves this by providing AI-driven packaging recommendations with sustainability analytics.

---

# 🏗️ System Architecture

The system follows a modular full-stack architecture:



Components:

- Frontend (HTML + CSS + Bootstrap)
- Flask Backend API
- PostgreSQL Cloud Database
- AI Scoring Model
- Report Generation (Excel + PDF)
- Deployment on Render

# 📅 Milestone-wise Implementation

## 🚀 Milestone 1 (Week 1–2)
### Module 1: Data Collection & Management

- Collected eco-friendly packaging material dataset
- Attributes included:
  - Material Name
  - Cost per kg
  - CO₂ Emission
  - Tensile Strength
  - Biodegradability

### Module 2: Data Cleaning & Feature Engineering

- Handled missing values
- Converted numerical columns
- Engineered:
  - Sustainability Score
  - Eco Score
  - Cost Score
  - Strength Score
- Normalized material metrics
- Created structured dataset (CSV format)
---

## 🚀 Milestone 2 (Week 3–4)

### Module 3: ML Dataset Preparation

- Selected relevant material features
- Prepared scoring mechanism
- Designed weighted sustainability index

### Module 4: AI Recommendation Engine

- Built sustainability ranking logic
- Computed:
  - Total Cost
  - Total CO₂ Emission
  - Material Strength Compatibility
- Generated Top 5 Ranked Recommendations

---

## 🚀 Milestone 3 (Week 5–6)

### Module 5: Flask Backend Integration

- Created POST endpoint for user input
- Connected Flask to PostgreSQL
- Stored best material recommendations
- Implemented error handling
- Managed cloud environment variables

### Module 6: Frontend UI Development

- Built interactive input form
- Displayed:
  - Best material
  - Top 5 ranked materials
  - Sustainability Score
  - Environmental metrics
- Integrated Bootstrap responsive UI

---

## 🚀 Milestone 4 (Week 7–8)

### Module 7: Business Intelligence & Reporting

- Developed sustainability reporting system
- Implemented:
  - Excel report export
  - PDF report generation using ReportLab
- Displayed environmental impact results

### Module 8: Deployment & Documentation

- Deployed on Render Cloud
- Connected to PostgreSQL cloud database
- Configured environment variables
- Created professional documentation
- Version-controlled via GitHub

---

# 🧠 AI Sustainability Scoring Formula

Sustainability Score is calculated using weighted factors:

- Eco Impact (30%)
- Cost Efficiency (25%)
- Biodegradability (20%)
- Strength Compatibility (25%)

Final Score = Weighted sustainability performance out of 100.

---

# 📊 Key Features

✅ AI-based material ranking  
✅ Sustainability score calculation  
✅ CO₂ footprint estimation  
✅ Cost analysis   
✅ PostgreSQL data storage  
✅ Excel report export  
✅ PDF sustainability report  
✅ Cloud deployment  

---

# 🛠️ Tech Stack

- Python
- Flask
- PostgreSQL
- Pandas
- NumPy
- ReportLab
- HTML / CSS / Bootstrap
- Render Cloud Deployment

---

# 📦 Deployment

The application is deployed on Render:

🌐 https://ecopackai-s2mq.onrender.com

Database: PostgreSQL (Render Cloud)
