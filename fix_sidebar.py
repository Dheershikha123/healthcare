import sys

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

search_router_start = 'if "current_page" not in st.session_state:'
search_chart_render = 'def render_chart(fig):'

idx_start = code.find(search_router_start)
idx_end = code.find(search_chart_render)

print(f"sidebar boundaries: {idx_start} to {idx_end}")
if idx_start == -1 or idx_end == -1: sys.exit(1)

new_sidebar = """st.sidebar.markdown("### 🎛️ ANALYSIS CONTROLS")
years = ["All Years"] + sorted(data["year"].dropna().unique().tolist())
sel_year = st.sidebar.selectbox("Select Year", years)

analyses = ["Overview", "Clinical Analysis", "Demographic Analysis", "Financial Analysis", "Hospital Analysis", "Admission Analysis", "Outcome Analysis", "Predictive Analytics", "Key Insights & Findings"]
sel_analysis = st.sidebar.selectbox("Select Analysis", analyses)

ydf = data if sel_year == "All Years" else data[data["year"] == sel_year]
df = ydf

st.sidebar.markdown("### 🔍 DEEP FILTERS")
def single_filter(label, col, curr):
    opts = ["All"] + sorted(curr[col].dropna().astype(str).unique().tolist())
    return st.sidebar.selectbox(label, opts)

bread = f"{sel_year} ➔ {sel_analysis}"
sel_cat = ""
pop_context = "Selected Cohort"

if sel_analysis == "Clinical Analysis":
    sel_cat = st.sidebar.selectbox("Select Category", ["Ward Type", "Admission Type", "Diagnosis Category", "Specific Diagnosis", "Length of Stay", "Procedures", "Clinical Outcome"])
    c_ward = single_filter("Filter by Ward", "ward_type", df)
    df = df if c_ward == "All" else df[df["ward_type"]==c_ward]
    c_cat2 = single_filter("Filter by Diagnosis Category", "primary_category", df)
    df = df if c_cat2 == "All" else df[df["primary_category"]==c_cat2]
    c_diag = single_filter("Filter by Specific Diagnosis", "primary_diagnosis", df)
    df = df if c_diag == "All" else df[df["primary_diagnosis"]==c_diag]
    bc_arr = [opt for opt in [c_ward, c_cat2, c_diag] if opt != "All"]
    bread += f" ➔ {sel_cat}" + (" ➔ " + " ➔ ".join(bc_arr) if len(bc_arr)>0 else "")
    pop_context = bc_arr[-1] if len(bc_arr)>0 else f"Clinical ({sel_cat})"

elif sel_analysis == "Demographic Analysis":
    sel_cat = st.sidebar.selectbox("Select Category", ["Gender", "Age Group", "Patient State", "BPL Status", "Insurance Type"])
    c_gen = single_filter("Filter by Gender", "gender", df)
    df = df if c_gen == "All" else df[df["gender"]==c_gen]
    c_age = single_filter("Filter by Age Group", "age_group", df)
    df = df if c_age == "All" else df[df["age_group"]==c_age]
    c_bpl = single_filter("Filter by BPL Status", "bpl_card", df)
    df = df if c_bpl == "All" else df[df["bpl_card"]==c_bpl]
    bc_arr = [opt for opt in [c_gen, c_age, c_bpl] if opt != "All"]
    bread += f" ➔ {sel_cat}" + (" ➔ " + " ➔ ".join(bc_arr) if len(bc_arr)>0 else "")
    pop_context = bc_arr[-1] if len(bc_arr)>0 else f"Demographic ({sel_cat})"

elif sel_analysis == "Financial Analysis":
    sel_cat = st.sidebar.selectbox("Select Category", ["Insurance Type", "BPL Status", "Cost Category", "Total Treatment Cost", "Government Subsidy", "Out-of-Pocket Cost"])
    c_ins = single_filter("Filter by Insurance", "insurance_type", df)
    if c_ins == "Unknown": st.sidebar.warning("Note: Unknown represents missing insurance information natively.")
    df = df if c_ins == "All" else df[df["insurance_type"]==c_ins]
    c_bpl = single_filter("Filter by BPL Status", "bpl_card", df)
    df = df if c_bpl == "All" else df[df["bpl_card"]==c_bpl]
    bc_arr = [opt for opt in [c_ins, c_bpl] if opt != "All"]
    bread += f" ➔ {sel_cat}" + (" ➔ " + " ➔ ".join(bc_arr) if len(bc_arr)>0 else "")
    pop_context = bc_arr[-1] if len(bc_arr)>0 else f"Financial ({sel_cat})"

elif sel_analysis == "Hospital Analysis":
    sel_cat = st.sidebar.selectbox("Select Category", ["Hospital Tier", "Hospital", "Hospital State", "Teaching Status", "Ward"])
    c_tier = single_filter("Filter by Tier", "tier", df)
    df = df if c_tier == "All" else df[df["tier"]==c_tier]
    c_hp = single_filter("Filter by Hospital", "name", df)
    df = df if c_hp == "All" else df[df["name"]==c_hp]
    c_ward = single_filter("Filter by Ward", "ward_type", df)
    df = df if c_ward == "All" else df[df["ward_type"]==c_ward]
    bc_arr = [opt for opt in [c_tier, c_hp, c_ward] if opt != "All"]
    bread += f" ➔ {sel_cat}" + (" ➔ " + " ➔ ".join(bc_arr) if len(bc_arr)>0 else "")
    pop_context = bc_arr[-1] if len(bc_arr)>0 else f"Hospital ({sel_cat})"

elif sel_analysis == "Admission Analysis":
    sel_cat = st.sidebar.selectbox("Select Category", ["Emergency", "Elective", "OPD", "Admission Trend"])
    c_adm = single_filter("Filter by Admit Route", "admit_type", df)
    df = df if c_adm == "All" else df[df["admit_type"]==c_adm]
    bc_arr = [opt for opt in [c_adm] if opt != "All"]
    bread += f" ➔ {sel_cat}" + (" ➔ " + " ➔ ".join(bc_arr) if len(bc_arr)>0 else "")
    pop_context = bc_arr[-1] if len(bc_arr)>0 else f"Admission ({sel_cat})"

elif sel_analysis == "Outcome Analysis":
    sel_cat = st.sidebar.selectbox("Select Category", ["Recovered", "LAMA", "Referred", "Expired", "All Outcomes"])
    c_out = single_filter("Filter by Outcome", "discharge_type", df)
    df = df if c_out == "All" else df[df["discharge_type"]==c_out]
    bc_arr = [opt for opt in [c_out] if opt != "All"]
    bread += f" ➔ {sel_cat}" + (" ➔ " + " ➔ ".join(bc_arr) if len(bc_arr)>0 else "")
    pop_context = bc_arr[-1] if len(bc_arr)>0 else f"Outcome ({sel_cat})"

"""

code = code[:idx_start] + new_sidebar + code[idx_end:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
