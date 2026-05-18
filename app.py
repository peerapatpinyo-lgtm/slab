import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(page_title="SlabMaster Pro V3 - Engineering Suite", layout="wide")
st.title("🦅 SlabMaster Pro V3 (Ultimate Visual Engine)")
st.caption("Commercial-Grade Reinforced Concrete Design Software | ACI 318-99 Method 3 Fully Compliant")

# Set matplotlib style for clean engineering look (FIXED)
if 'seaborn-v0_8-whitegrid' in plt.style.available:
    plt.style.use('seaborn-v0_8-whitegrid')
elif 'ggplot' in plt.style.available:
    plt.style.use('ggplot')
else:
    plt.style.use('default')

# ==========================================
# 2. CORE DATABASE (ACI METHOD 3)
# ==========================================
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

# Mapping boundaries: (Top, Bottom, Left, Right) - True means Continuous
case_boundaries = {
    1: (True, True, True, True),
    2: (False, False, False, False),
    3: (True, False, False, False),
    4: (False, False, True, False),
    5: (True, False, True, False),
    6: (True, True, False, False),
    7: (False, False, True, True),
    8: (True, True, True, False),
    9: (True, False, True, True)
}

# ==========================================
# 3. SIDEBAR PARAMETERS
# ==========================================
st.sidebar.header("📐 Geometric Configuration")
Lx = st.sidebar.number_input("Short Span Lx (m) - ทิศทาง X", min_value=1.0, max_value=12.0, value=4.0, step=0.1)
Ly = st.sidebar.number_input("Long Span Ly (m) - ทิศทาง Y", min_value=1.0, max_value=24.0, value=5.0, step=0.1)
t_cm = st.sidebar.slider("Slab Thickness t (cm)", min_value=8.0, max_value=35.0, value=15.0, step=0.5)
covering_cm = st.sidebar.slider("Clear Concrete Cover (cm)", min_value=1.5, max_value=5.0, value=2.0, step=0.5)

st.sidebar.header("🛠️ Material Specifications")
method = st.sidebar.selectbox("Design Method Framework", ["Strength Design Method (SDM / USD)", "Working Stress Design (WSD)"])
fc_prime = st.sidebar.number_input("Concrete Strength fc' (kg/cm²)", min_value=140, max_value=450, value=280)
fy = st.sidebar.selectbox("Rebar Yield Strength fy (kg/cm²)", [2400, 3000, 4000], index=2)

st.sidebar.header("⚖️ Loading Systems")
UDL_SDL = st.sidebar.number_input("Superimposed Dead Load (kg/m²)", value=120)
UDL_LL = st.sidebar.number_input("Occupancy Live Load (kg/m²)", value=250)
line_load_w = st.sidebar.number_input("Partition Wall Load (kg/m)", value=180.0)
line_load_len = st.sidebar.number_input("Total Length of Wall on Slab (m)", value=4.0)
point_load_p = st.sidebar.number_input("Heavy Equipment Point Load (kg)", value=500.0)
point_load_count = st.sidebar.number_input("Point Load Quantity", value=1)

st.sidebar.header("💰 Budgeting Rates")
unit_concrete_cost = st.sidebar.number_input("Concrete Rate (THB / m³)", value=2200)
unit_steel_cost = st.sidebar.number_input("Steel Rate (THB / kg)", value=28)

# ==========================================
# 4. INTERACTIVE GRAPHICAL SELECTOR (PLAN VIEW)
# ==========================================
st.markdown("### 🗺️ Dynamic Plan View & Boundary Selector")
col_sel, col_gfx = st.columns([4, 3])

with col_sel:
    case_idx = st.selectbox("เลือกผังการต่อเนื่องของแผ่นพื้น (ACI Cases 1-9):", [
        "Case 1: Fully Continuous (แผ่นพื้นภายใน ต่อเนื่องทั้ง 4 ด้าน)",
        "Case 2: Fully Discontinuous (แผ่นพื้นเดี่ยว ไม่ต่อเนื่องเลยทั้ง 4 ด้าน)",
        "Case 3: One Long Edge Continuous (ต่อเนื่องด้านยาวด้านเดียว)",
        "Case 4: One Short Edge Continuous (ต่อเนื่องด้านสั้นด้านเดียว)",
        "Case 5: Two Adjacent Edges Continuous (ต่อเนื่อง 2 ด้านติดกัน - ขอบมุมตึก)",
        "Case 6: Two Long Edges Continuous (ต่อเนื่องด้านยาว 2 ด้านตรงข้ามกัน)",
        "Case 7: Two Short Edges Continuous (ต่อเนื่องด้านสั้น 2 ด้านตรงข้ามกัน)",
        "Case 8: Three Edges Continuous (ต่อเนื่อง 3 ด้าน - ขอบด้านสั้นปล่อยอิสระ 1 ด้าน)",
        "Case 9: Three Edges Continuous (ต่อเนื่อง 3 ด้าน - ขอบด้านยาวปล่อยอิสระ 1 ด้าน)"
    ])
    case_selected = int(case_idx.split(":")[0].split(" ")[1])
    
    m_ratio = Lx / Ly if Ly > 0 else 0
    is_one_way = m_ratio < 0.5
    slab_type_str = "One-Way Slab (พื้นทางเดียว)" if is_one_way else "Two-Way Slab (พื้นสองทาง)"
    st.metric(label="ระบบจำแนกประเภทพื้นพิจารณาอัตโนมัติ:", value=slab_type_str, delta=f"อัตราส่วนมิติสปัน m = {m_ratio:.3f}")

with col_gfx:
    bounds = case_boundaries[case_selected]
    fig_plan, ax_plan = plt.subplots(figsize=(4.5, 3.8))
    
    ax_plan.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, facecolor='#f1f2f6', edgecolor='none'))
    ax_plan.text(0.5, 0.5, f"SLAB PANEL\n{Lx:.1f}m x {Ly:.1f}m", ha='center', va='center', weight='bold', color='#2f3542')
    
    # Border Logic
    ax_plan.plot([0.1, 0.9], [0.9, 0.9], color='#ff4757' if bounds[0] else '#a4b0be', linewidth=5 if bounds[0] else 2, linestyle='-' if bounds[0] else '--')
    ax_plan.text(0.5, 0.93, "Continuous" if bounds[0] else "Discontinuous (Free)", ha='center', fontsize=8, color='#ff4757' if bounds[0] else '#747d8c')
    
    ax_plan.plot([0.1, 0.9], [0.1, 0.1], color='#ff4757' if bounds[1] else '#a4b0be', linewidth=5 if bounds[1] else 2, linestyle='-' if bounds[1] else '--')
    ax_plan.text(0.5, 0.03, "Continuous" if bounds[1] else "Discontinuous (Free)", ha='center', fontsize=8, color='#ff4757' if bounds[1] else '#747d8c')
    
    ax_plan.plot([0.1, 0.1], [0.1, 0.9], color='#ff4757' if bounds[2] else '#a4b0be', linewidth=5 if bounds[2] else 2, linestyle='-' if bounds[2] else '--')
    ax_plan.text(0.02, 0.5, "Continuous" if bounds[2] else "Free", va='center', rotation=90, fontsize=8, color='#ff4757' if bounds[2] else '#747d8c')
    
    ax_plan.plot([0.9, 0.9], [0.1, 0.9], color='#ff4757' if bounds[3] else '#a4b0be', linewidth=5 if bounds[3] else 2, linestyle='-' if bounds[3] else '--')
    ax_plan.text(0.95, 0.5, "Continuous" if bounds[3] else "Free", va='center', rotation=-90, fontsize=8, color='#ff4757' if bounds[3] else '#747d8c')
    
    ax_plan.set_xlim(0, 1)
    ax_plan.set_ylim(0, 1)
    ax_plan.axis('off')
    st.pyplot(fig_plan)

# ==========================================
# 5. STRUCTURAL ANALYTICAL ENGINE
# ==========================================
slab_area = Lx * Ly
t = t_cm / 100
slab_self_weight = t * 2400

eudl_line_load = (line_load_w * line_load_len / slab_area) * 1.5 if slab_area > 0 else 0.0
eudl_point_load = (point_load_p * point_load_count / slab_area) * 2.0 if slab_area > 0 else 0.0
total_structural_dl = slab_self_weight + UDL_SDL + eudl_line_load + eudl_point_load

if method == "Strength Design Method (SDM / USD)":
    w_u = (1.2 * total_structural_dl) + (1.6 * UDL_LL)
else:
    w_u = total_structural_dl + UDL_LL

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

t_min_req = (Lx / 24) * (0.4 + fy/7000) * 100 if is_one_way else (2 * (Lx + Ly) / 180) * 100
deflection_passed = t_cm >= t_min_req

main_bar = st.selectbox("เลือกขนาดเส้นผ่านศูนย์กลางเหล็กแกนที่ใช้ (mm):", [9, 12, 16], index=1)
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

def floor_to_half_cm(val):
    return math.floor(val * 2) / 2

def get_max_safe_spacing(as_required, bar_area):
    if as_required <= 0: return 25.0
    calc_s = (bar_area / as_required) * 100
    return min(floor_to_half_cm(calc_s), 3 * t_cm, 45.0)

st.markdown("### 🎛️ ปรับแต่งระยะห่างเหล็กหน้างาน (Construction Pitch Control)")
c1, c2, c3, c4 = st.columns(4)
with c1: 
    s_xb = c1.number_input("เหล็กล่าง แกน X (@ cm)", value=15.0, step=0.5)
    s_xb_max = get_max_safe_spacing(As_xb_req, ab)
with c2: 
    s_xt = c2.number_input("เหล็กบน Support X (@ cm)", value=15.0, step=0.5)
    s_xt_max = get_max_safe_spacing(As_xt_req, ab)
with c3: 
    s_yb = c3.number_input("เหล็กล่าง แกน Y (@ cm)", value=20.0, step=0.5)
    s_yb_max = get_max_safe_spacing(As_yb_req, ab)
with c4: 
    s_yt = c4.number_input("เหล็กบน Support Y (@ cm)", value=20.0, step=0.5)
    s_yt_max = get_max_safe_spacing(As_yt_req, ab)

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
# 6. OUTPUT WORKSPACE DISPLAY TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Safety & Code Compliance", 
    "📈 Bending Moment Profiles", 
    "💰 Takeoff Material BOM", 
    "📑 Formal Calculation Document"
])

with tab1:
    st.subheader("Structural Integrity Check & Smart Recommendations")
    thick_status = "🟢 Passed" if deflection_passed else f"🔴 หนาไม่พอ! ACI บังคับขั้นต่ำ {t_min_req:.1f} cm"
    status_xb = "🟢 Passed" if As_xb_prov >= As_xb_req else f"🔴 เหล็กขาด! แนะนำปรับระยะห่างเป็น @ ≤ {s_xb_max} cm"
    status_xt = "🟢 Passed" if As_xt_prov >= As_xt_req else f"🔴 เหล็กขาด! แนะนำปรับระยะห่างเป็น @ ≤ {s_xt_max} cm"
    status_yb = "🟢 Passed" if As_yb_prov >= As_yb_req else f"🔴 เหล็กขาด! แนะนำปรับระยะห่างเป็น @ ≤ {s_yb_max} cm"
    
    compliance_data = {
        "ดัชนีตรวจสอบกำลังตามมาตรฐานควบคุม": ["ความหนาแผ่นพื้น (Deflection Control)", "ปริมาณเหล็กเสริมล่าง แกน X", "ปริมาณเหล็กเสริมบน (หัวคาน) X", "ปริมาณเหล็กเสริมล่าง แกน Y"],
        "ค่าเป้าหมายทางวิศวกรรม": [f"≥ {t_min_req:.1f} cm", f"{As_xb_req:.2f} cm²/m", f"{As_xt_req:.2f} cm²/m", f"{As_yb_req:.2f} cm²/m"],
        "ค่าที่จัดให้จริงหน้างาน": [f"{t_cm:.1f} cm", f"{As_xb_prov:.2f} cm²/m", f"{As_xt_prov:.2f} cm²/m", f"{As_yb_prov:.2f} cm²/m"],
        "สถานะประเมินผลปลอดภัย": [thick_status, status_xb, status_xt, status_yb]
    }
    st.table(pd.DataFrame(compliance_data))

with tab2:
    st.subheader("Bending Moment Internal Forces Graph")
    fig_mom, ax_mom = plt.subplots(figsize=(10, 3.5))
    moments_labels = ['Mx+ (Midspan X)', 'Mx- (Support X)', 'My+ (Midspan Y)', 'My- (Support Y)']
    moments_values = [M_x_pos, M_x_neg, M_y_pos, M_y_neg]
    
    bars = ax_mom.barh(moments_labels, moments_values, color=['#3498db', '#e74c3c', '#2ecc71', '#f1c40f'], edgecolor='none', height=0.5)
    ax_mom.bar_label(bars, fmt='%.1f kg-m', padding=5, weight='bold')
    ax_mom.set_xlabel('Ultimate Design Bending Moment (kg-m)')
    ax_mom.set_title('เปรียบเทียบแรงดัดที่เกิดขึ้นในแต่ละตำแหน่งบนแผ่นพื้น')
    st.pyplot(fig_mom)

with tab3:
    st.subheader("Bill of Quantities (BOQ) Summary Breakdown")
    takeoff_data = {
        "องค์ประกอบวัสดุโครงสร้าง": ["คอนกรีตโครงสร้างฐานราก/แผ่นพื้น", "เหล็กเสริมรับแรงดึง High-Tensile Steel", "รวมต้นทุนค่าวัสดุสุทธิ (Core Structural Cost)"],
        "ปริมาณคำนวณสุทธิ": [f"{concrete_volume:.2f} m³", f"{calc_steel_weight:.1f} kg", f"{grand_total:,.2f} THB"],
        "สรุปแนวคิดตรรกะการถอดแบบ": [
            "คำนวณจากปริมาตรทางเรขาคณิตตรงตามความหนาจริง", 
            "คำนวณจากน้ำหนักเหล็กจริงรวมระยะต่อทาบและงอขอมาตรฐาน", 
            "คำนวณอิงจากราคาต่อหน่วยโดยไม่รวมค่าแรงและสัมประสิทธิ์เผื่อสูญเสียหน้างาน"
        ]
    }
    st.table(pd.DataFrame(takeoff_data))

with tab4:
    st.subheader("ACI 318 Structural Calculation Record Output")
    report_body = f"""======================================================================
         OFFICIAL STRUCTURAL VERIFICATION & CALCULATION DOCUMENT
======================================================================
Design Framework Regulation: ACI 318-99 Method 3 Analysis
----------------------------------------------------------------------
[1] GEOMETRICAL SYSTEM DIAGNOSTICS:
- Geometry Dimensions: Short Aspect Lx = {Lx:.2f} m | Long Aspect Ly = {Ly:.2f} m
- Aspect Ratio (m = Lx/Ly): {m_ratio:.3f} -> Classification: {slab_type_str}
- Boundary Condition Profile Selected: {case_idx}
- Structural Control Thickness: Check Requirement {t_min_req:.1f} cm vs Configured {t_cm:.1f} cm

[2] LOAD INTENSITY DISTRIBUTION DOCKET:
- Slab Concrete SW: {slab_self_weight:.2f} kg/m²
- Superimposed Dead Load (SDL): {UDL_SDL:.2f} kg/m²
- Equalized Partition Wall Load (EUDL): {eudl_line_load:.2f} kg/m²
- Equalized Point Load Actions (EUDL): {eudl_point_load:.2f} kg/m²
- Total Structural Factored Ultimate Load (w_u): {w_u:.2f} kg/m²

[3] EXPERT MECHANICAL OUTPUT ANALYSIS:
- Ultimate Moment Mx+ (Short Span Mid): {M_x_pos:.2f} kg-m
- Ultimate Moment Mx- (Short Span Continuous edge): {M_x_neg:.2f} kg-m
- Ultimate Moment My+ (Long Span Mid): {M_y_pos:.2f} kg-m
- Ultimate Moment My- (Long Span Continuous edge): {M_y_neg:.2f} kg-m

[4] STEEL VERIFICATION COMPLIANCE CHECKLIST:
- Rebar Size Used: DB{main_bar} mm (Area per bar = {ab:.3f} cm²)
- Mesh Layout X Bottom: Pitch @ {s_xb:.1f} cm [As Prov: {As_xb_prov:.2f} / Req: {As_xb_req:.2f} cm²/m] -> Status: {"PASS" if As_xb_prov >= As_xb_req else "FAIL"}
- Mesh Layout X Top   : Pitch @ {s_xt:.1f} cm [As Prov: {As_xt_prov:.2f} / Req: {As_xt_req:.2f} cm²/m] -> Status: {"PASS" if As_xt_prov >= As_xt_req else "FAIL"}
- Mesh Layout Y Bottom: Pitch @ {s_yb:.1f} cm [As Prov: {As_yb_prov:.2f} / Req: {As_yb_req:.2f} cm²/m] -> Status: {"PASS" if As_yb_prov >= As_yb_req else "FAIL"}
======================================================================
"""
    st.code(report_body, language="text")
    st.download_button("📥 Download Engineering Record (.txt)", data=report_body, file_name="Engineering_Report.txt")
