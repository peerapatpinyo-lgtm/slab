import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# 1. Page Configuration and Theme
st.set_page_config(page_title="SlabMaster Pro - Advanced RC Slab Designer", layout="wide")
st.title("🦅 SlabMaster Pro (Ultimate Industrial Edition)")
st.caption("Advanced Reinforced Concrete Slab Analysis, Design, BOM, and Reporting based on ACI 318")

# 2. ACI Method 3 Coefficients Function (Separated Dead / Live Loads)
def get_aci_method3_coeffs(case, m_ratio):
    # Table structure: { case: { m: (Cx_neg, Cx_pos_dl, Cx_pos_ll, Cy_neg, Cy_pos_dl, Cy_pos_ll) } }
    aci_table_m3 = {
        1: { # Case 1: Isolated (Unrestrained all edges)
            1.0: (0.000, 0.036, 0.036, 0.000, 0.036, 0.036),
            0.9: (0.000, 0.040, 0.044, 0.000, 0.031, 0.030),
            0.8: (0.000, 0.045, 0.053, 0.000, 0.025, 0.023),
            0.7: (0.000, 0.050, 0.064, 0.000, 0.020, 0.016),
            0.6: (0.000, 0.056, 0.075, 0.000, 0.014, 0.010),
            0.5: (0.000, 0.061, 0.086, 0.000, 0.009, 0.006)
        },
        2: { # Case 2: Interior Panel (Continuous all edges)
            1.0: (0.033, 0.015, 0.018, 0.033, 0.015, 0.018),
            0.9: (0.040, 0.017, 0.021, 0.027, 0.012, 0.014),
            0.8: (0.048, 0.019, 0.025, 0.022, 0.009, 0.011),
            0.7: (0.056, 0.022, 0.030, 0.016, 0.007, 0.008),
            0.6: (0.064, 0.024, 0.035, 0.011, 0.005, 0.005),
            0.5: (0.072, 0.026, 0.041, 0.007, 0.003, 0.003)
        }
    }
    selected_case = aci_table_m3.get(case, aci_table_m3[2])
    ratios = sorted(selected_case.keys())
    
    if m_ratio >= ratios[-1]: return selected_case[ratios[-1]]
    if m_ratio <= ratios[0]: return selected_case[ratios[0]]
    
    # Linear Interpolation Engine
    for i in range(len(ratios) - 1):
        r1, r2 = ratios[i], ratios[i+1]
        if r1 <= m_ratio <= r2:
            v1, v2 = selected_case[r1], selected_case[r2]
            return tuple(v1[j] + (v2[j] - v1[j]) * (m_ratio - r1) / (r2 - r1) for j in range(6))
    return selected_case[1.0]

# 3. Sidebar Input Layout
st.sidebar.header("📐 Geometry Parameters")
Lx = st.sidebar.number_input("Short Span Lx (m)", min_value=1.0, max_value=12.0, value=4.0, step=0.1)
Ly = st.sidebar.number_input("Long Span Ly (m)", min_value=1.0, max_value=24.0, value=5.0, step=0.1)
t_cm = st.sidebar.slider("Slab Thickness t (cm)", min_value=8.0, max_value=35.0, value=15.0, step=0.5)
covering_cm = st.sidebar.slider("Clear Cover (cm)", min_value=1.5, max_value=5.0, value=2.0, step=0.5)

st.sidebar.header("🛠️ Material Properties")
method = st.sidebar.selectbox("Design Method", ["Strength Design Method (SDM / USD)", "Working Stress Design (WSD)"])
fc_prime = st.sidebar.number_input("Concrete Compressive Strength fc' (kg/cm²)", min_value=140, max_value=450, value=280)
fy = st.sidebar.selectbox("Rebar Yield Strength fy (kg/cm²)", [2400, 3000, 4000], index=2)

st.sidebar.header("⚖️ Design Loads")
SDL = st.sidebar.number_input("Superimposed Dead Load SDL (kg/m²)", min_value=0, max_value=500, value=120)
LL = st.sidebar.number_input("Live Load LL (kg/m²)", min_value=0, max_value=1500, value=300)

st.sidebar.header("💰 Cost Estimation Parameters")
unit_concrete_cost = st.sidebar.number_input("Concrete Price (per m³)", value=2200)
unit_steel_cost = st.sidebar.number_input("Steel Price (per kg)", value=28)

# --- Core Engineering Computation ---
m_ratio = Lx / Ly if Ly > 0 else 0
is_one_way = m_ratio < 0.5
slab_type_str = "One-Way Slab" if is_one_way else "Two-Way Slab"

t = t_cm / 100
w_dl_self = t * 2400
w_dl_total = w_dl_self + SDL

# Bending Moment Calculation
if is_one_way:
    if method == "Strength Design Method (SDM / USD)":
        w_u = (1.2 * w_dl_total) + (1.6 * LL)
    else:
        w_u = w_dl_total + LL
    M_x_pos = (w_u * (Lx ** 2)) / 11
    M_x_neg = (w_u * (Lx ** 2)) / 10
    M_y_pos = M_y_neg = 0.0
    V_u = (w_u * Lx) / 2
else:
    # Use Case 2 (Interior Panel) as default example
    case_select = 2 
    cx_n, cx_p_dl, cx_p_ll, cy_n, cy_p_dl, cy_p_ll = get_aci_method3_coeffs(case_select, m_ratio)
    
    if method == "Strength Design Method (SDM / USD)":
        M_x_pos = (1.2 * cx_p_dl * w_dl_total + 1.6 * cx_p_ll * LL) * (Lx ** 2)
        M_x_neg = (1.2 * cx_n * w_dl_total + 1.6 * cx_n * LL) * (Lx ** 2)
        M_y_pos = (1.2 * cy_p_dl * w_dl_total + 1.6 * cy_p_ll * LL) * (Lx ** 2)
        M_y_neg = (1.2 * cy_n * w_dl_total + 1.6 * cy_n * LL) * (Lx ** 2)
        w_u = (1.2 * w_dl_total) + (1.6 * LL)
    else:
        M_x_pos = (cx_p_dl * w_dl_total + cx_p_ll * LL) * (Lx ** 2)
        M_x_neg = cx_n * (w_dl_total + LL) * (Lx ** 2)
        M_y_pos = (cy_p_dl * w_dl_total + cy_p_ll * LL) * (Lx ** 2)
        M_y_neg = cy_n * (w_dl_total + LL) * (Lx ** 2)
        w_u = w_dl_total + LL
    V_u = (w_u * Lx) / 3

# Minimum Thickness Check for Deflection Control (ACI Code)
if is_one_way:
    t_min_req = (Lx / 24) * (0.4 + fy/7000) * 100 # Assuming one end continuous
else:
    t_min_req = (2 * (Lx + Ly) / 180) * 100 # Assuming standard continuous edges
deflection_passed = t_cm >= t_min_req

# Rebar Selection and Area Calculation
main_bar = st.selectbox("Select Main Rebar Size (mm):", [9, 12, 16], index=1, key="main_bar_select")
ab = (math.pi / 4) * ((main_bar / 10) ** 2)
d = t_cm - covering_cm - (main_bar / 20)

as_min_ratio = 0.0018 if fy >= 4000 else 0.0020
As_min = as_min_ratio * 100 * t_cm

def design_as(M, d_eff, fc, fy_g, mth):
    if M <= 0: return 0.0
    M_cm = M * 100
    if mth == "Strength Design Method (SDM / USD)":
        Rn = M_cm / (0.90 * 100 * (d_eff ** 2))
        inside = 1.0 - (2.0 * Rn) / (0.85 * fc)
        if inside < 0: return -1.0
        return (0.85 * fc / fy_g) * (1.0 - math.sqrt(inside)) * 100 * d_eff
    else:
        return M_cm / (1500 * 0.88 * d_eff)

As_xb_req = max(design_as(M_x_pos, d, fc_prime, fy, method), As_min)
As_xt_req = max(design_as(M_x_neg, d, fc_prime, fy, method), As_min)
As_yb_req = max(design_as(M_y_pos, d, fc_prime, fy, method), As_min) if not is_one_way else As_min
As_yt_req = max(design_as(M_y_neg, d, fc_prime, fy, method), As_min) if (not is_one_way and M_y_neg > 0) else 0.0

# Manual Spacing Override for Site Control
st.markdown("### 🛠️ Manual Rebar Spacing Override (@ cm)")
col_ui1, col_ui2, col_ui3, col_ui4 = st.columns(4)
with col_ui1: s_xb = st.number_input("Bottom Rebar X-Axis (@ cm)", value=15.0, step=1.0)
with col_ui2: s_xt = st.number_input("Top Rebar X-Axis (@ cm)", value=15.0, step=1.0)
with col_ui3: s_yb = st.number_input("Bottom Rebar Y-Axis (@ cm)", value=20.0, step=1.0)
with col_ui4: s_yt = st.number_input("Top Rebar Y-Axis (@ cm)", value=20.0, step=1.0)

# Provided Rebar Area Calculation
As_xb_prov = (ab / s_xb) * 100
As_xt_prov = (ab / s_xt) * 100
As_yb_prov = (ab / s_yb) * 100
As_yt_prov = (ab / s_yt) * 100 if s_yt > 0 else 0.0

# Bill of Materials (BOM) & Cost Calculation Engine
weight_per_meter = (math.pi / 4) * ((main_bar / 1000) ** 2) * 7850 # Rebar weight per meter (kg/m)
total_area = Lx * Ly
concrete_volume = total_area * t

# Approximate steel length per sqm including bends and development length
steel_length_x = (100 / s_xb * Lx) + (100 / s_xt * Lx * 0.5) 
steel_length_y = (100 / s_yb * Ly) + (100 / s_yt * Ly * 0.5 if s_yt > 0 else 0)
total_steel_weight = (steel_length_x * Ly + steel_length_y * Lx) * weight_per_meter

cost_concrete = concrete_volume * unit_concrete_cost
cost_steel = total_steel_weight * unit_steel_cost
total_cost = cost_concrete + cost_steel

# --- UI Dashboard Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Engineering Verification", "🎨 Structural Detailing", "💰 Bill of Materials (BOM)", "📑 Official Calculation Report"])

with tab1:
    st.subheader("🚧 Structural Safety & Verification Results")
    
    val_thickness = "🟢 Passed (Deflection Control)" if deflection_passed else f"⚠️ Warning: Long-term deflection risk (ACI recommends min. {t_min_req:.1f} cm)"
    val_xb = "🟢 Passed" if As_xb_prov >= As_xb_req else "🔴 Insufficient reinforcement"
    val_xt = "🟢 Passed" if As_xt_prov >= As_xt_req else "🔴 Insufficient reinforcement"
    
    summary_df = pd.DataFrame({
        "Verification Parameter": ["Deflection Thickness Limit", "Bottom Rebar (X-Axis)", "Top Rebar (X-Axis)"],
        "Required by Code": [f"≥ {t_min_req:.1f} cm", f"{As_xb_req:.2f} cm²/m", f"{As_xt_req:.2f} cm²/m"],
        "Provided (Actual)": [f"{t_cm:.1f} cm", f"{As_xb_prov:.2f} cm²/m", f"{As_xt_prov:.2f} cm²/m"],
        "Status": [val_thickness, val_xb, val_xt]
    })
    st.table(summary_df)

with tab2:
    st.subheader("📐 Formwork and Rebar Detailing Sketch")
    
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.add_patch(plt.Rectangle((10, 0), 80, t_cm, facecolor='#f1f2f6', edgecolor='#2f3542', linewidth=2, hatch='.'))
    # Supporting Beams
    ax.add_patch(plt.Rectangle((0, -12), 10, t_cm+12, facecolor='#ced6e0', edgecolor='#57606f'))
    ax.add_patch(plt.Rectangle((90, -12), 10, t_cm+12, facecolor='#ced6e0', edgecolor='#57606f'))
    
    # Rebar Lines
    ax.plot([2, 98], [covering_cm, covering_cm], color='#ff4757', linewidth=2.5, label='Main Bottom Rebar')
    ax.plot([0, 25], [t_cm-covering_cm, t_cm-covering_cm], color='#1e90ff', linewidth=2.5, label='Top Support Rebar')
    ax.plot([75, 100], [t_cm-covering_cm, t_cm-covering_cm], color='#1e90ff', linewidth=2.5)
    
    ax.text(35, t_cm/2, f"DB{main_bar} @ {s_xb:.0f} cm", color='#ff4757', weight='bold')
    ax.set_xlim(-5, 105)
    ax.set_ylim(-15, t_cm + 10)
    ax.axis('off')
    st.pyplot(fig)

with tab3:
    st.subheader("📊 Bill of Quantities (BOQ) Summary")
    
    bom_df = pd.DataFrame({
        "Material Item": ["Structural Concrete (Volume)", "Main Reinforcement (Total Weight)", "Total Estimated Material Cost"],
        "Calculated Quantity": [f"{concrete_volume:.2f} m³", f"{total_steel_weight:.1f} kg", f"{total_cost:,.2f} THB"],
        "Remarks": ["Based on geometric volume", f"Includes avg. development length for DB{main_bar}", "Excludes labor and site waste allowance"]
    })
    st.table(bom_df)

with tab4:
    st.subheader("📄 Official Calculation Report for Submission")
    
    official_txt = f"""======================================================================
               STRUCTURAL DESIGN & VERIFICATION REPORT (ACI 318)
======================================================================
Structural Distribution Type: {slab_type_str}
Bending Moment Analysis Method: ACI Method 3 (Separated Load Proportions)
----------------------------------------------------------------------
[1] Geometric Properties & Slab Diagnostics:
- Slab Dimensions: Short Span Lx = {Lx:.2f} m | Long Span Ly = {Ly:.2f} m
- Aspect Ratio (m) = {m_ratio:.2f} -> Behavior: {slab_type_str}
- Provided Thickness: {t_cm:.1f} cm
- ACI Minimum Thickness (Deflection Control): {t_min_req:.1f} cm
- Long-term Deflection Status: {"[PASSED - Deflection thickness limits met]" if deflection_passed else "[WARNING - Increase thickness to prevent excessive deflection]"}

[2] Design Loads & Combinations:
- Total Dead Load (Self-weight + SDL): {w_dl_total:.2f} kg/m²
- Live Load (LL): {LL:.2f} kg/m²
- Ultimate Factored Load (w_u): {w_u:.2f} kg/m²
- Max Ultimate Positive Moment (Mx Positive): {M_x_pos:.2f} kg-m
- Max Ultimate Negative Moment (Mx Negative): {M_x_neg:.2f} kg-m

[3] Reinforcement Calculation & Verification:
- Design Strip Width: 1.00 m
- Main Bottom Rebar (Short Span X): DB{main_bar} @ {s_xb:.1f} cm [Provided: {As_xb_prov:.2f} / Required: {As_xb_req:.2f} cm²/m] -> {"PASSED" if As_xb_prov >= As_xb_req else "FAILED"}
- Top Support Rebar (Short Span X) : DB{main_bar} @ {s_xt:.1f} cm [Provided: {As_xt_prov:.2f} / Required: {As_xt_req:.2f} cm²/m] -> {"PASSED" if As_xt_prov >= As_xt_req else "FAILED"}

[4] Bill of Materials (BOM) Estimate:
- Net Concrete Volume: {concrete_volume:.2f} m³
- Total Reinforcement Weight: {total_steel_weight:.1f} kg
======================================================================
"""
    st.code(official_txt, language="text")
    st.download_button(label="📥 Download Calculation Report & BOQ (.txt)", data=official_txt, file_name="Ultimate_Slab_Report.txt", mime="text/plain")
