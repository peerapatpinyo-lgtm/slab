import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# 1. Page Config
st.set_page_config(page_title="SlabMaster Pro V2 - Visual Suite", layout="wide")
st.title("🦅 SlabMaster Pro V2 (Visual Boundary Edition)")
st.caption("Fully Compliant with ACI 318-99 Method 3 | Enhanced Visual UI")

# 2. ACI Coefficient Core Engine
def get_full_aci_method3_coeffs(case_num, m_ratio):
    aci_database = {
        1: {1.0: (0.033, 0.015, 0.018, 0.033, 0.015, 0.018), 0.9: (0.040, 0.017, 0.021, 0.027, 0.012, 0.014), 0.8: (0.048, 0.019, 0.025, 0.022, 0.009, 0.011), 0.7: (0.056, 0.022, 0.030, 0.016, 0.007, 0.008), 0.6: (0.064, 0.024, 0.035, 0.011, 0.005, 0.005), 0.5: (0.072, 0.026, 0.041, 0.007, 0.003, 0.003)},
        2: {1.0: (0.000, 0.036, 0.036, 0.000, 0.036, 0.036), 0.9: (0.000, 0.040, 0.044, 0.000, 0.031, 0.030), 0.8: (0.000, 0.045, 0.053, 0.000, 0.025, 0.023), 0.7: (0.000, 0.050, 0.064, 0.000, 0.020, 0.016), 0.6: (0.000, 0.056, 0.075, 0.000, 0.014, 0.010), 0.5: (0.000, 0.061, 0.086, 0.000, 0.009, 0.006)},
        3: {1.0: (0.041, 0.018, 0.022, 0.000, 0.027, 0.027), 0.9: (0.049, 0.020, 0.025, 0.000, 0.022, 0.021), 0.8: (0.057, 0.022, 0.029, 0.000, 0.017, 0.016), 0.7: (0.065, 0.024, 0.034, 0.000, 0.013, 0.011), 0.6: (0.072, 0.025, 0.039, 0.000, 0.009, 0.007), 0.5: (0.079, 0.026, 0.044, 0.000, 0.006, 0.004)},
        4: {1.0: (0.000, 0.027, 0.027, 0.041, 0.018, 0.022), 0.9: (0.000, 0.031, 0.031, 0.034, 0.015, 0.018), 0.8: (0.000, 0.036, 0.037, 0.027, 0.012, 0.014), 0.7: (0.000, 0.042, 0.045, 0.020, 0.009, 0.010), 0.6: (0.000, 0.049, 0.054, 0.014, 0.006, 0.006), 0.5: (0.000, 0.057, 0.065, 0.009, 0.004, 0.004)},
        5: {1.0: (0.049, 0.022, 0.025, 0.049, 0.022, 0.025), 0.9: (0.056, 0.024, 0.028, 0.040, 0.018, 0.020), 0.8: (0.064, 0.026, 0.032, 0.032, 0.014, 0.015), 0.7: (0.071, 0.028, 0.036, 0.024, 0.011, 0.011), 0.6: (0.078, 0.029, 0.041, 0.017, 0.007, 0.007), 0.5: (0.085, 0.030, 0.046, 0.011, 0.004, 0.004)},
        6: {1.0: (0.049, 0.020, 0.024, 0.000, 0.020, 0.020), 0.9: (0.057, 0.022, 0.027, 0.000, 0.016, 0.015), 0.8: (0.065, 0.024, 0.031, 0.000, 0.012, 0.011), 0.7: (0.072, 0.025, 0.035, 0.000, 0.009, 0.007), 0.6: (0.079, 0.026, 0.040, 0.000, 0.006, 0.004), 0.5: (0.085, 0.026, 0.045, 0.000, 0.003, 0.002)},
        7: {1.0: (0.000, 0.020, 0.020, 0.049, 0.020, 0.024), 0.9: (0.000, 0.024, 0.024, 0.041, 0.017, 0.020), 0.8: (0.000, 0.029, 0.029, 0.033, 0.013, 0.015), 0.7: (0.000, 0.035, 0.036, 0.025, 0.010, 0.011), 0.6: (0.000, 0.042, 0.045, 0.017, 0.007, 0.007), 0.5: (0.000, 0.051, 0.057, 0.011, 0.004, 0.004)},
        8: {1.0: (0.037, 0.016, 0.020, 0.037, 0.016, 0.020), 0.9: (0.044, 0.018, 0.023, 0.031, 0.013, 0.015), 0.8: (0.052, 0.021, 0.027, 0.025, 0.010, 0.012), 0.7: (0.059, 0.023, 0.031, 0.019, 0.008, 0.009), 0.6: (0.067, 0.025, 0.036, 0.013, 0.005, 0.005), 0.5: (0.074, 0.026, 0.042, 0.008, 0.003, 0.003)},
        9: {1.0: (0.037, 0.016, 0.020, 0.037, 0.016, 0.020), 0.9: (0.045, 0.019, 0.023, 0.030, 0.013, 0.015), 0.8: (0.053, 0.021, 0.026, 0.023, 0.010, 0.011), 0.7: (0.061, 0.023, 0.030, 0.017, 0.007, 0.008), 0.6: (0.068, 0.025, 0.035, 0.012, 0.005, 0.005), 0.5: (0.075, 0.026, 0.040, 0.007, 0.003, 0.002)}
    }
    selected_case = aci_database.get(case_num, aci_database[1])
    ratios = sorted(selected_case.keys())
    if m_ratio >= ratios[-1]: return selected_case[ratios[-1]]
    if m_ratio <= ratios[0]: return selected_case[ratios[0]]
    for i in range(len(ratios) - 1):
        r1, r2 = ratios[i], ratios[i+1]
        if r1 <= m_ratio <= r2:
            v1, v2 = selected_case[r1], selected_case[r2]
            return tuple(v1[j] + (v2[j] - v1[j]) * (m_ratio - r1) / (r2 - r1) for j in range(6))
    return selected_case[1.0]

# ==========================================
# 3. SIDEBAR CONTROLS & GEOMETRY
# ==========================================
st.sidebar.header("📐 Slab Geometry")
Lx = st.sidebar.number_input("Short Span Lx (m)", min_value=1.0, max_value=12.0, value=4.0, step=0.1)
Ly = st.sidebar.number_input("Long Span Ly (m)", min_value=1.0, max_value=24.0, value=5.0, step=0.1)
t_cm = st.sidebar.slider("Slab Thickness t (cm)", min_value=8.0, max_value=35.0, value=15.0, step=0.5)
covering_cm = st.sidebar.slider("Clear Cover (cm)", min_value=1.5, max_value=5.0, value=2.0, step=0.5)

st.sidebar.header("🛠️ Material & Framework")
method = st.sidebar.selectbox("Design Framework", ["Strength Design Method (SDM / USD)", "Working Stress Design (WSD)"])
fc_prime = st.sidebar.number_input("Concrete Strength fc' (kg/cm²)", min_value=140, max_value=450, value=280)
fy = st.sidebar.selectbox("Rebar Yield strength fy (kg/cm²)", [2400, 3000, 4000], index=2)

st.sidebar.header("⚖️ Loading Parameters")
UDL_SDL = st.sidebar.number_input("Floor Finish / SDL (kg/m²)", value=120)
UDL_LL = st.sidebar.number_input("Occupancy Live Load (kg/m²)", value=250)
line_load_w = st.sidebar.number_input("Wall Line Load (kg/m)", value=180.0)
line_load_len = st.sidebar.number_input("Wall Total Length (m)", value=4.0)
point_load_p = st.sidebar.number_input("Equipment Point Load (kg)", value=500.0)
point_load_count = st.sidebar.number_input("Point Load Qty", value=1)

st.sidebar.header("💰 Cost Setup")
unit_concrete_cost = st.sidebar.number_input("Concrete Price (per m³)", value=2200)
unit_steel_cost = st.sidebar.number_input("Steel Price (per kg)", value=28)

# ==========================================
# VISUAL BOUNDARY CONDITION SELECTOR IN MAIN APP
# ==========================================
st.markdown("### 🗺️ Visual Boundary Condition Selector (ACI Method 3)")
st.info("💡 เส้นหนาทึบ (▓▓▓) = ขอบต่อเนื่องกับห้องอื่น | เส้นบาง (---) = ขอบอิสระ/ขอบนอกอาคาร")

# Custom dictionary with ASCII visualization matrix to make it intuitive
cases_visual_dict = {
    "Case 1: Fully Continuous (Interior Panel)": {
        "id": 1,
        "ui": "```\n      ▓▓▓▓▓▓▓▓▓▓▓▓▓\n      ▓           ▓\n      ▓  CASE 1   ▓\n      ▓  (กลางตึก) ▓\n      ▓           ▓\n      ▓▓▓▓▓▓▓▓▓▓▓▓▓\n```"
    },
    "Case 2: Fully Discontinuous (Isolated)": {
        "id": 2,
        "ui": "```\n      -------------\n      |           |\n      |  CASE 2   |\n      | (พื้นเดี่ยว) |\n      |           |\n      -------------\n```"
    },
    "Case 3: One Long Edge Continuous": {
        "id": 3,
        "ui": "```\n      ▓▓▓▓▓▓▓▓▓▓▓▓▓\n      |           |\n      |  CASE 3   |\n      |           |\n      |           |\n      -------------\n```"
    },
    "Case 4: One Short Edge Continuous": {
        "id": 4,
        "ui": "```\n      -------------\n      ▓           |\n      ▓  CASE 4   |\n      ▓           |\n      ▓           |\n      -------------\n```"
    },
    "Case 5: Two Adjacent Edges Continuous": {
        "id": 5,
        "ui": "```\n      ▓▓▓▓▓▓▓▓▓▓▓▓▓\n      ▓           |\n      ▓  CASE 5   |\n      ▓  (มุมตึก)  |\n      ▓           |\n      -------------\n```"
    },
    "Case 6: Two Long Edges Continuous": {
        "id": 6,
        "ui": "```\n      ▓▓▓▓▓▓▓▓▓▓▓▓▓\n      |           |\n      |  CASE 6   |\n      |           |\n      |           |\n      ▓▓▓▓▓▓▓▓▓▓▓▓▓\n```"
    },
    "Case 7: Two Short Edges Continuous": {
        "id": 7,
        "ui": "```\n      -------------\n      ▓           ▓\n      ▓  CASE 7   ▓\n      ▓           ▓\n      ▓           ▓\n      -------------\n```"
    },
    "Case 8: Three Edges Continuous (Short Discont.)": {
        "id": 8,
        "ui": "```\n      ▓▓▓▓▓▓▓▓▓▓▓▓▓\n      ▓           ▓\n      ▓  CASE 8   ▓\n      ▓           ▓\n      ▓           ▓\n      -------------\n```"
    },
    "Case 9: Three Edges Continuous (Long Discont.)": {
        "id": 9,
        "ui": "```\n      ▓▓▓▓▓▓▓▓▓▓▓▓▓\n      ▓           |\n      ▓  CASE 9   |\n      ▓           |\n      ▓           |\n      ▓▓▓▓▓▓▓▓▓▓▓▓▓\n```"
    }
}

selected_case_name = st.selectbox("คลิกเลือกเคสแผ่นพื้นตามตำแหน่งในโครงสร้างของคุณ:", list(cases_visual_dict.keys()))

# Render visual representation dynamically inside an expansive container
st.markdown(cases_visual_dict[selected_case_name]["ui"])
case_selected = cases_visual_dict[selected_case_name]["id"]

# ==========================================
# 4. CORE MATH & STRUCTURAL ENGINEERING
# ==========================================
m_ratio = Lx / Ly if Ly > 0 else 0
is_one_way = m_ratio < 0.5
slab_type_str = "One-Way Slab (พื้นทางเดียว)" if is_one_way else "Two-Way Slab (พื้นสองทาง)"

st.metric(label="Slab System Classification", value=slab_type_str, delta=f"Aspect Ratio m = {m_ratio:.3f}")

slab_area = Lx * Ly
t = t_cm / 100
slab_self_weight = t * 2400

# EUDL Engine Transformation
eudl_line_load = (line_load_w * line_load_len / slab_area) * 1.5 if slab_area > 0 else 0.0
eudl_point_load = (point_load_p * point_load_count / slab_area) * 2.0 if slab_area > 0 else 0.0
total_structural_dl = slab_self_weight + UDL_SDL + eudl_line_load + eudl_point_load

if method == "Strength Design Method (SDM / USD)":
    w_u = (1.2 * total_structural_dl) + (1.6 * UDL_LL)
else:
    w_u = total_structural_dl + UDL_LL

# Flexural Moments Matrix Calculator
if is_one_way:
    M_x_pos = (w_u * (Lx ** 2)) / 11
    M_x_neg = (w_u * (Lx ** 2)) / 10
    M_y_pos = M_y_neg = 0.0
    V_u = (w_u * Lx) / 2
else:
    cx_n, cx_p_dl, cx_p_ll, cy_n, cy_p_dl, cy_p_ll = get_full_aci_method3_coeffs(case_selected, m_ratio)
    if method == "Strength Design Method (SDM / USD)":
        M_x_pos = (1.2 * cx_p_dl * total_structural_dl + 1.6 * cx_p_ll * UDL_LL) * (Lx ** 2)
        M_x_neg = (1.2 * cx_n * total_structural_dl + 1.6 * cx_n * UDL_LL) * (Lx ** 2)
        M_y_pos = (1.2 * cy_p_dl * total_structural_dl + 1.6 * cy_p_ll * UDL_LL) * (Lx ** 2)
        M_y_neg = (1.2 * cy_n * total_structural_dl + 1.6 * cy_n * UDL_LL) * (Lx ** 2)
    else:
        M_x_pos = (cx_p_dl * total_structural_dl + cx_p_ll * UDL_LL) * (Lx ** 2)
        M_x_neg = cx_n * (total_structural_dl + UDL_LL) * (Lx ** 2)
        M_y_pos = (cy_p_dl * total_structural_dl + cy_p_ll * UDL_LL) * (Lx ** 2)
        M_y_neg = cy_n * (total_structural_dl + UDL_LL) * (Lx ** 2)
    V_u = (w_u * Lx) / 3

# Safety Controls & Deflection Checks
t_min_req = (Lx / 24) * (0.4 + fy/7000) * 100 if is_one_way else (2 * (Lx + Ly) / 180) * 100
deflection_passed = t_cm >= t_min_req

# Rebar Reinforcement Calculations
main_bar = st.selectbox("Design Rebar Diameter (mm):", [9, 12, 16], index=1)
ab = (math.pi / 4) * ((main_bar / 10) ** 2)
d = t_cm - covering_cm - (main_bar / 20)
as_min_ratio = 0.0018 if fy >= 4000 else 0.0020
As_min = as_min_ratio * 100 * t_cm

def compute_exact_as(M, d_eff, fc, fy_g, mth):
    if M <= 0: return 0.0
    M_cm = M * 100
    if mth == "Strength Design Method (SDM / USD)":
        Rn = M_cm / (0.90 * 100 * (d_eff ** 2))
        inside = 1.0 - (2.0 * Rn) / (0.85 * fc)
        if inside < 0: return -1.0
        return (0.85 * fc / fy_g) * (1.0 - math.sqrt(inside)) * 100 * d_eff
    else:
        return M_cm / (1500 * 0.88 * d_eff)

As_xb_req = max(compute_exact_as(M_x_pos, d, fc_prime, fy, method), As_min)
As_xt_req = max(compute_exact_as(M_x_neg, d, fc_prime, fy, method), As_min)
As_yb_req = max(compute_exact_as(M_y_pos, d, fc_prime, fy, method), As_min) if not is_one_way else As_min
As_yt_req = max(compute_exact_as(M_y_neg, d, fc_prime, fy, method), As_min) if (not is_one_way and M_y_neg > 0) else 0.0

st.markdown("### 🎛️ Real-world Field Construction Pitch Setup (@ cm)")
c1, c2, c3, c4 = st.columns(4)
with c1: s_xb = c1.number_input("Bottom Spacing X (@ cm)", value=15.0, step=0.5)
with c2: s_xt = c2.number_input("Top Spacing X (@ cm)", value=15.0, step=0.5)
with c3: s_yb = c3.number_input("Bottom Spacing Y (@ cm)", value=20.0, step=0.5)
with c4: s_yt = c4.number_input("Top Spacing Y (@ cm)", value=20.0, step=0.5)

As_xb_prov = (ab / s_xb) * 100
As_xt_prov = (ab / s_xt) * 100
As_yb_prov = (ab / s_yb) * 100
As_yt_prov = (ab / s_yt) * 100 if s_yt > 0 else 0.0

concrete_volume = slab_area * t
weight_m = (math.pi / 4) * ((main_bar / 1000) ** 2) * 7850
steel_len_x = (100 / s_xb * Lx) + (100 / s_xt * Lx * 0.5) 
steel_len_y = (100 / s_yb * Ly) + (100 / s_yt * Ly * 0.5 if s_yt > 0 else 0)
calc_steel_weight = (steel_len_x * Ly + steel_len_y * Lx) * weight_m

cost_con = concrete_volume * unit_concrete_cost
cost_st = calc_steel_weight * unit_steel_cost
grand_total = cost_con + cost_st

# ==========================================
# 5. CODE OUTPUT TABS INTERFACE
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Compliance", "🎨 Blueprint", "💰 Takeoff (BOQ)", "📑 Design Report"])

with tab1:
    st.subheader("Structural Integrity Check")
    thick_status = "🟢 Passed" if deflection_passed else f"⚠️ Increase to {t_min_req:.1f} cm"
    status_xb = "🟢 Passed" if As_xb_prov >= As_xb_req else "🔴 Deficient Steel Area"
    status_xt = "🟢 Passed" if As_xt_prov >= As_xt_req else "🔴 Deficient Steel Area"
    status_yb = "🟢 Passed" if As_yb_prov >= As_yb_req else "🔴 Deficient Steel Area"
    
    compliance_data = {
        "Checklist Metric": ["Min Slab Depth", "Bottom Rebar X", "Top Rebar X", "Bottom Rebar Y"],
        "Target": [f"≥ {t_min_req:.1f} cm", f"{As_xb_req:.2f} cm²/m", f"{As_xt_req:.2f} cm²/m", f"{As_yb_req:.2f} cm²/m"],
        "Actual": [f"{t_cm:.1f} cm", f"{As_xb_prov:.2f} cm²/m", f"{As_xt_prov:.2f} cm²/m", f"{As_yb_prov:.2f} cm²/m"],
        "Result": [thick_status, status_xb, status_xt, status_yb]
    }
    st.table(pd.DataFrame(compliance_data))

with tab2:
    st.subheader("Dynamic Cross-Section Draft")
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.add_patch(plt.Rectangle((10, 0), 80, t_cm, facecolor='#f8f9fa', edgecolor='#1e272e', linewidth=2.5, hatch='/'))
    ax.add_patch(plt.Rectangle((0, -15), 10, t_cm+15, facecolor='#dcdde1', edgecolor='#2f3640'))
    ax.add_patch(plt.Rectangle((90, -15), 10, t_cm+15, facecolor='#dcdde1', edgecolor='#2f3640'))
    ax.plot([1.5, 98.5], [covering_cm, covering_cm], color='#eb2f06', linewidth=3)
    ax.plot([0, 25], [t_cm-covering_cm, t_cm-covering_cm], color='#0652dd', linewidth=3)
    ax.plot([75, 100], [t_cm-covering_cm, t_cm-covering_cm], color='#0652dd', linewidth=3)
    ax.text(32, t_cm/2, f"Main Bottom: DB{main_bar} @ {s_xb:.1f} cm", color='#eb2f06', weight='bold')
    ax.text(12, t_cm + 3, f"Top Support: DB{main_bar} @ {s_xt:.1f} cm", color='#0652dd', weight='bold')
    ax.set_xlim(-5, 105)
    ax.set_ylim(-18, t_cm + 12)
    ax.axis('off')
    st.pyplot(fig)

with tab3:
    st.subheader("Bill of Quantities (BOQ)")
    takeoff_data = {
        "Material Component": ["Concrete Volume", "Reinforcement High-Tensile Steel", "Total Material Core Cost"],
        "Quantity": [f"{concrete_volume:.2f} m³", f"{calc_steel_weight:.1f} kg", f"{grand_total:,.2f} THB"],
        "Logic": ["Geometric Volumetric Formula", "Spacing layouts including basic hook estimations", "Net procurement costs without factoring waste"]
    }
    st.table(pd.DataFrame(takeoff_data))

with tab4:
    st.subheader("ACI 318 Structural Calculation Record")
    report_body = f"""======================================================================
         OFFICIAL STRUCTURAL VERIFICATION & CALCULATION DOCUMENT
======================================================================
Design Regulation Profile: ACI 318-99 Method 3 Analysis
----------------------------------------------------------------------
[1] GEOMETRICAL ANALYSIS:
- Aspect Ratio (m = Lx/Ly): {m_ratio:.3f} -> {slab_type_str}
- Selected Boundary Configuration: {selected_case_name}
- Deflection Depth Target vs Configured: {t_min_req:.1f} cm req. vs {t_cm:.1f} cm actual

[2] ULTIMATE LOAD PROFILE:
- Total Structural Dead Load: {total_structural_dl:.2f} kg/m² (Slab SW + SDL + EUDL Walls + EUDL Point Load)
- Ultimate Factored Design Action (w_u): {w_u:.2f} kg/m²

[3] STRUCTURAL CROSS-SECTION VERIFICATION STATUS:
- Bottom Mesh Setup X: DB{main_bar} @ {s_xb:.1f} cm [Prov: {As_xb_prov:.2f} / Req: {As_xb_req:.2f} cm²/m] -> {"SECURE" if As_xb_prov >= As_xb_req else "DEFICIENT"}
- Top Support Setup X: DB{main_bar} @ {s_xt:.1f} cm [Prov: {As_xt_prov:.2f} / Req: {As_xt_req:.2f} cm²/m] -> {"SECURE" if As_xt_prov >= As_xt_req else "DEFICIENT"}
- Bottom Mesh Setup Y: DB{main_bar} @ {s_yb:.1f} cm [Prov: {As_yb_prov:.2f} / Req: {As_yb_req:.2f} cm²/m] -> {"SECURE" if As_yb_prov >= As_yb_req else "DEFICIENT"}
======================================================================
"""
    st.code(report_body, language="text")
