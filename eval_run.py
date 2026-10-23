import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve, mean_absolute_error, mean_squared_error, r2_score

data = pd.read_csv("data/cleaned/master_patient_health.csv")
data['admit_date'] = pd.to_datetime(data['admit_date'])
data['age_group'] = pd.cut(data['age'], bins=[-1,18,40,60,80,150], labels=['0–18','19–40','41–60','61–80','81+'], right=True)

df_in = data.copy()
thresh = df_in['total_cost_inr'].quantile(0.95)
df_in['high_cost'] = (df_in['total_cost_inr'] > thresh).astype(int)

num_cols = ['age', 'comorbidity_count', 'prev_admissions', 'num_procedures', 'num_diagnoses', 'beds']
cat_cols = ['gender', 'ward_type', 'admit_type', 'primary_category', 'insurance_type', 'bpl_card', 'tier', 'teaching']

X = df_in[num_cols + cat_cols].fillna(0)
X[cat_cols] = X[cat_cols].astype(str)
y = df_in['high_cost']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
print(f"High-cost threshold: {thresh}")
print(f"High-cost admissions: {y.sum()}")
print(f"Normal-cost admissions: {len(y) - y.sum()}")

prep = ColumnTransformer([
    ('num', StandardScaler(), num_cols),
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)
])

X_tr = prep.fit_transform(X_train)
X_te = prep.transform(X_test)

lr = LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000)
rf = RandomForestClassifier(class_weight="balanced", random_state=42, n_estimators=50, max_depth=10, n_jobs=-1)

lr.fit(X_tr, y_train)
rf.fit(X_tr, y_train)

preds_lr = lr.predict(X_te)
prob_lr = lr.predict_proba(X_te)[:,1]
preds_rf = rf.predict(X_te)
prob_rf = rf.predict_proba(X_te)[:,1]

def g_met(yt, yp, yp_prob):
    return [accuracy_score(yt, yp), precision_score(yt, yp, zero_division=0), 
            recall_score(yt, yp, zero_division=0), f1_score(yt, yp, zero_division=0), 
            roc_auc_score(yt, yp_prob)]

m_lr = g_met(y_test, preds_lr, prob_lr)
m_rf = g_met(y_test, preds_rf, prob_rf)

print("\n### Classification — Test Set")
print("Logistic Regression:")
print(f"Accuracy: {m_lr[0]:.4f}")
print(f"Precision: {m_lr[1]:.4f}")
print(f"Recall: {m_lr[2]:.4f}")
print(f"F1 Score: {m_lr[3]:.4f}")
print(f"ROC-AUC: {m_lr[4]:.4f}")

print("\nRandom Forest Classifier:")
print(f"Accuracy: {m_rf[0]:.4f}")
print(f"Precision: {m_rf[1]:.4f}")
print(f"Recall: {m_rf[2]:.4f}")
print(f"F1 Score: {m_rf[3]:.4f}")
print(f"ROC-AUC: {m_rf[4]:.4f}")


df_reg = data.copy()
df_reg = df_reg.dropna(subset=['los_days'])

df_reg['admission_year'] = df_reg['admit_date'].dt.year
df_reg['admission_month'] = df_reg['admit_date'].dt.month

num_cols_reg = ['age', 'comorbidity_count', 'prev_admissions', 'num_procedures', 'num_diagnoses', 'beds', 'admission_year', 'admission_month']
cat_cols_reg = ['gender', 'ward_type', 'admit_type', 'primary_category', 'insurance_type', 'bpl_card', 'tier', 'teaching']

X_r = df_reg[num_cols_reg + cat_cols_reg].fillna(0)
X_r[cat_cols_reg] = X_r[cat_cols_reg].astype(str)
y_r = df_reg['los_days']

Xr_train, Xr_test, yr_train, yr_test = train_test_split(X_r, y_r, test_size=0.2, random_state=42)

prepr = ColumnTransformer([
    ('num', StandardScaler(), num_cols_reg),
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols_reg)
])

Xr_tr = prepr.fit_transform(Xr_train)
Xr_te = prepr.transform(Xr_test)

linreg = LinearRegression()
rfreg = RandomForestRegressor(random_state=42, n_estimators=50, max_depth=10, n_jobs=-1)

linreg.fit(Xr_tr, yr_train)
rfreg.fit(Xr_tr, yr_train)

preds_lin = linreg.predict(Xr_te)
preds_rfreg = rfreg.predict(Xr_te)

def g_reg_met(yt, yp):
    return [mean_absolute_error(yt, yp), np.sqrt(mean_squared_error(yt, yp)), r2_score(yt, yp)]

mr_lin = g_reg_met(yr_test, preds_lin)
mr_rf = g_reg_met(yr_test, preds_rfreg)

print("\n### Regression — Test Set")
print("Linear Regression:")
print(f"MAE: {mr_lin[0]:.4f}")
print(f"RMSE: {mr_lin[1]:.4f}")
print(f"R²: {mr_lin[2]:.4f}")

print("\nRandom Forest Regressor:")
print(f"MAE: {mr_rf[0]:.4f}")
print(f"RMSE: {mr_rf[1]:.4f}")
print(f"R²: {mr_rf[2]:.4f}")
