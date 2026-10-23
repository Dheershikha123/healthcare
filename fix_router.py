import sys

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()


search_dash = 'if st.session_state.current_page == "dashboard":'
search_pred = 'elif st.session_state.current_page == "predictive":'

idx_dash = code.find(search_dash)
idx_pred = code.find(search_pred)

if idx_dash == -1 or idx_pred == -1:
    print("Cannot find router marks")
    print(idx_dash, idx_pred)
    sys.exit(1)

new_dash = """if sel_analysis == "Overview":
    st.title(f"🏥 {'Healthcare Overview' if sel_year == 'All Years' else f'{sel_year} Healthcare Overview'}")
    if sel_year != "All Years": st.markdown(f"*Based on selected year: {sel_year}*")
    
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Admissions", f"{len(df):,}")
    k2.metric("Unique Patients", f"{df['patient_id'].nunique():,}" if not df.empty else "0")
    k3.metric("Average LOS", f"{df['los_days'].mean():.2f}" if not df.empty else "0")
    k4.metric("Average Age", f"{df['age'].mean():.1f}" if not df.empty else "0")
    
    k5,k6,k7,k8 = st.columns(4)
    k5.metric("Average Total Cost", f"₹{df['total_cost_inr'].mean():,.0f}" if not df.empty else "0")
    k6.metric("Average OOP", f"₹{df['out_of_pocket_inr'].mean():,.0f}" if not df.empty else "0")
    k7.metric("Average Subsidy", f"₹{df['govt_subsidy_inr'].mean():,.0f}" if not df.empty else "0")
    
    if not df.empty:
        thresh = df['total_cost_inr'].quantile(0.95)
        hc = len(df[df['total_cost_inr']>=thresh])
    else: hc = 0
    k8.metric("High-Cost Admissions", f"{hc:,}")
    st.markdown("---")
    
    if sel_year == "All Years":
        st.subheader("📈 Year-wise Trend")
        r1, r2, r3 = st.columns(3)
        with r1: render_chart(px.line(cnt(df,['year']).sort_values('year'), x='year', y='count', title="Admissions by Year", markers=True))
        with r2: render_chart(px.line(avg(df,'year','total_cost_inr').sort_values('year'), x='year', y='total_cost_inr', title="Average Cost by Year", markers=True))
        with r3: render_chart(px.line(avg(df,'year','los_days').sort_values('year'), x='year', y='los_days', title="Average LOS by Year", markers=True))
    else:
        st.subheader(f"📊 Detailed Analysis — {sel_year}")
        r1, r2 = st.columns(2)
        with r1: ppie(cnt(df,['admit_type']), ["admit_type"], "count", "Admission Type Distribution", pop="Overview Population", raw_d=df)
        with r2: phist(df, "ward_type", "Ward Distribution", pop="Overview Population", raw_d=df)
        r3, r4 = st.columns(2)
        with r3: pbar(cnt(df,['primary_category']).head(10), ["primary_category"], "count", "Top Diagnosis Categories", 'h', pop="Overview Population", raw_d=df)
        with r4: pbar(avg(df,"ward_type","total_cost_inr"), "ward_type", "total_cost_inr", "Average Cost by Ward", pop="Overview Population", raw_d=df)

elif sel_analysis not in ["Predictive Analytics", "Key Insights & Findings"]:
    st.markdown(f"<div style='background-color:#E3F2FD; padding:10px; border-radius:6px; color:#1565C0; font-weight:600; margin-bottom: 20px;'>{bread}</div>", unsafe_allow_html=True)
    st.markdown(f"### {sel_year if sel_year != 'All Years' else 'All Years'} {sel_analysis} — {sel_cat}")
    drilldown_content(df, pop_name=f"{pop_context} ({sel_year})")

"""

code = code[:idx_dash] + new_dash + code[idx_pred:]

code = code.replace('elif st.session_state.current_page == "predictive":', 'elif sel_analysis == "Predictive Analytics":')
code = code.replace('elif st.session_state.current_page == "insights":', 'elif sel_analysis == "Key Insights & Findings":')

def rm_back(match): return ""
import re
code = re.sub(r'^\s*def back\(\):.*?st\.markdown\("---\"\)\n', '', code, flags=re.MULTILINE|re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
