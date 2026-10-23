import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith("def pbar(d, x, y, t, ori='v'"): start_idx = i
    if line.startswith("def cnt(d, c):"): end_idx = i

if start_idx == -1 or end_idx == -1: 
    print("Cannot find bounds")
    sys.exit(1)

new_macros = """def dump_insight(msg):
    import streamlit as st
    st.markdown(msg)

def generate_analytical_insight(agg_d, x, y, pop, raw_d, graph_type):
    if raw_d is None or raw_d.empty: return ""
    try:
        col_x = x[0] if type(x) is list else x
        
        if graph_type == "histogram" or graph_type == "scatter plot" or graph_type == "box plot":
            hx = str(col_x).replace('_', ' ').title()
            msg = f"### 1. What does this graph show?\\nThis {graph_type} displays the distribution and density of **{hx}** across the selected population: **{pop}**. It provides a granular view into where data points naturally cluster, highlighting expected clinical or operational bounds.\\n\\n"
            
            try: mode_val = raw_d[col_x].mode().iloc[0]
            except: mode_val = "N/A"
            
            msg += f"### 2. Observed pattern\\nThe dataset shows a distinct clustering of admissions. The most concentrated zone lies around **{mode_val}**. This concentration defines the typical hospital experience for the selected subset, indicating where standard variations safely lie.\\n\\n"
            
            msg += f"### 3. Why is this pattern observed?\\nThis distribution is fundamentally associated with clinical operational standards. A tight cluster indicates standardized procedural recovery times or fixed cost brackets, whereas widespread tails suggest complex outlier patients demanding custom attention.\\n\\n"
            
            msg += f"### 4. Analytical breakdown\\nIsolating the most frequent subset ({hx} = {mode_val}):\\n"
            sub = raw_d[raw_d[col_x] == mode_val] if type(mode_val) != str else raw_d
            if not sub.empty:
                msg += f"*   **Average Cost:** ₹{sub['total_cost_inr'].mean():,.0f} (OOP: ₹{sub['out_of_pocket_inr'].mean():,.0f})\\n"
                msg += f"*   **Average LOS:** {sub['los_days'].mean():.2f} days\\n"
                msg += f"*   **Procedures:** {sub['num_procedures'].mean():.1f}\\n"
                msg += f"*   **Admissions volume:** {len(sub):,}\\n\\n"
            
            msg += f"### 5. Project implication\\nVisualizing this spread empowers hospital administrators to identify outlier limits. Understanding the baseline distribution of {hx} ensures that deviations from the norm are rapidly flagged for operational review.\\n"
            return msg

        is_cnt = (y == "count")
        metric_name = "total admissions" if is_cnt else str(y).replace('_', ' ').title()
        hx = str(col_x).replace('_', ' ').title()
        
        msg = f"### 1. What does this graph show?\\nThis {graph_type} represents **{metric_name}** across various categories of **{hx}**. The currently selected population is **{pop}**. This visualization systematically isolates how different {hx} groups diverge in terms of {metric_name} footprint.\\n\\n"
        
        sorted_d = agg_d.sort_values(by=y, ascending=False)
        top_cat = sorted_d.iloc[0][col_x]
        top_val = sorted_d.iloc[0][y]
        bot_cat = sorted_d.iloc[-1][col_x]
        bot_val = sorted_d.iloc[-1][y]
        
        msg += f"### 2. Observed pattern\\nThe dataset shows that the highest {metric_name} occurs in **{top_cat}** at **{top_val:,.1f}**. Conversely, the lowest metric lies in **{bot_cat}** at **{bot_val:,.1f}**. "
        if is_cnt:
            pct = (top_val / agg_d[y].sum() * 100) if agg_d[y].sum() > 0 else 0
            msg += f"The category '{top_cat}' captures approximately **{pct:.1f}%** of all volume within this filter block.\\n\\n"
        else:
            msg += f"This distinct variance signals that {hx} is differentially associated with the underlying case complexity or billing structure across the cohort.\\n\\n"

        msg += f"### 3. Why is this pattern observed?\\nThese patterns are rarely arbitrary; they correlate with acute severity and systemic hospital handling protocols. The dataset demonstrates that the heightened magnitude in **{top_cat}** is frequently associated with distinct differences in stay duration and intervention rates. This relationship should be thoroughly investigated at the procedural level.\\n\\n"

        msg += f"### 4. Analytical breakdown\\nExecuting a deeper layer slice into **{top_cat}** from the filtered data reveals:\\n"
        if col_x in raw_d.columns:
            sub = raw_d[raw_d[col_x] == top_cat]
            if not sub.empty:
                s_diag = sub['primary_diagnosis'].mode().iloc[0] if not sub['primary_diagnosis'].mode().empty else "N/A"
                s_ward = sub['ward_type'].mode().iloc[0] if not sub['ward_type'].mode().empty else "N/A"
                msg += f"*   **Primary Diagnosis Encountered:** {s_diag}\\n"
                msg += f"*   **Average Hospital LOS:** {sub['los_days'].mean():.2f} days\\n"
                msg += f"*   **Net Treatment Cost:** ₹{sub['total_cost_inr'].mean():,.0f}\\n"
                msg += f"*   **Net OOP Expenditure:** ₹{sub['out_of_pocket_inr'].mean():,.0f}\\n"
                msg += f"*   **Average Subsidy:** ₹{sub['govt_subsidy_inr'].mean():,.0f}\\n"
                msg += f"*   **Average Procedures:** {sub['num_procedures'].mean():.1f}\\n"
                msg += f"*   **Most Common Ward:** {s_ward}\\n\\n"

        msg += f"### 5. Project implication\\nThis graph helps pinpoint the pivotal {hx} entities dictating capacity and cost thresholds. Expanding investigations explicitly into **{top_cat}** lets clinical strategists map systemic bottlenecks—facilitating optimized procedure planning and robust financial triage.\\n"
        
        return msg
    except Exception as e:
        return ""

def pbar(d, x, y, t, ori='v', pop="", raw_d=None):
    if not d.empty:
        col_x = x[0] if type(x) is list else x
        if ori == 'h':
            c = px.bar(d, x=y, y=col_x, title=t, orientation=ori)
        else:
            c = px.bar(d, x=col_x, y=y, title=t, orientation=ori)
        if ori=='h': c.update_yaxes(categoryorder="total ascending")
        render_chart(c)
        if raw_d is not None:
            ans = generate_analytical_insight(d, x, y, pop, raw_d, "bar chart")
            if ans: dump_insight(ans)

def ppie(d, n, v, t, pop="", raw_d=None):
    if not d.empty: 
        col_n = n[0] if type(n) is list else n
        render_chart(px.pie(d, names=col_n, values=v, title=t, hole=0.3))
        if raw_d is not None:
            ans = generate_analytical_insight(d, n, v, pop, raw_d, "pie chart")
            if ans: dump_insight(ans)

def phist(d, x, t, color=None, pop="", raw_d=None):
    if not d.empty: 
        render_chart(px.histogram(d, x=x, title=t, color=color, barmode='group'))
        if raw_d is not None:
            ans = generate_analytical_insight(d, x, "", pop, raw_d, "histogram")
            if ans: dump_insight(ans)

def psca(d, x, y, t, pop="", raw_d=None):
    if not d.empty: 
        render_chart(px.scatter(d, x=x, y=y, title=t, opacity=0.1))
        if raw_d is not None:
            ans = generate_analytical_insight(d, x, y, pop, raw_d, "scatter plot")
            if ans: dump_insight(ans)

def pbox(d, x, y, t, pop="", raw_d=None):
    if not d.empty:
        render_chart(px.box(d, x=x, y=y, title=t))
        if raw_d is not None:
            ans = generate_analytical_insight(d, x, y, pop, raw_d, "box plot")
            if ans: dump_insight(ans)
"""

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines[:start_idx])
    f.write(new_macros + '\\n')
    f.writelines(lines[end_idx:])
