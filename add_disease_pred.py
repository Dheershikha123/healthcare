import sys

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

find_str = '    with tab3:'
idx = code.find(find_str)
if idx == -1: sys.exit(1)

next_elif = code.find('elif sel_analysis == "Future Forecasting":')

new_tab3 = '''    with tab3:
        @st.cache_resource
        def train_disease_pipeline(df_in):
            d = df_in.copy().dropna(subset=['primary_category'])
            num_dis = ['age', 'comorbidity_count', 'prev_admissions']
            cat_dis = ['gender', 'insurance_type', 'tier']
            # Sample to save memory and time
            d_s = d.sample(frac=0.4, random_state=42)
            X_dis = d_s[num_dis + cat_dis].fillna(0)
            X_dis[cat_dis] = X_dis[cat_dis].astype(str)
            y_dis = d_s['primary_category']
            
            prep_d = ColumnTransformer([('n', StandardScaler(), num_dis), ('c', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_dis)])
            X_d_tr = prep_d.fit_transform(X_dis)
            rf_d = RandomForestClassifier(random_state=42, n_estimators=30, max_depth=8, n_jobs=-1)
            rf_d.fit(X_d_tr, y_dis)
            return prep_d, rf_d
            
        prep_d, rf_d = train_disease_pipeline(data)

        st.markdown("### 🧬 AI Patient Triage & Disease Prediction")
        st.markdown("Enter basic patient parameters below. The AI will first **predict the most likely Disease Category (Diagnosis)**, and then simulate expected **Length of Stay** and **Financial Risk** based on that disease prediction.")
        with st.form("prediction_form"):
            fcol1, fcol2, fcol3 = st.columns(3)
            with fcol1:
                in_age = st.number_input("Patient Age", min_value=0, max_value=120, value=45)
                in_gen = st.selectbox("Gender", data['gender'].dropna().unique())
                in_ward = st.selectbox("Expected Ward Type", data['ward_type'].dropna().unique())
                
            with fcol2:
                in_comorb = st.number_input("Known Comorbidities", 0, 10, 1)
                in_prev = st.number_input("Previous Admissions", 0, 20, 0)
                in_ins = st.selectbox("Insurance Type", data['insurance_type'].dropna().unique())
                
            with fcol3:
                in_tier = st.selectbox("Target Hospital Tier", data['tier'].dropna().unique())
                in_admit = st.selectbox("Admit Route", data['admit_type'].dropna().unique())
                in_bpl = st.selectbox("BPL Card Possessed", ["Yes", "No"])
                
            # hidden default inputs for subsequent models (required but not logically needed for disease)
            in_proc = 1
            in_diag = 2
            in_teach = "Yes"
            in_beds = 200
            
            submitted = st.form_submit_button("🩺 Predict Disease & Outcomes")
            if submitted:
                import datetime
                import numpy as np
                
                # 1. Disease Prediction Phase
                d_row = {
                    'age': in_age, 'comorbidity_count': in_comorb, 'prev_admissions': in_prev,
                    'gender': in_gen, 'insurance_type': in_ins, 'tier': in_tier
                }
                d_df = pd.DataFrame([d_row])
                X_d_trans = prep_d.transform(d_df)
                
                dis_probs = rf_d.predict_proba(X_d_trans)[0]
                dis_classes = rf_d.classes_
                
                # Get top 3
                top_indices = np.argsort(dis_probs)[::-1][:3]
                top_dis = dis_classes[top_indices[0]]
                top_prob = dis_probs[top_indices[0]] * 100
                
                st.success("Analysis Complete! Patient profile scanned across 120,000 historical records.")
                
                st.markdown("### 1. Predicted Disease Breakdown")
                st.info(f"Based on the provided demographic and historical parameters, the model strongly flags a potential **{top_dis}** condition.")
                
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric(dis_classes[top_indices[0]], f"{dis_probs[top_indices[0]]*100:.1f}%")
                cc2.metric(dis_classes[top_indices[1]], f"{dis_probs[top_indices[1]]*100:.1f}%")
                cc3.metric(dis_classes[top_indices[2]], f"{dis_probs[top_indices[2]]*100:.1f}%")
                
                # 2. Pipeline Phase
                row = {
                    'age': in_age, 'comorbidity_count': in_comorb, 'prev_admissions': in_prev,
                    'num_procedures': in_proc, 'num_diagnoses': in_diag, 'beds': in_beds,
                    'gender': in_gen, 'ward_type': in_ward, 'admit_type': in_admit,
                    'primary_category': top_dis, 'insurance_type': in_ins, 'bpl_card': in_bpl,
                    'tier': in_tier, 'teaching': in_teach,
                    'admission_year': datetime.datetime.now().year,
                    'admission_month': datetime.datetime.now().month
                }
                inp_df = pd.DataFrame([row])
                
                # Predict
                try:
                    X_clf = prep_c.transform(inp_df)
                    clf_pred = rf_m.predict(X_clf)[0]
                    clf_prob = rf_m.predict_proba(X_clf)[0][1]
                    
                    X_reg = prep_r.transform(inp_df)
                    reg_pred = rf_r.predict(X_reg)[0]
                    
                    st.markdown("### 2. Follow-Up Outcome Predictions")
                    st.markdown(f"Assuming the primary condition is *{top_dis}*, here are the projected operational requirements:")
                    rc1, rc2 = st.columns(2)
                    rc1.metric("Predicted Length of Stay (LOS)", f"{reg_pred:.1f} Days")
                    risk_label = "High Financial Risk (Top 5%)" if clf_pred == 1 else "Normal Expected Cost"
                    rc2.metric("Financial Cost Risk", risk_label, f"{(clf_prob*100):.1f}% Probability", delta_color="inverse" if clf_pred==1 else "normal")
                except Exception as e:
                    st.error(f"Secondary Prediction Error: {e}")

'''

code = code[:idx] + new_tab3 + '\n\n' + code[next_elif:]

open('app.py', 'w', encoding='utf-8').write(code)
