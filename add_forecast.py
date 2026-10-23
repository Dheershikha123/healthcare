import sys

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update the Select Analysis dropdown to include Future Forecasting
old_analyses_str = 'analyses = ["Overview", "Clinical Analysis", "Demographic Analysis", "Financial Analysis", "Hospital Analysis", "Admission Analysis", "Outcome Analysis", "Predictive Analytics", "Key Insights & Findings"]'
new_analyses_str = 'analyses = ["Overview", "Clinical Analysis", "Demographic Analysis", "Financial Analysis", "Hospital Analysis", "Admission Analysis", "Outcome Analysis", "Predictive Analytics", "Future Forecasting", "Key Insights & Findings"]'

if old_analyses_str not in code:
    print("Cannot find analyses list to update.")
    sys.exit(1)
code = code.replace(old_analyses_str, new_analyses_str)

# 2. Add forecasting sidebar controls
old_outcome = '''elif sel_analysis == "Outcome Analysis":
    sel_cat = st.sidebar.selectbox("Select Category", ["Recovered", "LAMA", "Referred", "Expired", "All Outcomes"])
    c_out = single_filter("Filter by Outcome", "discharge_type", df)
    df = df if c_out == "All" else df[df["discharge_type"]==c_out]
    bc_arr = [opt for opt in [c_out] if opt != "All"]
    bread += f" ➔ {sel_cat}" + (" ➔ " + " ➔ ".join(bc_arr) if len(bc_arr)>0 else "")
    pop_context = bc_arr[-1] if len(bc_arr)>0 else f"Outcome ({sel_cat})"
'''

new_outcome = old_outcome + '''
elif sel_analysis == "Future Forecasting":
    st.sidebar.markdown("### ⏲️ FORECAST PARAMETERS")
    target_year = st.sidebar.slider("Target Prediction Year", 2025, 2030, 2026)
    sel_cat = "Trend Projection"
    
    c_dis = single_filter("Filter Disease Category", "primary_category", data)
    c_hosp = single_filter("Filter by Hospital", "name", data)
    c_sta = single_filter("Filter by State", "hospital_state", data)
    bread = f"Future Forecasting ➔ Projections up to {target_year}"
'''
code = code.replace(old_outcome, new_outcome)

# 3. Add forecasting main page routing
old_insights = 'elif sel_analysis == "Key Insights & Findings":'

new_forecasting = '''elif sel_analysis == "Future Forecasting":
    st.title(f"🔮 Future Disease & Capacity Forecasting (Up to {target_year})")
    
    st.markdown(f"<div style='background-color:#E3F2FD; padding:10px; border-radius:6px; color:#1565C0; font-weight:600; margin-bottom: 20px;'>{bread}</div>", unsafe_allow_html=True)
    st.info(f"Model predicting future trends based on historical patterns (2015-2024).")
    
    # Filter on the overarching data, ignoring the main UI year filter (since we need all years for trend)
    f_df = data.copy()
    if 'c_dis' in locals() and c_dis != "All": f_df = f_df[f_df["primary_category"] == c_dis]
    if 'c_hosp' in locals() and c_hosp != "All": f_df = f_df[f_df["name"] == c_hosp]
    if 'c_sta' in locals() and c_sta != "All": f_df = f_df[f_df["hospital_state"] == c_sta]
    
    yearly_counts = f_df.groupby('year').size().reset_index(name='count')
    
    if len(yearly_counts) < 3:
        st.warning("Not enough historical data points to perform a reliable automated forecast for this slice.")
    else:
        from sklearn.linear_model import LinearRegression
        import numpy as np
        
        X = yearly_counts[['year']].values
        y = yearly_counts['count'].values
        model = LinearRegression()
        model.fit(X, y)
        
        future_years = np.arange(2025, target_year + 1).reshape(-1, 1)
        preds = np.maximum(0, np.round(model.predict(future_years)))
        
        hist_plot = yearly_counts.copy()
        hist_plot['Timeline'] = 'Historical (Actual)'
        
        import pandas as pd
        fut_plot = pd.DataFrame({'year': future_years.flatten(), 'count': preds, 'Timeline': f'Predicted'})
        
        plot_df = pd.concat([hist_plot, fut_plot], ignore_index=True)
        
        # KPIs
        exp_adm = int(preds[-1]) if len(preds) > 0 else 0
        base_adm = int(y[-1]) if len(y) > 0 else 0
        growth = ((exp_adm - base_adm) / base_adm * 100) if base_adm > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Projected Admissions ({target_year})", f"{exp_adm:,}")
        c2.metric(f"Current Baseline Volume", f"{base_adm:,}")
        c3.metric(f"Expected Growth Delta", f"{growth:+.1f}%")
        
        # Plot
        fig = px.line(plot_df, x='year', y='count', color='Timeline', markers=True, 
                      title=f"Volume Forecast over Time — {c_dis if 'c_dis' in locals() and c_dis != 'All' else 'All Diseases'}")
        fig.update_traces(line=dict(dash="dot"), selector=dict(name='Predicted'))
        render_chart(fig)
        
        st.markdown("### 🗺️ Expected Geographical & Facility Burden")
        st.markdown(f"Assuming hospital distributions remain highly correlated with current baselines, here is the expected location strain for **{target_year}**:")
        
        fac_dist = f_df['name'].value_counts(normalize=True).reset_index()
        fac_dist.columns = ['Hospital', 'Proportion']
        fac_dist['Expected Patients'] = np.round(fac_dist['Proportion'] * exp_adm)
        
        ch1, ch2 = st.columns(2)
        with ch1:
            render_chart(px.bar(fac_dist.head(10), x='Expected Patients', y='Hospital', orientation='h', 
                            title=f"Top 10 Burdened Hospitals in {target_year}").update_yaxes(categoryorder="total ascending"))
        
        state_dist = f_df['hospital_state'].value_counts(normalize=True).reset_index()
        state_dist.columns = ['State', 'Proportion']
        state_dist['Expected Patients'] = np.round(state_dist['Proportion'] * exp_adm)
        with ch2:
            render_chart(px.pie(state_dist.head(8), names='State', values='Expected Patients', hole=0.3, 
                            title=f"Projected State-Level Hotspots ({target_year})"))
                            
        st.markdown(f"""
#### 🤖 Analyst Breakdown for {target_year}
- **What this predicts:** If the historical trends for **{c_dis if 'c_dis' in locals() and c_dis != 'All' else 'All Diseases'}** remain consistent, overall volume is modeled to reach **{exp_adm:,}** admissions by {target_year}.
- **Where they will be:** The heaviest pressure is modeled to fall upon **{fac_dist['Hospital'].iloc[0] if len(fac_dist)>0 else 'N/A'}**. State-wise, **{state_dist['State'].iloc[0] if len(state_dist)>0 else 'N/A'}** projects the most significant concentration of inbound patients.
- **Project Implication:** Administration and supply-chains should allocate preventative resources, funding, and critical care capacity heavily towards these primary forecasted nodes ahead of time.
""")

'''

code = code.replace(old_insights, new_forecasting + old_insights)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
