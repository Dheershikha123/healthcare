import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, mean_absolute_error, mean_squared_error, r2_score

@st.cache_resource
def get_class_model(df_in):
    d = df_in.copy()
    thresh = d['total_cost_inr'].quantile(0.95)
    d['high_cost'] = (d['total_cost_inr'] >= thresh).astype(int)
    num_cols = ['age', 'comorbidity_count', 'prev_admissions', 'num_procedures', 'num_diagnoses', 'beds']
    cat_cols = ['gender', 'ward_type', 'admit_type', 'primary_category', 'insurance_type', 'bpl_card', 'tier', 'teaching']
    X = d[num_cols + cat_cols].fillna(0)
    X[cat_cols] = X[cat_cols].astype(str)
    y = d['high_cost']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    prep = ColumnTransformer([('num', StandardScaler(), num_cols), ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)])
    X_tr = prep.fit_transform(X_train)
    rf = RandomForestClassifier(class_weight="balanced", random_state=42, n_estimators=50, max_depth=10, n_jobs=-1)
    lr = LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000)
    rf.fit(X_tr, y_train)
    lr.fit(X_tr, y_train)
    
    cat_names = prep.named_transformers_['cat'].get_feature_names_out(cat_cols)
    feat_names = num_cols + list(cat_names)
    
    X_te = prep.transform(X_test)
    rf_pred = rf.predict(X_te)
    lr_pred = lr.predict(X_te)
    metrics = {
        'rf': {'acc': accuracy_score(y_test, rf_pred), 'prec': precision_score(y_test, rf_pred, zero_division=0), 'rec': recall_score(y_test, rf_pred, zero_division=0), 'f1': f1_score(y_test, rf_pred, zero_division=0), 'auc': roc_auc_score(y_test, rf.predict_proba(X_te)[:, 1])},
        'lr': {'acc': accuracy_score(y_test, lr_pred), 'prec': precision_score(y_test, lr_pred, zero_division=0), 'rec': recall_score(y_test, lr_pred, zero_division=0), 'f1': f1_score(y_test, lr_pred, zero_division=0), 'auc': roc_auc_score(y_test, lr.predict_proba(X_te)[:, 1])}
    }
    return thresh, prep, rf, lr, feat_names, num_cols, cat_cols, metrics

@st.cache_resource
def get_reg_model(df_in):
    d = df_in.copy().dropna(subset=['los_days'])
    if 'admit_date' in d.columns:
        d['admission_year'] = pd.to_datetime(d['admit_date']).dt.year
        d['admission_month'] = pd.to_datetime(d['admit_date']).dt.month
    else:
        d['admission_year'] = 2026
        d['admission_month'] = 1
    num_cols = ['age', 'comorbidity_count', 'prev_admissions', 'num_procedures', 'num_diagnoses', 'beds', 'admission_year', 'admission_month']
    cat_cols = ['gender', 'ward_type', 'admit_type', 'primary_category', 'insurance_type', 'bpl_card', 'tier', 'teaching']
    X = d[num_cols + cat_cols].fillna(0)
    X[cat_cols] = X[cat_cols].astype(str)
    y = d['los_days']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    prep = ColumnTransformer([('num', StandardScaler(), num_cols), ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)])
    X_tr = prep.fit_transform(X_train)
    rf = RandomForestRegressor(random_state=42, n_estimators=50, max_depth=10, n_jobs=-1)
    lin = LinearRegression()
    rf.fit(X_tr, y_train)
    lin.fit(X_tr, y_train)
    
    X_te = prep.transform(X_test)
    rf_pred = rf.predict(X_te)
    lin_pred = lin.predict(X_te)
    metrics = {
        'rf': {'mae': mean_absolute_error(y_test, rf_pred), 'rmse': np.sqrt(mean_squared_error(y_test, rf_pred)), 'r2': r2_score(y_test, rf_pred)},
        'lin': {'mae': mean_absolute_error(y_test, lin_pred), 'rmse': np.sqrt(mean_squared_error(y_test, lin_pred)), 'r2': r2_score(y_test, lin_pred)}
    }
    return prep, rf, lin, num_cols, cat_cols, metrics

def nav_to(page, p_id=None):
    st.session_state.pa_page = page
    if p_id:
        st.session_state.pa_pid = p_id
    st.rerun()

def btn_back(target='Overview', label='🔙 Back'):
    if st.button(label):
        nav_to(target)

def make_breadcrumb(crumbs):
    html = "<div style='font-size: 14px; color: #607D8B; margin-bottom: 20px; font-weight: 500;'>"
    html += " ➔ ".join(crumbs)
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def render_search(data):
    st.title("Patient Search")
    st.markdown("Find and select a patient to begin a deep analytical dive.")
    
    with st.expander("🔍 Search and Filters", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            name_q = st.text_input("Search by Name")
            age_q = st.number_input("Maximum Age", min_value=0, max_value=120, value=120)
        with c2:
            pid_q = st.text_input("Patient ID")
            gen_q = st.selectbox("Gender", ["All", "Male", "Female", "Other"])
        with c3:
            adm_q = st.text_input("Admission ID")
            hosp_q = st.selectbox("Hospital", ["All"] + sorted(data['name'].dropna().unique().tolist()))
            
    df = data.copy()
    if name_q: df = df[df['patient_name'].str.contains(name_q, case=False, na=False)] if 'patient_name' in df.columns else df
    if pid_q: df = df[df['patient_id'].astype(str).str.contains(pid_q, case=False, na=False)]
    if adm_q: df = df[df['admission_id'].astype(str).str.contains(adm_q, case=False, na=False)]
    if hosp_q != "All": df = df[df['name'] == hosp_q]
    if gen_q != "All": df = df[df['gender'] == gen_q]
    df = df[df['age'] <= age_q]
    
    if 'admit_date' in df.columns:
        df = df.sort_values('admit_date', ascending=False)
        
    df_unique = df.drop_duplicates(subset=['patient_id'])
    st.markdown(f"**{len(df_unique)}** patients found.")
    
    disp = df_unique.head(50)
    for idx, row in disp.iterrows():
        with st.container():
            st.markdown(f'''
            <div style="border: 1px solid #E0E0E0; border-radius: 8px; padding: 15px; margin-bottom: 10px; background-color: #FAFAFA;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #16324F;">{row.get('patient_name', 'Patient')} ({row['patient_id']})</div>
                        <div style="font-size: 0.9rem; color: #555;">Age: {row['age']} | Gender: {row['gender']} | Ward: {row.get('ward_type', 'N/A')}</div>
                        <div style="font-size: 0.9rem; color: #555;">Latest Hospital: {row.get('name', 'N/A')} | Outcome: {row.get('discharge_type', 'N/A')}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("View Patient", key=f"vp_{row['patient_id']}"):
                nav_to("Overview", p_id=row['patient_id'])

def get_patient_data(data):
    pid = st.session_state.pa_pid
    return data[data['patient_id'] == pid].sort_values('admit_date', ascending=False) if 'admit_date' in data.columns else data[data['patient_id'] == pid]

def render_overview(data):
    make_breadcrumb(["Patient Analysis", "Patient Search", "Patient Overview"])
    pdata = get_patient_data(data)
    if pdata.empty: return st.error("Patient not found.")
    latest = pdata.iloc[0]
    
    st.markdown(f"## {latest.get('patient_name', 'Patient')}")
    st.markdown(f"**ID:** {latest['patient_id']} &nbsp;|&nbsp; **Age:** {latest['age']} &nbsp;|&nbsp; **Gender:** {latest['gender']} &nbsp;|&nbsp; **State:** {latest.get('patient_state', 'N/A')} &nbsp;|&nbsp; **Insurance:** {latest.get('insurance_type', 'N/A')}")
    
    st.markdown("---")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Admissions", len(pdata))
    m2.metric("Previous Admissions", latest.get('prev_admissions', 0))
    m3.metric("Latest Ward", latest.get('ward_type', 'N/A'))
    m4.metric("Latest Diagnosis", latest.get('primary_diagnosis', 'N/A'))
    m5.metric("Latest Outcome", latest.get('discharge_type', 'N/A'))
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Analytical Modules")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🩺 Clinical Profile", use_container_width=True): nav_to("Clinical")
        if st.button("🚑 Admission History", use_container_width=True): nav_to("Admission")
    with col2:
        if st.button("🦠 Diagnosis", use_container_width=True): nav_to("Diagnosis")
        if st.button("💰 Financial Summary", use_container_width=True): nav_to("Financial")
    with col3:
        if st.button("🏥 Hospital Information", use_container_width=True): nav_to("Hospital")
        if st.button("🤖 Predictive Analytics", use_container_width=True): nav_to("Predictive")
        
    btn_back('Search', '🔙 Back to Search')

def render_clinical(data):
    make_breadcrumb(["Patient Analysis", "Patient Overview", "Clinical Profile"])
    pdata = get_patient_data(data)
    latest = pdata.iloc[0]
    st.title("Clinical Profile")
    
    st.markdown(f"**Name:** {latest.get('patient_name', 'Patient')} &nbsp;|&nbsp; **ID:** {latest['patient_id']}")
    st.markdown("---")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Age:** {latest['age']}")
        st.markdown(f"**Gender:** {latest['gender']}")
        st.markdown(f"**State:** {latest.get('patient_state', 'N/A')}")
    with c2:
        st.markdown(f"**BPL Status:** {latest.get('bpl_card', 'N/A')}")
        st.markdown(f"**Insurance Type:** {latest.get('insurance_type', 'N/A')}")
    with c3:
        st.markdown(f"**Comorbidities:** {latest.get('comorbidity_count', 0)}")
        st.markdown(f"**Previous Admissions:** {latest.get('prev_admissions', 0)}")
        
    st.markdown("### Clinical Summary")
    st.info(f"Patient has a total of {len(pdata)} recorded admissions. The latest recorded comorbid burden is {latest.get('comorbidity_count', 0)}.")
    
    st.markdown("### Related Analysis")
    r1, r2, r3 = st.columns(3)
    with r1:
        if st.button("Go to Diagnosis"): nav_to("Diagnosis")
    with r2:
        if st.button("Go to Admission Details"): nav_to("Admission")
    
    btn_back()

def render_admission(data):
    make_breadcrumb(["Patient Analysis", "Patient Overview", "Admission Details"])
    pdata = get_patient_data(data)
    st.title("Admission History")
    
    for idx, row in pdata.iterrows():
        with st.expander(f"Admission ID: {row.get('admission_id', f'A-{idx}')} | Date: {row.get('admit_date', 'N/A')} ({row.get('admit_type', 'N/A')})", expanded=True):
            tab1, tab2, tab3 = st.tabs(["Overview", "Treatment & Stay", "Outcome"])
            with tab1:
                st.write(f"**Hospital:** {row.get('name', 'N/A')}")
                st.write(f"**Ward:** {row.get('ward_type', 'N/A')}")
            with tab2:
                st.write(f"**Length of Stay:** {row.get('los_days', 'N/A')} days")
                st.write(f"**Procedures:** {row.get('num_procedures', 0)}")
            with tab3:
                st.write(f"**Discharge Type:** {row.get('discharge_type', 'N/A')}")
                st.write(f"**Discharge Date:** {row.get('discharge_date', 'N/A')}")
                
    btn_back()

def render_diagnosis(data):
    make_breadcrumb(["Patient Analysis", "Patient Overview", "Diagnosis Details"])
    pdata = get_patient_data(data)
    latest = pdata.iloc[0]
    st.title("Diagnosis Details")
    
    st.write(f"**Admission ID:** {latest.get('admission_id', 'Latest')}")
    
    with st.expander(f"Primary Diagnosis: {latest.get('primary_diagnosis', 'N/A')}", expanded=True):
        st.write(f"**ICD-10:** {latest.get('icd10_code', 'N/A')}")
        st.write(f"**Diagnosis Category:** {latest.get('primary_category', 'N/A')}")
        st.write(f"**Number of Diagnoses Recorded:** {latest.get('num_diagnoses', 1)}")
    
    btn_back()

def render_financial(data):
    make_breadcrumb(["Patient Analysis", "Patient Overview", "Financial Details"])
    pdata = get_patient_data(data)
    latest = pdata.iloc[0]
    st.title("Financial Details")
    
    t_cost = latest.get('total_cost_inr', 0)
    gov_sub = latest.get('govt_subsidy_inr', 0)
    oop_cost = latest.get('out_of_pocket_inr', 0)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cost", f"₹{t_cost:,.2f}")
    col2.metric("Government Subsidy", f"₹{gov_sub:,.2f}")
    col3.metric("Out-of-Pocket Cost", f"₹{oop_cost:,.2f}")
    
    st.write(f"**Insurance Type:** {latest.get('insurance_type', 'N/A')}")
    st.write(f"**BPL Status:** {latest.get('bpl_card', 'N/A')}")
    
    st.markdown("### Financial Context")
    st.info(f"Observed total cost for the current admission is ₹{t_cost:,.2f}. The associated subsidy absorbed ₹{gov_sub:,.2f}, resulting in an out-of-pocket amount of ₹{oop_cost:,.2f}.")
    
    btn_back()

def render_hospital(data):
    make_breadcrumb(["Patient Analysis", "Patient Overview", "Hospital Details"])
    pdata = get_patient_data(data)
    latest = pdata.iloc[0]
    st.title("Hospital Information")
    
    st.markdown("### Facility")
    st.write(f"**Hospital Name:** {latest.get('name', 'N/A')}")
    st.write(f"**Hospital ID:** {latest.get('hospital_id', 'N/A')}")
    st.write(f"**State:** {latest.get('hospital_state', 'N/A')}")
    st.write(f"**Tier:** {latest.get('tier', 'N/A')}")
    st.write(f"**Teaching Status:** {latest.get('teaching', 'N/A')}")
    st.write(f"**Beds:** {latest.get('beds', 'N/A')}")
    
    st.markdown("### Selected Admission Context")
    st.write(f"**Ward:** {latest.get('ward_type', 'N/A')}")
    st.write(f"**Admission Type:** {latest.get('admit_type', 'N/A')}")
    st.write(f"**Length of Stay:** {latest.get('los_days', 'N/A')} days")
    st.write(f"**Outcome:** {latest.get('discharge_type', 'N/A')}")
    
    btn_back()

def render_predictive(data):
    make_breadcrumb(["Patient Analysis", "Patient Overview", "Predictive Analytics"])
    st.title("Predictive Analytics")
    st.markdown("#### Model-based analysis for the selected patient admission")
    pdata = get_patient_data(data)
    latest = pdata.iloc[0].copy()
    
    thresh, prep_c, rf_c, lr_c, feat_names, num_cols, cat_cols, metrics_c = get_class_model(data)
    prep_r, rf_r, lr_r, num_cols_r, cat_cols_r, metrics_r = get_reg_model(data)
    
    st.markdown("### Patient Profile Used by Model")
    with st.container():
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Age:** {latest['age']}")
        c1.write(f"**Gender:** {latest['gender']}")
        c1.write(f"**Comorbidity Count:** {latest.get('comorbidity_count', 0)}")
        
        c2.write(f"**Ward Type:** {latest.get('ward_type', 'N/A')}")
        c2.write(f"**Admission Type:** {latest.get('admit_type', 'N/A')}")
        c2.write(f"**Previous Admissions:** {latest.get('prev_admissions', 0)}")
        
        c3.write(f"**Procedures:** {latest.get('num_procedures', 0)}")
        c3.write(f"**Diagnosis Category:** {latest.get('primary_category', 'N/A')}")
        c3.write(f"**Hospital Tier:** {latest.get('tier', 'N/A')}")
        c3.write(f"**Insurance Type:** {latest.get('insurance_type', 'N/A')}")
        c3.write(f"**BPL Status:** {latest.get('bpl_card', 'N/A')}")

    st.markdown("---")
    
    st.markdown("### High-Cost Admission Prediction")
    import datetime
    
    row = dict(latest)
    if 'admit_date' in row and pd.notnull(row['admit_date']):
        row['admission_year'] = pd.to_datetime(row['admit_date']).year
        row['admission_month'] = pd.to_datetime(row['admit_date']).month
    else:
        row['admission_year'] = 2026
        row['admission_month'] = 1
        
    inp_df = pd.DataFrame([row])
    
    X_c = prep_c.transform(inp_df)
    pred_c = rf_c.predict(X_c)[0]
    prob_c = rf_c.predict_proba(X_c)[0][1] * 100
    
    lbl = "HIGH COST" if pred_c == 1 else "NORMAL COST"
    color = "#D32F2F" if pred_c == 1 else "#388E3C"
    
    st.markdown(f"**Prediction:** <span style='color:{color}; font-weight:bold; font-size:1.2rem;'>{lbl}</span>", unsafe_allow_html=True)
    st.markdown(f"**High-Cost Probability:** {prob_c:.1f}%")
    st.progress(int(prob_c) / 100.0)
    st.caption(f"Prediction threshold: 95th percentile cost threshold (₹{thresh:,.2f})")
    
    X_c_dense = X_c.toarray() if hasattr(X_c, "toarray") else X_c
    global_imp = rf_c.feature_importances_
    local_contrib = (global_imp * X_c_dense[0])
    
    contribs = list(zip(feat_names, local_contrib))
    contribs.sort(key=lambda x: abs(x[1]), reverse=True)
    top_contribs = contribs[:5]
    
    with st.expander("Why did the model make this prediction?"):
        st.write("**Top Model Contributors**")
        for i, (fn, cv) in enumerate(top_contribs):
            clean_fn = fn.split('__')[-1].replace('_', ' ').title()
            st.write(f"{i+1}. {clean_fn}")
            
        if st.button("View Detailed Explanation"):
            nav_to("Explanation")
            
    st.markdown("---")
    st.markdown("### Length of Stay Prediction")
    X_r = prep_r.transform(inp_df)
    pred_r = rf_r.predict(X_r)[0]
    st.write(f"**Predicted LOS:** {pred_r:.1f} days")
    if 'los_days' in latest and pd.notnull(latest['los_days']):
        st.write(f"**Actual LOS:** {latest['los_days']} days")
        
    st.markdown("---")
    with st.expander("Model Performance"):
        st.write("**Classification Models (Test Set)**")
        st.write(f"**Random Forest Classifier:** Accuracy: {metrics_c['rf']['acc']:.3f} | F1: {metrics_c['rf']['f1']:.3f} | ROC-AUC: {metrics_c['rf']['auc']:.3f}")
        st.write(f"**Logistic Regression:** Accuracy: {metrics_c['lr']['acc']:.3f} | F1: {metrics_c['lr']['f1']:.3f} | ROC-AUC: {metrics_c['lr']['auc']:.3f}")
        
        st.write("**Regression Models (Test Set)**")
        st.write(f"**Random Forest Regressor:** MAE: {metrics_r['rf']['mae']:.3f} | RMSE: {metrics_r['rf']['rmse']:.3f} | R²: {metrics_r['rf']['r2']:.3f}")
        st.write(f"**Linear Regression:** MAE: {metrics_r['lin']['mae']:.3f} | RMSE: {metrics_r['lin']['rmse']:.3f} | R²: {metrics_r['lin']['r2']:.3f}")
        st.info("Random Forest generally achieved a better performance profile on the current test set.")
        
    with st.expander("Global Model Insights"):
        st.write("Top features influencing high-cost classification across the test dataset:")
        glob_ordered = sorted(zip(feat_names, global_imp), key=lambda x: x[1], reverse=True)
        for i, (fn, imp) in enumerate(glob_ordered[:10]):
            st.write(f"{i+1}. {fn.split('__')[-1].replace('_',' ').title()} (Importance: {imp:.4f})")
            
    btn_back()

def render_explanation(data):
    make_breadcrumb(["Patient Analysis", "Patient Overview", "Predictive Analytics", "Prediction Explanation"])
    st.title("Prediction Explanation")
    pdata = get_patient_data(data)
    latest = pdata.iloc[0].copy()
    
    thresh, prep_c, rf_c, lr_c, feat_names, num_cols, cat_cols, metrics_c = get_class_model(data)
    
    row = dict(latest)
    if 'admit_date' in row and pd.notnull(row['admit_date']):
        row['admission_year'] = pd.to_datetime(row['admit_date']).year
        row['admission_month'] = pd.to_datetime(row['admit_date']).month
    else:
        row['admission_year'] = 2026
        row['admission_month'] = 1
        
    inp_df = pd.DataFrame([row])
    X_c = prep_c.transform(inp_df)
    pred_c = rf_c.predict(X_c)[0]
    prob_c = rf_c.predict_proba(X_c)[0][1] * 100
    
    lbl = "HIGH COST" if pred_c == 1 else "NORMAL COST"
    st.markdown(f"**Prediction:** {lbl}")
    st.markdown(f"**Probability:** {prob_c:.1f}%")
    st.markdown(f"**Model Used:** Random Forest Classifier")
    
    st.markdown("### Model Feature Contribution")
    
    X_c_dense = X_c.toarray() if hasattr(X_c, "toarray") else X_c
    global_imp = rf_c.feature_importances_
    local_contrib = (global_imp * X_c_dense[0])
    
    contribs = list(zip(feat_names, local_contrib))
    contribs.sort(key=lambda x: abs(x[1]), reverse=True)
    top_contribs = contribs[:10]
    
    max_c = max([abs(x[1]) for x in top_contribs]) if top_contribs else 1
    
    for fn, cv in top_contribs:
        clean_fn = fn.split('__')[-1].replace('_', ' ').title()
        bar_len = int(abs(cv) / max_c * 40)
        st.markdown(f"<div style='font-family:monospace; margin-bottom:5px;'>{clean_fn.ljust(25)} {'█' * bar_len}</div>", unsafe_allow_html=True)
        
    st.info("**What this means:** The model identified these variables as important contributors associated with this particular prediction. This represents the calculated model feature contribution and does not imply medical causation.")
    
    btn_back('Predictive', '🔙 Back to Predictive Analytics')

def render_patient_analysis(data):
    if 'pa_page' not in st.session_state:
        st.session_state.pa_page = "Search"
    if 'pa_pid' not in st.session_state:
        st.session_state.pa_pid = None
        
    page = st.session_state.pa_page
    
    if page == "Search": render_search(data)
    elif page == "Overview": render_overview(data)
    elif page == "Clinical": render_clinical(data)
    elif page == "Admission": render_admission(data)
    elif page == "Diagnosis": render_diagnosis(data)
    elif page == "Financial": render_financial(data)
    elif page == "Hospital": render_hospital(data)
    elif page == "Predictive": render_predictive(data)
    elif page == "Explanation": render_explanation(data)
