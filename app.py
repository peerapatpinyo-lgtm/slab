import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(page_title="SlabMaster Pro V4 - Real-World Edition", layout="wide")

# Theme Setup
if 'seaborn-v0_8-whitegrid' in plt.style.available:
    plt.style.use('seaborn-v0_8-whitegrid')
elif 'ggplot' in plt.style.available:
    plt.style.use('ggplot')
else:
    plt.style.use('default')

st.title("🏗️ SlabMaster Pro V4 (Real-World Edition)")
st.markdown("**โปรแกรมออกแบบแผ่นพื้นคอนกรีตเสริมเหล็กที่ใช้งานได้จริงหน้างาน** วิเคราะห์ตามมาตรฐาน ACI 318 (วิธีที่ 3)")
st.divider()

# ==========================================
# 2. CORE DATABASE & LOGIC
# ==========================================
def get_full_aci_method3_coeffs(case_num, m_ratio):
    # (Coefficients table remains the same rigorous ACI Method 3 data)
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

case_boundaries = {
    1: (True, True, True, True), 2: (False, False, False, False), 3: (True, False, False, False),
    4: (False, False, True, False), 5: (True, False, True, False), 6: (True, True, False, False),
    7: (False, False, True, True), 8: (True, True, True, False), 9: (True, False, True, True)
}

# ==========================================
# 3. SIDEBAR PARAMETERS (Organized via Expanders)
# ==========================================
with st.sidebar:
    st.header("⚙️ การตั้งค่าหน้างาน")
    
    with st.expander("📐 1. มิติแผ่นพื้น (Geometry)", expanded=True):
        Lx = st.number_input("ด้านสั้น Lx (m)", value=4.0, step=0.1, help="ความยาวด้านที่สั้นกว่าของห้อง (ทิศทางเหล็กรับแรงหลักแกน X)")
        Ly = st.number_input("ด้านยาว Ly (m)", value=5.0, step=0.1, help="ความยาวด้านที่ยาวกว่าของห้อง (ทิศทางเหล็กแกน Y)")
        t_cm = st.slider("ความหนาพื้น t (cm)", min_value=8.0, max_value=35.0, value=15.0, step=0.5, help="ความหนารวมของแผ่นพื้นคอนกรีต")
        covering_cm = st.slider("Covering (cm)", min_value=1.5, max_value=5.0, value=2.0, step=0.5, help="ระยะหุ้มคอนกรีต เพื่อป้องกันสนิม (แผ่นพื้นภายในทั่วไปใช้ 2 - 2.5 ซม.)")

    with st.expander("🛠️ 2. คุณสมบัติวัสดุ (Materials)", expanded=True):
        fc_prime = st.number_input("กำลังคอนกรีต fc' (ksc)", value=280, step=10, help="กำลังอัดทรงกระบอก เช่น 240, 280, 320 ksc")
        st.caption("กำลังครากเหล็ก (Yield Strength):")
        fy_main = st.selectbox("เกรดเหล็กรับแรงหลัก (Main Bar)", [("SD40 (4000 ksc)", 4000), ("SD50 (5000 ksc)", 5000), ("SR24 (2400 ksc)", 2400)], index=0)[1]
        fy_temp = st.selectbox("เกรดเหล็กกันร้าว (Temp Bar)", [("SR24 (2400 ksc)", 2400), ("SD40 (4000 ksc)", 4000)], index=0)[1]

    with st.expander("⚖️ 3. น้ำหนักบรรทุก (Loads)", expanded=False):
        st.info("ระบบจะคิดน้ำหนักแผ่นพื้น (Self-weight) ให้อัตโนมัติ ไม่ต้องบวกเพิ่ม")
        UDL_SDL = st.number_input("น้ำหนักวัสดุทับหลัง SDL (kg/m²)", value=120, help="เช่น กระเบื้อง, ปูนทรายปรับระดับ, ฝ้าเพดาน (ทั่วไป 100-150)")
        UDL_LL = st.number_input("น้ำหนักจร Live Load (kg/m²)", value=250, help="น้ำหนักคน/สิ่งของ (บ้าน=150, ออฟฟิศ=250, ห้าง=400)")

    with st.expander("💰 4. ราคาประเมิน (Costing)", expanded=False):
        unit_concrete_cost = st.number_input("ราคาคอนกรีต (บาท/คิว)", value=2200)
        unit_steel_cost = st.number_input("ราคาเหล็ก (บาท/กก.)", value=28)

# ==========================================
# 4. MAIN WORKSPACE: CONTINUITY SELECTOR
# ==========================================
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📍 ผังการต่อเนื่องของพื้น (Continuity Model)")
    case_idx = st.selectbox("เลือกตำแหน่งของแผ่นพื้นในอาคาร:", [
        "Case 1: พื้นภายใน (ต่อเนื่องทั้ง 4 ด้าน)",
        "Case 2: พื้นเดี่ยว / พื้นหลังคาอิสระ (ไม่ต่อเนื่องเลย)",
        "Case 3: ต่อเนื่องด้านยาว 1 ด้าน (ขอบระเบียงยาว)",
        "Case 4: ต่อเนื่องด้านสั้น 1 ด้าน",
        "Case 5: ต่อเนื่อง 2 ด้านติดกัน (พื้นมุมอาคาร)",
        "Case 6: ต่อเนื่องด้านยาว 2 ด้าน (พื้นทางเดิน/โถง)",
        "Case 7: ต่อเนื่องด้านสั้น 2 ด้าน",
        "Case 8: ต่อเนื่อง 3 ด้าน (ขอบด้านสั้นอิสระ)",
        "Case 9: ต่อเนื่อง 3 ด้าน (ขอบด้านยาวอิสระ)"
    ], help="เลือกตามความเป็นจริงว่า ขอบของแผ่นพื้นนี้มีพื้นห้องอื่นต่อยื่นออกไปหรือไม่")
    case_selected = int(case_idx.split(":")[0].split(" ")[1])
    
    m_ratio = Lx / Ly if Ly > 0 else 0
    is_one_way = m_ratio < 0.5
    
    if is_one_way:
        st.warning(f"**พฤติกรรม: พื้นทางเดียว (One-Way Slab)** (สัดส่วน $m = {m_ratio:.2f} < 0.5$) แรงดัดส่วนใหญ่จะถ่ายลงทางด้านสั้น ทิศทางยาวจะใช้เหล็กกันร้าว")
    else:
        st.info(f"**พฤติกรรม: พื้นสองทาง (Two-Way Slab)** (สัดส่วน $m = {m_ratio:.2f} \\ge 0.5$) แรงดัดจะถ่ายลงทั้ง 2 แกน")

with col2:
    bounds = case_boundaries[case_selected]
    fig_plan, ax_plan = plt.subplots(figsize=(4, 3))
    ax_plan.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, facecolor='#f1f2f6', edgecolor='none'))
    ax_plan.text(0.5, 0.5, f"SLAB PANEL\n{Lx:.1f}m x {Ly:.1f}m", ha='center', va='center', weight='bold')
    
    # Draw boundaries
    ax_plan.plot([0.1, 0.9], [0.9, 0.9], color='#e84118' if bounds[0] else '#7f8fa6', linewidth=4 if bounds[0] else 2, linestyle='-' if bounds[0] else '--')
    ax_plan.text(0.5, 0.95, "Continuous (มีพื้นต่อ)" if bounds[0] else "Free (ขอบลอย)", ha='center', fontsize=9, color='#e84118' if bounds[0] else '#7f8fa6')
    ax_plan.plot([0.1, 0.9], [0.1, 0.1], color='#e84118' if bounds[1] else '#7f8fa6', linewidth=4 if bounds[1] else 2, linestyle='-' if bounds[1] else '--')
    ax_plan.plot([0.1, 0.1], [0.1, 0.9], color='#e84118' if bounds[2] else '#7f8fa6', linewidth=4 if bounds[2] else 2, linestyle='-' if bounds[2] else '--')
    ax_plan.plot([0.9, 0.9], [0.1, 0.9], color='#e84118' if bounds[3] else '#7f8fa6', linewidth=4 if bounds[3] else 2, linestyle='-' if bounds[3] else '--')
    
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
total_dl = slab_self_weight + UDL_SDL
w_u = (1.2 * total_dl) + (1.6 * UDL_LL) # SDM Method Standard

# Moment Calculations
if is_one_way:
    M_x_pos = (w_u * (Lx ** 2)) / 11
    M_x_neg = (w_u * (Lx ** 2)) / 10
    M_y_pos = M_y_neg = 0.0
else:
    cx_n, cx_p_dl, cx_p_ll, cy_n, cy_p_dl, cy_p_ll = get_full_aci_method3_coeffs(case_selected, m_ratio)
    M_x_pos = (1.2 * cx_p_dl * total_dl + 1.6 * cx_p_ll * UDL_LL) * (Lx ** 2)
    M_x_neg = (1.2 * cx_n * total_dl + 1.6 * cx_n * UDL_LL) * (Lx ** 2)
    M_y_pos = (1.2 * cy_p_dl * total_dl + 1.6 * cy_p_ll * UDL_LL) * (Lx ** 2)
    M_y_neg = (1.2 * cy_n * total_dl + 1.6 * cy_n * UDL_LL) * (Lx ** 2)

# Thickness Check
t_min_req = (Lx / 24) * (0.4 + fy_main/7000) * 100 if is_one_way else (2 * (Lx + Ly) / 180) * 100
deflection_passed = t_cm >= t_min_req

# Rebar Area Logic
def compute_exact_as(M, d_eff, fc, fy_g):
    if M <= 0: return 0.0
    M_cm = M * 100
    Rn = M_cm / (0.90 * 100 * (d_eff ** 2))
    inside = 1.0 - (2.0 * Rn) / (0.85 * fc)
    if inside < 0: return -1.0 # Section too small
    return (0.85 * fc / fy_g) * (1.0 - math.sqrt(inside)) * 100 * d_eff

as_min_ratio = 0.0018 if fy_main >= 4000 else 0.0020
As_min_main = as_min_ratio * 100 * t_cm
as_temp_ratio = 0.0018 if fy_temp >= 4000 else 0.0020
As_temp_req = as_temp_ratio * 100 * t_cm

d_x = t_cm - covering_cm - 0.6  # Assume DB12 center
d_y = d_x - 1.2 # Y direction bar rests on X direction

As_xb_req = max(compute_exact_as(M_x_pos, d_x, fc_prime, fy_main), As_min_main)
As_xt_req = max(compute_exact_as(M_x_neg, d_x, fc_prime, fy_main), As_min_main)
if not is_one_way:
    As_yb_req = max(compute_exact_as(M_y_pos, d_y, fc_prime, fy_main), As_min_main)
    As_yt_req = max(compute_exact_as(M_y_neg, d_y, fc_prime, fy_main), As_min_main) if M_y_neg > 0 else 0.0
else:
    As_yb_req = As_temp_req # One way uses temp steel in Y
    As_yt_req = 0.0

# ==========================================
# 6. INTERACTIVE REBAR SELECTION
# ==========================================
st.divider()
st.subheader("🛠️ จัดระยะเหล็กหน้างาน (Interactive Rebar Detailing)")
st.caption("ระบบจะคำนวณและแจ้งเตือนทันทีหากเหล็กที่จัดระยะไว้ ไม่เพียงพอต่อการรับแรง")

col_r1, col_r2 = st.columns(2)
with col_r1:
    main_bar_type = st.selectbox("ขนาดเหล็กรับแรงหลัก (ทิศทาง X)", ["DB10", "DB12", "DB16"], index=1)
    d_main = int(main_bar_type.replace("DB", ""))
    ab_main = (math.pi / 4) * ((d_main / 10) ** 2)
with col_r2:
    temp_bar_type = st.selectbox("ขนาดเหล็กกันร้าว/เหล็กรอง (ทิศทาง Y)", ["RB9", "DB10", "DB12"], index=0)
    d_temp = int(temp_bar_type.replace("RB", "").replace("DB", ""))
    ab_temp = (math.pi / 4) * ((d_temp / 10) ** 2)

def floor_to_half_cm(val):
    return math.floor(val * 2) / 2

def get_max_safe_spacing(as_required, bar_area, is_temp=False):
    if as_required <= 0: return 25.0
    calc_s = (bar_area / as_required) * 100
    max_code = min(5 * t_cm, 45.0) if is_temp else min(3 * t_cm, 45.0)
    return min(floor_to_half_cm(calc_s), max_code)

# Layout Inputs -> with Smart Suggestions
sc1, sc2, sc3, sc4 = st.columns(4)
s_xb = sc1.number_input(f"X-Bottom (@ cm)", value=min(20.0, get_max_safe_spacing(As_xb_req, ab_main)), step=1.0)
s_xt = sc2.number_input(f"X-Top (@ cm)", value=min(20.0, get_max_safe_spacing(As_xt_req, ab_main)), step=1.0)
s_yb = sc3.number_input(f"Y-Bottom (@ cm)", value=min(25.0, get_max_safe_spacing(As_yb_req, ab_temp, is_one_way)), step=1.0)
s_yt = sc4.number_input(f"Y-Top (@ cm)", value=25.0, step=1.0)

As_xb_prov = (ab_main / s_xb) * 100
As_xt_prov = (ab_main / s_xt) * 100
As_yb_prov = (ab_temp / s_yb) * 100
As_yt_prov = (ab_temp / s_yt) * 100 if s_yt > 0 else 0.0

# ==========================================
# 7. RESULTS & DASHBOARD TABS
# ==========================================
st.divider()
tab1, tab2, tab3 = st.tabs(["🚦 สถานะความปลอดภัย (Dashboard)", "📉 กราฟแรงดัด (Analysis)", "📋 สรุปรายการวัสดุ (Takeoff/BOQ)"])

with tab1:
    st.markdown("### สรุปผลการตรวจสอบ (Safety Verification)")
    
    # 1. Deflection Check
    if deflection_passed:
        st.success(f"✔️ ความหนาแผ่นพื้นผ่านเกณฑ์: ใช้ {t_cm} cm (ต้องการขั้นต่ำ {t_min_req:.1f} cm)")
    else:
        st.error(f"❌ พื้นบางเกินไป อาจเกิดการแอ่นตัว!: ต้องการขั้นต่ำ {t_min_req:.1f} cm แต่ใช้ {t_cm} cm")

    # 2. Rebar Checks (Dashboard style)
    c_dash1, c_dash2, c_dash3, c_dash4 = st.columns(4)
    
    def render_rebar_status(col, title, as_prov, as_req, max_s, s_prov):
        if as_prov >= as_req:
            col.success(f"**{title}**\n\nผ่านเกณฑ์ ✅\n\n(ระยะ @{s_prov} cm)")
        else:
            col.error(f"**{title}**\n\nเหล็กขาด! ❌\n\nแนะนำ @ {max_s} cm")

    render_rebar_status(c_dash1, "เหล็กล่างแกน X", As_xb_prov, As_xb_req, get_max_safe_spacing(As_xb_req, ab_main), s_xb)
    render_rebar_status(c_dash2, "เหล็กบนหัวคานแกน X", As_xt_prov, As_xt_req, get_max_safe_spacing(As_xt_req, ab_main), s_xt)
    render_rebar_status(c_dash3, "เหล็กล่างแกน Y", As_yb_prov, As_yb_req, get_max_safe_spacing(As_yb_req, ab_temp, is_one_way), s_yb)
    if not is_one_way and M_y_neg > 0:
        render_rebar_status(c_dash4, "เหล็กบนหัวคานแกน Y", As_yt_prov, As_yt_req, get_max_safe_spacing(As_yt_req, ab_temp), s_yt)
    else:
        c_dash4.info("**เหล็กบนหัวคานแกน Y**\n\nไม่มีโมเมนต์ดัดลบ หรือเป็นพื้นทางเดียว\n\n(ไม่ต้องเสริมรับแรง)")

with tab2:
    st.markdown("### กราฟแสดงโมเมนต์ดัดประลัย (Ultimate Bending Moments)")
    fig_mom, ax_mom = plt.subplots(figsize=(10, 4))
    moments_labels = ['Mx+ (กลางสปัน X)', 'Mx- (หัวคาน X)', 'My+ (กลางสปัน Y)', 'My- (หัวคาน Y)']
    moments_values = [M_x_pos, M_x_neg, M_y_pos, M_y_neg]
    
    # Highlight highest moment
    colors = ['#e74c3c' if m == max(moments_values) else '#3498db' for m in moments_values]
    
    bars = ax_mom.bar(moments_labels, moments_values, color=colors)
    ax_mom.bar_label(bars, fmt='%.1f kg-m', padding=3, weight='bold')
    ax_mom.set_ylabel('Design Bending Moment (kg-m)')
    ax_mom.set_title('จุดสีแดงคือตำแหน่งที่รับแรงดัดสูงสุด (วิกฤตที่สุด)')
    st.pyplot(fig_mom)

with tab3:
    st.markdown("### ปริมาณวัสดุเบื้องต้น (Material Bill of Quantities)")
    vol = slab_area * (t_cm / 100)
    
    # Rough estimate of length per sq.m
    w_main = (math.pi/4) * ((d_main/1000)**2) * 7850
    w_temp = (math.pi/4) * ((d_temp/1000)**2) * 7850
    
    kg_x = ((100/s_xb) + (100/s_xt * 0.5)) * Lx * Ly * w_main
    kg_y = ((100/s_yb) + (100/s_yt * 0.5 if s_yt>0 else 0)) * Ly * Lx * w_temp
    total_kg = kg_x + kg_y

    cost_c = vol * unit_concrete_cost
    cost_s = total_kg * unit_steel_cost

    boq_df = pd.DataFrame({
        "รายการ": ["คอนกรีต", "เหล็กเสริมรับแรง", "รวมทั้งหมด"],
        "ปริมาณ": [f"{vol:.2f} คิว (m³)", f"{total_kg:.1f} กก.", "-"],
        "ประเมินราคา (บาท)": [f"{cost_c:,.2f}", f"{cost_s:,.2f}", f"{(cost_c + cost_s):,.2f}"]
    })
    
    st.table(boq_df)
    st.caption("* หมายเหตุ: การคำนวณราคาเหล็กเป็นการประมาณการสุทธิ ยังไม่รวม % เผื่อการสูญเสีย (Wastage) และความยาวระยะต่อทาบหน้างาน")
