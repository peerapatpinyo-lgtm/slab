import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(page_title="SlabMaster Pro V7 - Detail Calculation", layout="wide")

if 'seaborn-v0_8-whitegrid' in plt.style.available:
    plt.style.use('seaborn-v0_8-whitegrid')
else:
    plt.style.use('default')

st.title("🏗️ SlabMaster Pro V7 (Detailed Calculation Edition)")
st.markdown("**เครื่องมือวิเคราะห์และออกแบบแผ่นพื้นคอนกรีตเสริมเหล็ก (RC Slab Design)** | ความละเอียดสูง อ้างอิง ACI 318")
st.divider()

# ==========================================
# 2. CORE DATABASE (Cached)
# ==========================================
@st.cache_data
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

case_boundaries = {
    1: (True, True, True, True), 2: (False, False, False, False), 3: (True, False, False, False),
    4: (False, False, True, False), 5: (True, False, True, False), 6: (True, True, False, False),
    7: (False, False, True, True), 8: (True, True, True, False), 9: (True, False, True, True)
}

STANDARD_SPACINGS = [10.0, 12.5, 15.0, 17.5, 20.0, 22.5, 25.0, 30.0]

def get_practical_spacing(as_req, bar_area, is_temp=False, t=15.0):
    if as_req <= 0: return 25.0
    calc_s = (bar_area / as_req) * 100
    max_code = min(5 * t, 45.0) if is_temp else min(3 * t, 45.0)
    raw_max = min(calc_s, max_code)
    practical_s = 10.0
    for s in STANDARD_SPACINGS:
        if s <= raw_max: practical_s = s
    return practical_s

# ==========================================
# 3. SIDEBAR PARAMETERS 
# ==========================================
with st.sidebar:
    st.header("⚙️ Design Parameters")
    
    with st.expander("📐 1. มิติแผ่นพื้น (Geometry)", expanded=True):
        input_Lx = st.number_input("ความกว้าง Lx (m)", min_value=1.0, value=4.0, step=0.1)
        input_Ly = st.number_input("ความยาว Ly (m)", min_value=1.0, value=5.0, step=0.1)
        
        Lx = min(input_Lx, input_Ly)
        Ly = max(input_Lx, input_Ly)
        if input_Lx > input_Ly:
            st.warning(f"⚠️ สลับค่า Lx={Lx}m และ Ly={Ly}m อัตโนมัติ (Lx ต้องเป็นด้านสั้น)")
            
        t_cm = st.slider("ความหนาพื้น t (cm)", min_value=8.0, max_value=35.0, value=15.0, step=0.5)
        covering_cm = st.slider("ระยะหุ้ม Cover (cm)", min_value=1.5, max_value=5.0, value=2.0, step=0.5)

    with st.expander("🛠️ 2. คุณสมบัติวัสดุ (Materials)", expanded=True):
        fc_prime = st.number_input("กำลังอัดคอนกรีต fc' (ksc)", min_value=150, value=280, step=10)
        fy_main = st.selectbox("เหล็กรับแรงหลัก (Main)", [("SD40 (4000 ksc)", 4000), ("SD50 (5000 ksc)", 5000)], index=0)[1]
        fy_temp = st.selectbox("เหล็กกันร้าว (Temp)", [("SR24 (2400 ksc)", 2400), ("SD40 (4000 ksc)", 4000)], index=0)[1]

    with st.expander("⚖️ 3. น้ำหนักบรรทุก (Loads)", expanded=True):
        UDL_SDL = st.number_input("น้ำหนักทับหลัง SDL (kg/m²)", min_value=0, value=150)
        ll_preset = st.selectbox("หมวดหมู่การใช้งาน (Live Load)", [
            "ที่พักอาศัย / ห้องนอน (150 kg/m²)", "สำนักงาน / อาคารพาณิชย์ (250 kg/m²)",
            "ทางเดิน / บันได (300 kg/m²)", "ห้างสรรพสินค้า (400 kg/m²)", "กำหนดเอง (Custom)"
        ])
        if ll_preset == "กำหนดเอง (Custom)":
            UDL_LL = st.number_input("น้ำหนักจร (kg/m²)", min_value=0, value=250)
        else:
            UDL_LL = int(ll_preset.split("(")[1].split(" ")[0])

# ==========================================
# 4. MAIN WORKSPACE
# ==========================================
col_setup, col_blueprint = st.columns([1.3, 1])

with col_setup:
    st.subheader("📍 ผังการต่อเนื่อง (Boundary Conditions)")
    case_idx = st.selectbox("เลือกรูปแบบจุดรองรับ (ACI Cases):", [
        "Case 1: พื้นภายใน (ต่อเนื่อง 4 ด้าน)", "Case 2: พื้นเดี่ยว (ไม่ต่อเนื่อง 4 ด้าน)",
        "Case 3: ต่อเนื่องด้านยาว 1 ด้าน", "Case 4: ต่อเนื่องด้านสั้น 1 ด้าน",
        "Case 5: ต่อเนื่อง 2 ด้านติดกัน (พื้นมุม)", "Case 6: ต่อเนื่องด้านยาว 2 ด้าน",
        "Case 7: ต่อเนื่องด้านสั้น 2 ด้าน", "Case 8: ต่อเนื่อง 3 ด้าน (ด้านสั้นอิสระ)",
        "Case 9: ต่อเนื่อง 3 ด้าน (ด้านยาวอิสระ)"
    ])
    case_selected = int(case_idx.split(":")[0].split(" ")[1])
    
    m_ratio = Lx / Ly if Ly > 0 else 0
    is_one_way = m_ratio < 0.5
    
    st.metric(label="อัตราส่วนมิติ (m = Lx/Ly)", value=f"{m_ratio:.3f}")
    if is_one_way:
        st.warning("**พฤติกรรมโครงสร้าง:** พื้นทางเดียว (One-Way Slab)")
    else:
        st.success("**พฤติกรรมโครงสร้าง:** พื้นสองทาง (Two-Way Slab)")

with col_blueprint:
    bounds = case_boundaries[case_selected]
    fig_plan, ax_plan = plt.subplots(figsize=(4, 3.5))
    ax_plan.set_facecolor('#f4f6f9')
    ax_plan.grid(color='white', linestyle='-', linewidth=1.5)
    ax_plan.add_patch(plt.Rectangle((0.15, 0.1), 0.7, 0.8, facecolor='#d1d8e0', edgecolor='#2c3e50', linewidth=2))
    
    ax_plan.annotate(f"Lx = {Lx:.2f} m", xy=(0.5, 0.1), xytext=(0.5, 0.02), arrowprops=dict(arrowstyle='<->'), ha='center', fontsize=9, weight='bold')
    ax_plan.annotate(f"Ly = {Ly:.2f} m", xy=(0.15, 0.5), xytext=(0.02, 0.5), arrowprops=dict(arrowstyle='<->'), va='center', rotation=90, fontsize=9, weight='bold')
    
    def draw_boundary(is_cont, x_line, y_line, label_x, label_y, rot):
        color, style, thick = ('#27ae60', '-', 4) if is_cont else ('#e74c3c', '--', 2)
        ax_plan.plot(x_line, y_line, color=color, linewidth=thick, linestyle=style)
        ax_plan.text(label_x, label_y, "Cont." if is_cont else "Free", ha='center', va='center', rotation=rot, fontsize=8, color=color, weight='bold')

    draw_boundary(bounds[0], [0.15, 0.85], [0.9, 0.9], 0.5, 0.95, 0)
    draw_boundary(bounds[1], [0.15, 0.85], [0.1, 0.1], 0.5, 0.05, 0)
    draw_boundary(bounds[2], [0.15, 0.15], [0.1, 0.9], 0.05, 0.5, 90)
    draw_boundary(bounds[3], [0.85, 0.85], [0.1, 0.9], 0.95, 0.5, -90)
    
    ax_plan.set_xlim(-0.05, 1.05)
    ax_plan.set_ylim(-0.05, 1.05)
    ax_plan.axis('off')
    st.pyplot(fig_plan)

# ==========================================
# 5. REBAR SIZES & EXACT EFFECTIVE DEPTH (d)
# ==========================================
st.divider()
st.subheader("🛠️ ขนาดเหล็กและหน้าตัดวิกฤต (Section Capacity)")

col_b1, col_b2 = st.columns(2)
with col_b1:
    main_bar = st.selectbox("ขนาดเหล็กรับแรงหลัก (ทิศ X)", ["DB10", "DB12", "DB16"], index=1)
    d_main_mm = int(main_bar.replace("DB", ""))
    ab_main = (math.pi / 4) * ((d_main_mm / 10) ** 2)
with col_b2:
    temp_bar = st.selectbox("ขนาดเหล็กกันร้าว/เหล็กทิศ Y", ["RB9", "DB10", "DB12"], index=0)
    d_temp_mm = int(temp_bar.replace("RB", "").replace("DB", ""))
    ab_temp = (math.pi / 4) * ((d_temp_mm / 10) ** 2)

# คำนวณความลึกประสิทธิผลตาม True Layering Sequence ของตะแกรงเหล็กล่าง
d_x = t_cm - covering_cm - (d_main_mm / 10 / 2)
d_y = d_x - (d_main_mm / 10 / 2) - (d_temp_mm / 10 / 2)

# ==========================================
# 6. STRUCTURAL ANALYTICAL ENGINE (RECHECKED)
# ==========================================
slab_self_weight = (t_cm / 100) * 2400
total_dl = slab_self_weight + UDL_SDL
w_u = (1.2 * total_dl) + (1.6 * UDL_LL)

cx_n = cx_p_dl = cx_p_ll = cy_n = cy_p_dl = cy_p_ll = 0.0

if is_one_way:
    M_x_pos = (w_u * (Lx ** 2)) / 11
    M_x_neg = (w_u * (Lx ** 2)) / 10
    M_y_pos = M_y_neg = 0.0
    t_min_req = (Lx / 24) * (0.4 + fy_main/7000) * 100
else:
    cx_n, cx_p_dl, cx_p_ll, cy_n, cy_p_dl, cy_p_ll = get_full_aci_method3_coeffs(case_selected, m_ratio)
    M_x_pos = (1.2 * cx_p_dl * total_dl + 1.6 * cx_p_ll * UDL_LL) * (Lx ** 2)
    M_x_neg = (1.2 * cx_n * total_dl + 1.6 * cx_n * UDL_LL) * (Lx ** 2)
    M_y_pos = (1.2 * cy_p_dl * total_dl + 1.6 * cy_p_ll * UDL_LL) * (Lx ** 2)
    M_y_neg = (1.2 * cy_n * total_dl + 1.6 * cy_n * UDL_LL) * (Lx ** 2)
    t_min_req = (2 * (Lx + Ly) / 180) * 100

deflection_passed = t_cm >= t_min_req

def compute_exact_as(M, d_eff, fc, fy_g):
    if M <= 0: return 0.0
    M_cm = M * 100
    Rn = M_cm / (0.90 * 100 * (d_eff ** 2))
    inside_sqrt = 1.0 - (2.0 * Rn) / (0.85 * fc)
    if inside_sqrt < 0: return -1.0
    return (0.85 * fc / fy_g) * (1.0 - math.sqrt(inside_sqrt)) * 100 * d_eff

# คำนวณปริมาณเหล็กเสริมขั้นต่ำตามมาตรฐานสากล
As_min_main = (0.0018 if fy_main >= 4000 else 0.0020) * 100 * t_cm
As_temp_req = (0.0018 if fy_temp >= 4000 else 0.0020) * 100 * t_cm

# RECHECK: คำนวณ As โดยแยกเกรดกำลังเหล็ก (fy) ของเหล็กแกนหลักและแกนรองให้ถูกต้องแม่นยำ
as_xb_calc = compute_exact_as(M_x_pos, d_x, fc_prime, fy_main)
as_xt_calc = compute_exact_as(M_x_neg, d_x, fc_prime, fy_main)
as_yb_calc = compute_exact_as(M_y_pos, d_y, fc_prime, fy_temp) if not is_one_way else As_temp_req
as_yt_calc = compute_exact_as(M_y_neg, d_y, fc_prime, fy_temp) if (not is_one_way and M_y_neg > 0) else 0.0

if any(val == -1.0 for val in [as_xb_calc, as_xt_calc, as_yb_calc, as_yt_calc]):
    st.error("🚨 **CRITICAL ERROR: พื้นบางเกินไป! หน้าตัดคอนกรีตไม่สามารถรับแรงอัดได้ (Compression Failure)**")
    st.stop()

As_xb_req = max(as_xb_calc, As_min_main)
As_xt_req = max(as_xt_calc, As_min_main)
As_yb_req = max(as_yb_calc, As_min_main) if not is_one_way else As_temp_req
As_yt_req = max(as_yt_calc, As_min_main) if (not is_one_way and M_y_neg > 0) else 0.0

# ==========================================
# 7. SMART REBAR DETAILING (RECHECKED SYNCHRONIZATION)
# ==========================================
s_xb_rec = get_practical_spacing(As_xb_req, ab_main, t=t_cm)
s_xt_rec = get_practical_spacing(As_xt_req, ab_main, t=t_cm)
s_yb_rec = get_practical_spacing(As_yb_req, ab_temp, is_temp=is_one_way, t=t_cm)
s_yt_rec = get_practical_spacing(As_yt_req, ab_temp, t=t_cm) if As_yt_req > 0 else 25.0

sc1, sc2, sc3, sc4 = st.columns(4)
s_xb = sc1.number_input(f"X-Bottom (@ cm)", min_value=5.0, value=s_xb_rec, step=2.5)
s_xt = sc2.number_input(f"X-Top (@ cm)", min_value=5.0, value=s_xt_rec, step=2.5)
s_yb = sc3.number_input(f"Y-Bottom (@ cm)", min_value=5.0, value=s_yb_rec, step=2.5)
s_yt_input = sc4.number_input(f"Y-Top (@ cm)", min_value=5.0, value=s_yt_rec, step=2.5)

# RECHECK LOGIC: จัดการซิงโครไนซ์ตัวแปรเหล็กแกน Y สำหรับพื้นทางเดียวทันที เพื่อป้องกันตารางคำนวณแสดงค่าขัดแย้งกัน
if is_one_way:
    s_yt = s_yb  # พื้นทางเดียว เหล็กกันร้าวบน-ล่าง วิ่งระยะเท่ากันเต็มแผ่นผืน
else:
    s_yt = s_yt_input

As_xb_prov = (ab_main / s_xb) * 100
As_xt_prov = (ab_main / s_xt) * 100
As_yb_prov = (ab_temp / s_yb) * 100
As_yt_prov = (ab_temp / s_yt) * 100 if s_yt > 0 else 0.0

# ==========================================
# 8. DASHBOARDS & CALCULATION SHEET
# ==========================================
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["🚦 แดชบอร์ดตรวจสอบกำลัง", "📈 กราฟพฤติกรรมโครงสร้าง", "📑 รายการคำนวณวิศวกรรม (Detailed)", "📋 แบบขยายหน้าตัดพื้นและประมาณการ"])

with tab1:
    st.subheader("🔍 การตรวจสอบสภาวะการใช้งาน (Serviceability Check)")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(label="ความหนาที่ออกแบบไว้ (t)", value=f"{t_cm:.1f} cm")
    with col_m2:
        st.metric(label="ความหนาขั้นต่ำตามโค้ด (t_min)", value=f"{t_min_req:.1f} cm", 
                  delta=f"{t_cm - t_min_req:.1f} cm", 
                  delta_color="normal" if deflection_passed else "inverse")
    with col_m3:
        status_text = "ผ่าน (PASS)" if deflection_passed else "ไม่ผ่าน (FAIL)"
        st.metric(label="สถานะโครงสร้าง", value=status_text)

    st.divider()

    if deflection_passed:
        st.success(
            f"**การตรวจสอบความหนาพื้น (Deflection Control): ผ่าน ✅**\n\n"
            f"ความหนา $t = {t_cm}$ cm มากกว่าค่าขั้นต่ำตามมาตรฐาน ACI ({t_min_req:.1f} cm) "
            f"แผ่นพื้นมีความแกร่ง (Stiffness) เพียงพอที่จะควบคุมการแอ่นตัวในระยะยาว (Long-term Deflection) "
            f"โดยไม่ต้องคำนวณตรวจสอบค่าการโก่งตัวโดยละเอียด"
        )
    else:
        st.error(
            f"**การตรวจสอบความหนาพื้น (Deflection Control): ไม่ผ่าน ❌**\n\n"
            f"**เหตุผล:** ความหนาพื้นน้อยกว่าค่าขั้นต่ำที่ยอมรับได้ ({t_min_req:.1f} cm) เสี่ยงต่อการเกิดรอยร้าวและแผ่นพื้นแอ่นตัวมากเกินไปจนทำลายโครงสร้างสถาปัตยกรรม\n\n"
            f"**🛠️ คำแนะนำสำหรับวิศวกร:** โปรดกลับไปที่แถบด้านซ้าย (Sidebar) แล้วปรับเพิ่มความหนาพื้น $t$ ให้มีค่าอย่างน้อย **{math.ceil(t_min_req):.1f} cm** หรือมากกว่า เพื่อให้โครงสร้างปลอดภัย"
        )

with tab2:
    st.subheader("📈 แผนภูมิวิเคราะห์โมเมนต์ดัดวิกฤต (Bending Moment Diagram)")
    
    if is_one_way:
        m_labels = ['Mx+ (Midspan X)', 'Mx- (Support X)']
        m_vals = [M_x_pos, M_x_neg]
        colors = ['#2980b9', '#c0392b']  
    else:
        m_labels = ['Mx+ (Mid X)', 'Mx- (Sup X)', 'My+ (Mid Y)', 'My- (Sup Y)']
        m_vals = [M_x_pos, M_x_neg, M_y_pos, M_y_neg]
        colors = ['#2980b9', '#e67e22', '#27ae60', '#d35400']
    
    fig_bar, ax_bar = plt.subplots(figsize=(10, 4))
    ax_bar.set_facecolor('#f8f9fa')
    
    bars = ax_bar.bar(m_labels, m_vals, color=colors, width=0.45, edgecolor='#2c3e50', linewidth=0.8)
    
    max_headroom = max(m_vals) * 1.15 if max(m_vals) > 0 else 100
    ax_bar.set_ylim(0, max_headroom)
    
    ax_bar.bar_label(bars, fmt='%.1f kg-m', padding=6, weight='bold', fontsize=10)
    ax_bar.set_ylabel("Ultimate Moment, $M_u$ (kg-m)", fontsize=10, weight='bold')
    
    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)
    ax_bar.spines['left'].set_color('#bdc3c7')
    ax_bar.spines['bottom'].set_color('#bdc3c7')
    
    plt.tight_layout()
    st.pyplot(fig_bar)

with tab3:
    st.markdown("### 📑 รายการคำนวณวิศวกรรม (Structural Calculation Sheet)")
    
    st.markdown("#### 1. การตรวจสอบพฤติกรรมแผ่นพื้น (Slab Behavior)")
    st.latex(f"m = \\frac{{L_x}}{{L_y}} = \\frac{{{Lx}}}{{{Ly}}} = {m_ratio:.3f}")
    if is_one_way:
        st.info(f"เนื่องจาก $m < 0.5$ แผ่นพื้นมีพฤติกรรมเป็น **พื้นทางเดียว (One-Way Slab)** ดัดตัวเสมือนคานกว้าง")
    else:
        st.success(f"เนื่องจาก $m \\ge 0.5$ แผ่นพื้นมีพฤติกรรมเป็น **พื้นสองทาง (Two-Way Slab)** ถ่ายแรงทั้งสองแกน")

    st.markdown("#### 2. การวิเคราะห์น้ำหนักบรรทุก (Load Analysis)")
    st.latex(f"Dead\\ Load\\ (W_d) = (\\frac{{{t_cm}}}{{100}} \\times 2400) + {UDL_SDL} = {total_dl:.2f}\\ kg/m^2")
    st.latex(f"Ultimate\\ Load\\ (W_u) = 1.2(W_d) + 1.6(L_L) = 1.2({total_dl:.2f}) + 1.6({UDL_LL}) = {w_u:.2f}\\ kg/m^2")
    
    st.markdown("#### 3. การตรวจสอบความหนาขั้นต่ำ (Minimum Thickness for Deflection)")
    if is_one_way:
        st.latex(f"t_{{min}} = \\frac{{L_x}}{{24}} \\left(0.4 + \\frac{{f_y}}{{7000}}\\right) = \\frac{{{Lx*100:.0f}}}{{24}} \\left(0.4 + \\frac{{{fy_main}}}{{7000}}\\right) = {t_min_req:.2f}\\ cm")
    else:
        st.latex(f"t_{{min}} = \\frac{{2(L_x + L_y)}}{{180}} = \\frac{{2({Lx*100:.0f} + {Ly*100:.0f})}}{{180}} = {t_min_req:.2f}\\ cm")
    st.markdown(f"**สรุป:** เลือกใช้ความหนาพื้น $t = {t_cm}\\ cm$")
    st.latex(f"d_x = t - cover - \\frac{{d_{{main}}}}{{2}} = {t_cm} - {covering_cm} - {d_main_mm/20} = {d_x:.2f}\\ cm")

    st.markdown("#### 4. การคำนวณโมเมนต์ดัด (Bending Moment Calculation)")
    if is_one_way:
        st.markdown("ใช้สมการโมเมนต์สำหรับพื้นทางเดียว (เสมือนคานต่อเนื่อง):")
        st.latex(f"M_{{x+}} = \\frac{{W_u L_x^2}}{{11}} = \\frac{{{w_u:.2f} \\times {Lx}^2}}{{11}} = {M_x_pos:.2f}\\ kg-m")
        st.latex(f"M_{{x-}} = \\frac{{W_u L_x^2}}{{10}} = \\frac{{{w_u:.2f} \\times {Lx}^2}}{{10}} = {M_x_neg:.2f}\\ kg-m")
        st.markdown("*แกน Y ไม่เกิดโมเมนต์ดัดหลัก เสริมเพียงเหล็กกันร้าวต้านการยืดหดตัว (Temperature Steel)*")
    else:
        st.markdown("ใช้ตารางสัมประสิทธิ์ ACI Method 3 (สำหรับพื้นสองทาง):")
        st.latex(r"M_x = C_{x} \cdot W \cdot L_x^2 \quad , \quad M_y = C_{y} \cdot W \cdot L_x^2")
        st.latex(f"M_{{x+}} = (1.2({cx_p_dl:.3f})W_d + 1.6({cx_p_ll:.3f})W_l) \\times {Lx}^2 = {M_x_pos:.2f}\\ kg-m")
        st.latex(f"M_{{x-}} = (1.2({cx_n:.3f})W_d + 1.6({cx_n:.3f})W_l) \\times {Lx}^2 = {M_x_neg:.2f}\\ kg-m")
        st.latex(f"M_{{y+}} = (1.2({cy_p_dl:.3f})W_d + 1.6({cy_p_ll:.3f})W_l) \\times {Lx}^2 = {M_y_pos:.2f}\\ kg-m")
        st.latex(f"M_{{y-}} = (1.2({cy_n:.3f})W_d + 1.6({cy_n:.3f})W_l) \\times {Lx}^2 = {M_y_neg:.2f}\\ kg-m")

    st.markdown("#### 5. การคำนวณปริมาณเหล็กเสริมและการผ่านเกณฑ์มาตรฐาน")
    st.latex(r"R_n = \frac{M_u}{\phi b d^2}, \quad \rho = \frac{0.85 f_c'}{f_y} \left(1 - \sqrt{1 - \frac{2 R_n}{0.85 f_c'}}\right)")
    
    calc_df = pd.DataFrame({
        "ตำแหน่งการเสริมเหล็ก": ["เหล็กแกนหลักล่าง ทิศ X (Mx+)", "เหล็กแกนหลักบน ทิศ X (Mx-)", "เหล็กด้านล่าง ทิศ Y (My+)", "เหล็กด้านบน ทิศ Y (My-)"],
        "Moment (kg-m)": [f"{M_x_pos:.1f}", f"{M_x_neg:.1f}", f"{M_y_pos:.1f}", f"{M_y_neg:.1f}"],
        "As Req (cm²/m)": [f"{As_xb_req:.2f}", f"{As_xt_req:.2f}", f"{As_yb_req:.2f}", f"{As_yt_req:.2f}"],
        "As Provided (cm²/m)": [f"{As_xb_prov:.2f}", f"{As_xt_prov:.2f}", f"{As_yb_prov:.2f}", f"{As_yt_prov:.2f}"],
        "ผลการประเมิน": [
            "OK" if As_xb_prov >= As_xb_req else "FAIL", 
            "OK" if As_xt_prov >= As_xt_req else "FAIL", 
            "OK" if As_yb_prov >= As_yb_req else "FAIL", 
            "OK" if (As_yt_prov >= As_yt_req or (is_one_way and M_y_neg == 0)) else "FAIL"
        ]
    })
    st.table(calc_df)

with tab4:
    st.subheader("📋 แบบขยายรายละเอียดการเสริมเหล็ก (Structural Detailing)")
    st.markdown("แบบขยายหน้าตัดสัดส่วนจริง (True Scale) แสดงการซ้อนเลเยอร์ของเหล็กเสริมแยกตามพฤติกรรมอย่างถูกต้อง")

    view_option = st.radio(
        "🔄 เลือกมุมมองตัด (Section View):",
        ["Section A-A (ตัดตามแนว X - เห็นเหล็ก X เป็นเส้นยาว)", "Section B-B (ตัดตามแนว Y - เห็นเหล็ก Y เป็นเส้นยาว)"],
        horizontal=True
    )

    fig_sec, ax_sec = plt.subplots(figsize=(12, 5.5))
    ax_sec.set_facecolor('#ffffff')
    
    span_w = 120.0       
    beam_w = 20.0        
    h_beam = t_cm + 22.0 
    
    # วาดคอนกรีตพื้นและคานรองรับหัวท้าย
    ax_sec.add_patch(plt.Rectangle((-beam_w, t_cm - h_beam), beam_w, h_beam, facecolor='#f1f3f5', edgecolor='#34495e', linewidth=1.5))
    ax_sec.add_patch(plt.Rectangle((span_w, t_cm - h_beam), beam_w, h_beam, facecolor='#f1f3f5', edgecolor='#34495e', linewidth=1.5))
    ax_sec.add_patch(plt.Rectangle((0, 0), span_w, t_cm, facecolor='#f8f9fa', edgecolor='#34495e', linewidth=1.5))

    r_main = (d_main_mm / 10) / 2
    r_temp = (d_temp_mm / 10) / 2

    # กำหนดพิกัด Y ของเหล็กแต่ละเลเยอร์ (Shop Drawing Layering)
    y_x_bot = covering_cm + r_main                                  
    y_y_bot = covering_cm + (2 * r_main) + r_temp                   
    
    y_x_top = t_cm - covering_cm - r_main                           
    y_y_top = t_cm - covering_cm - (2 * r_main) - r_temp            

    dot_spacing = 15.0
    x_dots = [5 + i * dot_spacing for i in range(int(span_w/dot_spacing) + 1)]
    
    if "Section A-A" in view_option:
        line_bot_y = y_x_bot
        line_top_y = y_x_top
        dot_bot_y = y_y_bot
        dot_top_y = y_y_top
        
        lbl_line_bot = f"Main X Bot: {main_bar} @ {s_xb:.1f} cm"
        lbl_line_top = f"Main X Top: {main_bar} @ {s_xt:.1f} cm"
        lbl_dot = f"Cross Y: {temp_bar} @ {s_yb:.1f} cm"
        
        r_dot = r_temp
        top_cut_L = span_w * 0.25 
        show_top_mid = False
    else:
        line_bot_y = y_y_bot
        line_top_y = y_y_top
        dot_bot_y = y_x_bot
        dot_top_y = y_x_top
        
        lbl_dot = f"Cross X: {main_bar} @ {s_xb:.1f} cm (จุด)"
        r_dot = r_main
        
        if is_one_way:
            lbl_line_bot = f"Temp Y Bot: {temp_bar} @ {s_yb:.1f} cm (วิ่งยาว)"
            lbl_line_top = f"Temp Y Top: {temp_bar} @ {s_yt:.1f} cm (วิ่งยาว)"
            top_cut_L = span_w 
            show_top_mid = True
        else:
            lbl_line_bot = f"Main Y Bot: {temp_bar} @ {s_yb:.1f} cm"
            lbl_line_top = f"Main Y Top: {temp_bar} @ {s_yt:.1f} cm"
            top_cut_L = span_w * 0.25 
            show_top_mid = False

    # วาดเหล็กเส้นยาวนอน
    ax_sec.plot([-beam_w + 5, span_w + beam_w - 5], [line_bot_y, line_bot_y], color='#1a73e8', linewidth=2.8, zorder=4, label=lbl_line_bot)
    ax_sec.plot([-beam_w + 5, -beam_w + 5], [line_bot_y, line_bot_y + 4], color='#1a73e8', linewidth=2.8, zorder=4) 
    ax_sec.plot([span_w + beam_w - 5, span_w + beam_w - 5], [line_bot_y, line_bot_y + 4], color='#1a73e8', linewidth=2.8, zorder=4)
    
    if show_top_mid:
        ax_sec.plot([-beam_w + 5, span_w + beam_w - 5], [line_top_y, line_top_y], color='#d93025', linewidth=2.8, zorder=4, label=lbl_line_top)
    else:
        ax_sec.plot([-beam_w + 5, top_cut_L], [line_top_y, line_top_y], color='#d93025', linewidth=2.8, zorder=4, label=lbl_line_top)
        ax_sec.plot([span_w - top_cut_L, span_w + beam_w - 5], [line_top_y, line_top_y], color='#d93025', linewidth=2.8, zorder=4)
    ax_sec.plot([-beam_w + 5, -beam_w + 5], [line_top_y, line_top_y - 5], color='#d93025', linewidth=2.8, zorder=4) 
    ax_sec.plot([span_w + beam_w - 5, span_w + beam_w - 5], [line_top_y, line_top_y - 5], color='#d93025', linewidth=2.8, zorder=4)

    # วาดจุดวงกลมตัดขวาง
    for x in x_dots:
        ax_sec.add_patch(plt.Circle((x, dot_bot_y), r_dot, color='#1e7e34', zorder=5))
        if show_top_mid or (x <= top_cut_L or x >= span_w - top_cut_L):
            ax_sec.add_patch(plt.Circle((x, dot_top_y), r_dot, color='#1e7e34', zorder=5))
            
    ax_sec.scatter([], [], color='#1e7e34', s=60, label=lbl_dot)

    # วาดมิติเส้นบอกขนาด
    ax_sec.annotate('', xy=(span_w + beam_w + 8, 0), xytext=(span_w + beam_w + 8, t_cm), arrowprops=dict(arrowstyle='<->', color='#212529'))
    ax_sec.text(span_w + beam_w + 12, t_cm / 2, f"t = {t_cm} cm", va='center', weight='bold')
    
    if not show_top_mid:
        ax_sec.annotate(f"L/4 = {top_cut_L*0.01:.2f} m", xy=(top_cut_L, line_top_y), xytext=(top_cut_L + 8, line_top_y + 3), 
                        arrowprops=dict(arrowstyle='->', color='#7f8c8d', connectionstyle='arc3,rad=0.15'))

    ax_sec.set_xlim(-beam_w - 12, span_w + beam_w + 35)
    ax_sec.set_ylim(-10, t_cm + 12)
    ax_sec.axis('off')
    ax_sec.legend(loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=3, frameon=True, facecolor='#f8f9fa')
    st.pyplot(fig_sec)

    # 5. RECHECKED MATERIAL TAKEOFF (ตารางประมาณการวัสดุแม่นยำสูง)
    st.divider()
    st.markdown("#### 📊 ปริมาณเหล็กเสริมและคอนกรีตสุทธิต่อตารางเมตร (Estimate Material Takeoff per $1\\ m^2$)")
    
    w_main = (int(''.join(filter(str.isdigit, main_bar))) ** 2) / 162.0
    w_temp = (int(''.join(filter(str.isdigit, temp_bar))) ** 2) / 162.0
    
    # ถอดน้ำหนักเฉลี่ยตามจริง (เหล็กบนคิดสัมประสิทธิ์พื้นที่ความยาวกระจาย 0.5 สำหรับระยะตัดขาด L/4 สองฝั่งคาน)
    kg_x = ((100 / s_xb) * w_main) + ((100 / s_xt) * w_main * 0.5)
    kg_y = ((100 / s_yb) * w_temp) + ((100 / s_yt) * w_temp * (1.0 if is_one_way else 0.5))
    total_steel = kg_x + kg_y
    concrete_vol = (t_cm / 100) * 1.0 * 1.0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("น้ำหนักเหล็กแกน X", f"{kg_x:.2f} kg/m²")
    col2.metric("น้ำหนักเหล็กแกน Y", f"{kg_y:.2f} kg/m²")
    col3.metric("ปริมาตรคอนกรีตพื้น", f"{concrete_vol:.3f} m³/m²")
    
    st.info(f"💡 **รวมน้ำหนักเหล็กเสริมตะแกรงแผ่นพื้นทั้งหมดสุทธิ:** {total_steel:.2f} kg ต่อตารางเมตร")
