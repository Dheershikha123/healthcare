# 🏥 Patient Health Monitoring Dashboard — HCL PID090

A data-driven healthcare analytics project designed to analyze patient records, hospital admissions, diagnoses, billing information, and hospital performance. The project transforms raw healthcare datasets into meaningful insights to support data-driven decision-making.

## 📌 Project Overview

Healthcare organizations generate large volumes of patient and hospital data. Analyzing this data can help identify patient demographics, admission patterns, hospital utilization, diagnosis trends, and healthcare costs.

The **Patient Health Monitoring Dashboard** aims to organize, clean, analyze, and visualize healthcare data through an integrated data analytics workflow.

This project was developed as part of the **HCL college project initiative (PID090)**.

## 🎯 Objectives

- Analyze patient demographics and health-related records.
- Monitor hospital admission and discharge patterns.
- Explore diagnosis distributions and healthcare trends.
- Analyze hospital billing and treatment costs.
- Compare hospital performance and hospital tiers.
- Build an interactive dashboard for exploring healthcare KPIs.
- Prepare structured data for future predictive analytics.

## 📊 Dataset Overview

The project uses a synthetic healthcare dataset containing multiple interconnected CSV files.

| Dataset | Records | Description |
|---|---:|---|
| ADMISSIONS | 120,000 | Patient admission and hospital stay information |
| PATIENTS | 86,400 | Patient demographic information |
| DIAGNOSES | 271,341 | Patient diagnosis records |
| BILLING | 120,000 | Hospital billing and cost information |
| HOSPITALS | 33 | Hospital details and classifications |

### Master Dataset

- **Rows:** 120,000
- **Columns:** 43
- **Admission date range:** January 2015 – December 2024
- **Format:** CSV

The cleaned master dataset integrates relevant information from the source files for downstream analysis.

## 🛠️ Tech Stack

- **Programming Language:** Python
- **Data Analysis:** Pandas, NumPy
- **Data Visualization:** Plotly / Matplotlib / Seaborn, as applicable
- **Dashboard:** Streamlit or Power BI, depending on the final implementation
- **Machine Learning:** Scikit-learn, if predictive models are implemented
- **Version Control:** Git and GitHub

## ⚙️ Project Workflow

1. **Data Collection:** Load the source healthcare CSV files.
2. **Data Cleaning:** Handle missing values, duplicates, inconsistent formats, and invalid records.
3. **Data Integration:** Combine relevant datasets using appropriate identifiers.
4. **Exploratory Data Analysis:** Examine patient demographics, admissions, diagnoses, billing, and hospital distributions.
5. **KPI Development:** Calculate metrics such as average length of stay and average hospital cost.
6. **Dashboard Development:** Present key metrics and trends through interactive charts and filters.
7. **Predictive Analytics:** Extend the project with suitable machine-learning models where required.

## 📈 Key Insights Explored

- Patient age and gender distribution.
- Hospital admission trends over time.
- Average length of hospital stay.
- Diagnosis frequency and distribution.
- Average and total healthcare costs.
- Hospital distribution by tier.
- Missing data patterns and data quality.

### Initial Dataset Findings

- Average length of stay: approximately **6.85 days**.
- Average billing cost: approximately **₹95,779.53**.
- Hospitals represented: **33**.
- Hospital classifications include Tier 1, Tier 2, and Tier 3.

*These figures describe the analyzed dataset and should not be interpreted as real-world clinical benchmarks.*

## 📁 Project Structure

```text
patient-health-monitoring-dashboard/
│
├── data/
│   └── hospital_dataset/
│       ├── raw/
│       └── cleaned/
│           └── master_patient_health.csv
│
├── notebooks/
│   └── exploratory_data_analysis.ipynb
│
├── src/
│   ├── data_cleaning.py
│   ├── data_processing.py
│   └── analysis.py
│
├── dashboard/
│   └── app.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

*The structure above is a suggested organization. Adjust it to match your actual repository.*

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd patient-health-monitoring-dashboard
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Dashboard

If the project uses Streamlit:

```bash
streamlit run dashboard/app.py
```

If you use Power BI, open the `.pbix` report in Power BI Desktop instead.

## 🔮 Future Enhancements

- Add interactive filters for dates, hospital tiers, diagnoses, and demographics.
- Develop predictive models for patient readmission or length of stay, if suitable target labels are available.
- Add anomaly detection for unusual billing patterns.
- Improve data quality monitoring and validation.
- Implement role-based access and secure handling of patient information for production use.
- Deploy the dashboard for easier access to analytical insights.

## 👩‍💻 Contributors

Developed as part of the HCL PID090 college project.

**Project Domain:** Healthcare Analytics and Patient Monitoring

## ⚠️ Data Disclaimer

This project uses synthetic healthcare data for educational and analytical purposes. Dashboard findings are intended for demonstration and research, not for clinical diagnosis or treatment decisions.

## 📄 License

Add a license appropriate to your project before distributing or reusing the code.
