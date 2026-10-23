import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('elif st.session_state.current_page == "clin":')
end_idx = text.find('elif st.session_state.current_page == "predictive":')

if start_idx != -1 and end_idx != -1:
    new_code = """
def drilldown_content(d):
    st.markdown("### 📌 Selected Group Overview")
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Total Admissions", f"{len(d):,}")
    k2.metric("Unique Patients", f"{d['patient_id'].nunique():,}" if not d.empty else "0")
    k3.metric("Average LOS", f"{d['los_days'].mean():.2f}" if not d.empty else "0")
    k4.metric("Median LOS", f"{d['los_days'].median():.2f}" if not d.empty else "0")
    k5.metric("Average Total Cost", f"₹{d['total_cost_inr'].mean():,.0f}" if not d.empty else "0")
    k6,k7,k8,k9,k10 = st.columns(5)
    k6.metric("Average OOP", f"₹{d['out_of_pocket_inr'].mean():,.0f}" if not d.empty else "0")
    k7.metric("Average Subsidy", f"₹{d['govt_subsidy_inr'].mean():,.0f}" if not d.empty else "0")
    k8.metric("Avg Procedures", f"{d['num_procedures'].mean():.1f}" if not d.empty else "0")
    k9.metric("Avg Comorbidity", f"{d['comorbidity_count'].mean():.1f}" if not d.empty else "0")
    k10.metric("Avg Diagnoses", f"{d['num_diagnoses'].mean():.1f}" if not d.empty else "0")

    with st.expander("👥 Patient Profile", expanded=True):
        c1, c2 = st.columns(2)
        with c1: pbar(cnt(d, "age_group"), "age_group", "count", "Age Group Distribution")
        with c2: ppie(cnt(d, "gender"), "gender", "count", "Gender Distribution")
        c3, c4 = st.columns(2)
        with c3: ppie(cnt(d, "bpl_card"), "bpl_card", "count", "BPL Distribution")
        with c4: pbar(cnt(d, "insurance_type"), "count", "insurance_type", "Insurance Type Distribution", "h")
        c5, c6 = st.columns(2)
        with c5: phist(d, "comorbidity_count", "Comorbidity Distribution")
        with c6: phist(d, "prev_admissions", "Previous Admissions Distribution")

    with st.expander("🦠 Disease & Diagnosis Analysis"):
        c1, c2 = st.columns(2)
        with c1: pbar(cnt(d, "primary_category").head(10), "count", "primary_category", "Disease Category Distribution", "h")
        with c2: pbar(cnt(d, "primary_diagnosis").head(10), "count", "primary_diagnosis", "Top 10 Diagnoses", "h")
        c3, c4 = st.columns(2)
        with c3: phist(d, "num_diagnoses", "Diagnosis Count per Admission")
        with c4: 
            if not d.empty: render_chart(px.histogram(d, x="primary_category", color="age_group", title="Disease Category × Age Group", barmode="group"))
        c5, c6 = st.columns(2)
        with c5: 
            if not d.empty: render_chart(px.histogram(d, x="primary_category", color="gender", title="Disease Category × Gender", barmode="group"))
        with c6: 
            if not d.empty: pbar(avg(d, "primary_category", "comorbidity_count"), "primary_category", "comorbidity_count", "Average Comorbidity by Disease Category")

    with st.expander("🚑 Admission Pattern"):
        c1, c2 = st.columns(2)
        with c1: ppie(cnt(d, "admit_type"), "admit_type", "count", "Admission Type Distribution")
        with c2: 
            if not d.empty: render_chart(px.histogram(d, x="admit_type", color="primary_category", title="Admission Type × Disease Category", barmode="group"))
        c3, c4 = st.columns(2)
        with c3: pbar(avg(d, "admit_type", "los_days"), "admit_type", "los_days", "Admission Type × Average LOS")
        with c4: pbar(avg(d, "admit_type", "total_cost_inr"), "admit_type", "total_cost_inr", "Admission Type × Average Cost")

    with st.expander("🏥 Care & Resource Utilization"):
        c1, c2 = st.columns(2)
        with c1: pbar(avg(d, "ward_type", "los_days"), "ward_type", "los_days", "Ward Type × Average LOS")
        with c2: pbar(avg(d, "ward_type", "total_cost_inr"), "ward_type", "total_cost_inr", "Ward Type × Average Cost")
        c3, c4 = st.columns(2)
        with c3: psca(d, "num_procedures", "los_days", "Procedures vs LOS")
        with c4: psca(d, "num_procedures", "total_cost_inr", "Procedures vs Cost")
        c5, c6 = st.columns(2)
        with c5: psca(d, "comorbidity_count", "los_days", "Comorbidity vs LOS")
        with c6: psca(d, "los_days", "total_cost_inr", "LOS vs Total Cost")

    with st.expander("⏱ Length of Stay Analysis"):
        c1, c2 = st.columns(2)
        with c1: phist(d, "los_days", "LOS Distribution")
        with c2: pbar(avg(d, "primary_category", "los_days"), "primary_category", "los_days", "Average LOS by Disease Category")
        c3, c4 = st.columns(2)
        with c3: pbar(avg(d, "primary_diagnosis").sort_values("los_days", ascending=False).head(10) if not d.empty else pd.DataFrame(), "primary_diagnosis", "los_days", "Average LOS by Top Diagnoses")
        with c4: pbar(avg(d, "age_group", "los_days"), "age_group", "los_days", "Average LOS by Age Group")

    with st.expander("💰 Financial Analysis"):
        c1, c2 = st.columns(2)
        with c1: pbar(avg(d, "primary_category", "total_cost_inr"), "count", "primary_category", "Average Cost by Disease Category", "h")
        with c2: pbar(avg(d, "ward_type", "total_cost_inr"), "ward_type", "total_cost_inr", "Average Cost by Ward")
        c3, c4 = st.columns(2)
        with c3: pbar(avg(d, "insurance_type", "govt_subsidy_inr"), "insurance_type", "govt_subsidy_inr", "Average Subsidy by Insurance Type")
        with c4: pbar(avg(d, "primary_category", "out_of_pocket_inr"), "count", "primary_category", "Average OOP by Disease Category", "h")

    with st.expander("📋 Outcome Analysis"):
        c1, c2 = st.columns(2)
        with c1: ppie(cnt(d, "discharge_type"), "discharge_type", "count", "Discharge Type Distribution")
        with c2: 
            if not d.empty: render_chart(px.histogram(d, x="discharge_type", color="ward_type", title="Discharge Type × Ward", barmode="group"))
        c3, c4 = st.columns(2)
        with c3: pbar(avg(d, "discharge_type", "los_days"), "discharge_type", "los_days", "Discharge Type × Average LOS")
        with c4: pbar(avg(d, "discharge_type", "total_cost_inr"), "discharge_type", "total_cost_inr", "Discharge Type × Average Cost")

    with st.expander("🏨 Hospital Analysis"):
        c1, c2 = st.columns(2)
        with c1: pbar(cnt(d, "name").head(10), "count", "name", "Admissions by Hospital", "h")
        with c2: pbar(avg(d, "tier", "total_cost_inr"), "tier", "total_cost_inr", "Hospital Tier × Average Cost")

    with st.expander("💡 What the Data Shows", expanded=True):
        if not d.empty:
            st.info(f'''
            **Clinical Analysis for Selected Group:**
            - **Most Common Diagnosis:** {d["primary_diagnosis"].mode()[0] if not d["primary_diagnosis"].empty else "N/A"}
            - **Most Common Age Group:** {d["age_group"].mode()[0] if not d["age_group"].empty else "N/A"}
            - **Most Common Admission Type:** {d["admit_type"].mode()[0] if not d["admit_type"].empty else "N/A"}
            - **Average LOS:** {d["los_days"].mean():.1f} days (Median: {d["los_days"].median():.1f})
            - **Dominant Discharge Outcome:** {d["discharge_type"].mode()[0] if not d["discharge_type"].empty else "N/A"}
            - **Average Out-of-Pocket Cost:** ₹{d["out_of_pocket_inr"].mean():,.0f}
            - **Average Subsidy Provided:** ₹{d["govt_subsidy_inr"].mean():,.0f}
            - **Average Procedures performed:** {d["num_procedures"].mean():.1f}
            ''')
        else:
            st.info("No records match the current selection.")

elif st.session_state.current_page == "clin":
    st.title("🏥 Clinical Drill Down")
    back()
    c1, c2, c3 = st.columns(3)
    c_ward = c1.selectbox("Filter by Ward Type", ["All"] + list(df["ward_type"].dropna().unique()))
    c_cat = c2.selectbox("Filter by Disease Category", ["All"] + list(df[df["ward_type"] == c_ward]["primary_category"].dropna().unique() if c_ward != "All" else df["primary_category"].dropna().unique()))
    tmp_df = df
    if c_ward != "All": tmp_df = tmp_df[tmp_df["ward_type"] == c_ward]
    if c_cat != "All": tmp_df = tmp_df[tmp_df["primary_category"] == c_cat]
    c_diag = c3.selectbox("Filter by Specific Diagnosis", ["All"] + list(tmp_df["primary_diagnosis"].dropna().unique()))
    if c_diag != "All": tmp_df = tmp_df[tmp_df["primary_diagnosis"] == c_diag]
    drilldown_content(tmp_df)

elif st.session_state.current_page == "demo":
    st.title("👥 Demographics Drill Down")
    back()
    c1, c2, c3, c4 = st.columns(4)
    c_gen = c1.selectbox("Filter by Gender", ["All"] + list(df["gender"].dropna().unique()))
    tmp_df = df
    if c_gen != "All": tmp_df = tmp_df[tmp_df["gender"] == c_gen]
    c_age = c2.selectbox("Filter by Age Group", ["All"] + list(tmp_df["age_group"].dropna().unique()))
    if c_age != "All": tmp_df = tmp_df[tmp_df["age_group"] == c_age]
    c_cat = c3.selectbox("Filter by Disease Category", ["All"] + list(tmp_df["primary_category"].dropna().unique()))
    if c_cat != "All": tmp_df = tmp_df[tmp_df["primary_category"] == c_cat]
    c_diag = c4.selectbox("Filter by Specific Diagnosis", ["All"] + list(tmp_df["primary_diagnosis"].dropna().unique()))
    if c_diag != "All": tmp_df = tmp_df[tmp_df["primary_diagnosis"] == c_diag]
    drilldown_content(tmp_df)

elif st.session_state.current_page == "fin":
    st.title("💰 Financial Drill Down")
    back()
    c1, c2, c3, c4 = st.columns(4)
    c_ins = c1.selectbox("Filter by Insurance", ["All"] + list(df["insurance_type"].dropna().unique()))
    tmp_df = df
    if c_ins != "All": tmp_df = tmp_df[tmp_df["insurance_type"] == c_ins]
    c_bpl = c2.selectbox("Filter by BPL Status", ["All"] + list(tmp_df["bpl_card"].dropna().unique()))
    if c_bpl != "All": tmp_df = tmp_df[tmp_df["bpl_card"] == c_bpl]
    c_ward = c3.selectbox("Filter by Ward", ["All"] + list(tmp_df["ward_type"].dropna().unique()))
    if c_ward != "All": tmp_df = tmp_df[tmp_df["ward_type"] == c_ward]
    c_cat = c4.selectbox("Filter by Disease Category", ["All"] + list(tmp_df["primary_category"].dropna().unique()))
    if c_cat != "All": tmp_df = tmp_df[tmp_df["primary_category"] == c_cat]
    drilldown_content(tmp_df)

elif st.session_state.current_page == "hosp":
    st.title("🏨 Hospital Drill Down")
    back()
    c1, c2, c3, c4 = st.columns(4)
    c_tier = c1.selectbox("Filter by Tier", ["All"] + list(df["tier"].dropna().unique()))
    tmp_df = df
    if c_tier != "All": tmp_df = tmp_df[tmp_df["tier"] == c_tier]
    c_hp = c2.selectbox("Filter by Hospital", ["All"] + list(tmp_df["name"].dropna().unique()))
    if c_hp != "All": tmp_df = tmp_df[tmp_df["name"] == c_hp]
    c_ward = c3.selectbox("Filter by Ward", ["All"] + list(tmp_df["ward_type"].dropna().unique()))
    if c_ward != "All": tmp_df = tmp_df[tmp_df["ward_type"] == c_ward]
    c_cat = c4.selectbox("Filter by Disease Category", ["All"] + list(tmp_df["primary_category"].dropna().unique()))
    if c_cat != "All": tmp_df = tmp_df[tmp_df["primary_category"] == c_cat]
    drilldown_content(tmp_df)

elif st.session_state.current_page == "adm":
    st.title("🚑 Admission Drill Down")
    back()
    c1, c2, c3, c4 = st.columns(4)
    c_adm = c1.selectbox("Filter by Admission Type", ["All"] + list(df["admit_type"].dropna().unique()))
    tmp_df = df
    if c_adm != "All": tmp_df = tmp_df[tmp_df["admit_type"] == c_adm]
    c_ward = c2.selectbox("Filter by Ward", ["All"] + list(tmp_df["ward_type"].dropna().unique()))
    if c_ward != "All": tmp_df = tmp_df[tmp_df["ward_type"] == c_ward]
    c_cat = c3.selectbox("Filter by Disease Category", ["All"] + list(tmp_df["primary_category"].dropna().unique()))
    if c_cat != "All": tmp_df = tmp_df[tmp_df["primary_category"] == c_cat]
    c_diag = c4.selectbox("Filter by Specific Diagnosis", ["All"] + list(tmp_df["primary_diagnosis"].dropna().unique()))
    if c_diag != "All": tmp_df = tmp_df[tmp_df["primary_diagnosis"] == c_diag]
    drilldown_content(tmp_df)

elif st.session_state.current_page == "out":
    st.title("📋 Outcome Drill Down")
    back()
    c1, c2, c3, c4 = st.columns(4)
    c_out = c1.selectbox("Filter by Discharge Type", ["All"] + list(df["discharge_type"].dropna().unique()))
    tmp_df = df
    if c_out != "All": tmp_df = tmp_df[tmp_df["discharge_type"] == c_out]
    c_ward = c2.selectbox("Filter by Ward", ["All"] + list(tmp_df["ward_type"].dropna().unique()))
    if c_ward != "All": tmp_df = tmp_df[tmp_df["ward_type"] == c_ward]
    c_cat = c3.selectbox("Filter by Disease Category", ["All"] + list(tmp_df["primary_category"].dropna().unique()))
    if c_cat != "All": tmp_df = tmp_df[tmp_df["primary_category"] == c_cat]
    c_diag = c4.selectbox("Filter by Specific Diagnosis", ["All"] + list(tmp_df["primary_diagnosis"].dropna().unique()))
    if c_diag != "All": tmp_df = tmp_df[tmp_df["primary_diagnosis"] == c_diag]
    drilldown_content(tmp_df)

"""

    final_text = text[:start_idx] + new_code + text[end_idx:]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(final_text)
    print("Successfully replaced app.py sections")
else:
    print("Could not find blocks")
