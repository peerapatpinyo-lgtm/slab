import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# 1. การตั้งค่าหน้าจอและสไตล์ของระบบ
st.set_page_config(page_title="Enterprise RC Slab Designer", layout="wide")
st.title("🛡️ Enterprise RC Slab Designer (Official Engineering Edition)")
st.caption("ระบบคำนวณและเขียนแบบโครงสร้างแผ่นพื้นตามมาตรฐาน วสท. 1008 / ACI 318")

# 2. ฟังก์ชันระบบคำนวณค่าสัมประสิทธิ์โมเมนต์สองทางตามวิธี ACI Method 3 (Interpolation Engine)
def get_aci_coeffs(case, m_ratio):
    # ข้อมูลตารางสัมประสิทธิ์โมเมนต์ (ตัวอย่างกรณีหลักที่ใช้บ่อยในงานวิศวกรรมอาคาร)
    #โครงสร้างข้อมูล: { case_num: { m_ratio: (Cx_pos, Cx_neg, Cy_pos, Cy_neg) } }
    aci_table = {
        1: { # Case 1: จุดรองรับอิสระทั้ง 4 ด้าน
            1.0: (0.050, 0.000, 0.050, 0.000), 0.9: (0.056, 0.000, 0.044, 0.000),
            0.8: (0.063, 0.000, 0.037, 0.000), 0.7: (0.072, 0.000, 0.028, 0.000),
            0.6: (0.081, 0.000, 0.019, 0.000), 0.5: (0.090, 0.000, 0.010, 0.000)
        },
        2: { # Case 2: ต่อเนื่องกันทั้ง 4 ด้าน (Interior Panel)
            1.0: (0.018, 0.033, 0.018, 0.033), 0.9: (0.022, 0.041, 0.015, 0.028),
            0.8: (0.027, 0.048, 0.012, 0.022), 0.7: (0.033, 0.056, 0.009, 0.016),
            0.6: (0.039, 0.064, 0.006, 0.011), 0.5: (0.045, 0.072, 0.004, 0.007)
        },
        3: { # Case 3: ขอบไม่ต่อเนื่องด้านสั้นหนึ่งด้าน
            1.0: (0.021, 0.038, 0.021, 0.038), 0.9: (0.025, 0.045, 0.017, 0.030),
            0.8: (0.030, 0.053, 0.013, 0.023), 0.7: (0.036, 0.061, 0.009, 0.016),
            0.6: (0.042, 0.069, 0.006, 0.011), 0.5: (0.049, 0.077, 0.004, 0.007)
        },
        4: { # Case 4: ขอบไม่ต่อเนื่องด้านยาวหนึ่งด้าน
            1.0: (0.021, 0.038, 0.021, 0.038), 0.9: (0.026, 0.046, 0.016, 0.031),
            0.8: (0.032, 0.054, 0.012, 0.024), 0.7: (0.039, 0.063, 0.008, 0.017),
            0.6: (0.046, 0.072, 0.005, 0.011), 0.5: (0.054, 0.080, 0.003, 0.007)
        }
    }
    
    selected_case = aci_table.get(case, aci_table[1])
    
    # ดำเนินการลากเส้นกราฟอันดับที่หนึ่ง (Linear Interpolation)
    ratios = sorted(selected_case.keys())
    if m_ratio >= ratios[-1]: return selected_case[ratios[-1]]
    if m_ratio <= ratios[0]: return selected_case[ratios[0]]
    
    for i in range(len(ratios) - 1):
        r1, r2 = ratios[i], ratios[i+1]
        if r1 <= m_ratio <= r2:
            v1, v2 = selected_case[r1], selected_case[r2]
            return tuple(v1[j] + (v2[j] - v1[j]) * (m_ratio - r1) / (r2 - r1) for j in range(4))
    return selected_case[1.0]

# 3. ส่วนรับพารามิเตอร์นำเข้า (Sidebar Engineering Parameters)
st.sidebar.header("⚙️ 1. พารามิเตอร์วัสดุควบคุม")
method = st.sidebar.selectbox("ระเบียบวิธีการออกแบบ", ["วิธีวิเคราะห์กำลัง (SDM / USD)", "วิธีหน่วยแรงใช้งาน (WSD)"])

# แยกประเภทเหล็กมาตรฐาน มอก.
rebar_type = st.sidebar.selectbox("ชั้นคุณภาพเหล็กเสริม (Rebar Grade)", ["SR24 (เหล็กผิวเรียบ)", "SD30 (เหล็กข้ออ้อย)", "SD40 (เหล็กข้ออ้อย)"])
fy = 2400 if "SR24" in rebar_type else (3000 if "SD30" in rebar_type else 4000)

fc_prime = st.sidebar.number_input("กำลังอัดประลัยของคอนกรีต fc' - ทรงกระบอก (กก./ตร.ซม.)", min_value=140, max_value=450, value=240)

st.sidebar.header("📐 2. เรขาคณิตของแผ่นพื้น")
Lx = st.sidebar.number_input("ความยาวช่วงสั้น Lx (เมตร)", min_value=1.0, max_value=12.0, value=3.5, step=0.05)
Ly = st.sidebar.number_input("ความยาวช่วงยาว Ly (เมตร)", min_value=1.0, max_value=25.0, value=4.5, step=0.05)
t_cm = st.sidebar.slider("ความหนาแผ่นพื้นโครงสร้าง t (ซม.)", min_value=8.0, max_value=35.0, value=12.0, step=0.5)
covering_cm = st.sidebar.slider("ระยะหุ้มคอนกรีตเคลียร์ริ่ง (ซม.)", min_value=1.5, max_value=4.0, value=2.0, step=0.5)
rebar_dia = st.sidebar.selectbox("ขนาดเส้นผ่านศูนย์กลางเหล็กเสริมหลัก", [6, 9, 12, 16], index=2)

st.sidebar.header("⚖️ 3. น้ำหนักบรรทุกใช้งาน")
SDL = st.sidebar.number_input("น้ำหนักวัสดุปูผิว + งานระบบ (กก./ตร.ม.)", min_value=0, max_value=600, value=120)
LL = st.sidebar.number_input("น้ำหนักบรรทุกจรตามประเภทอาคาร (กก./ตร.ม.)", min_value=0, max_value=1500, value=250)

# --- ส่วนประมวลผลทางวิศวกรรมเชิงลึก ---
aspect_ratio = Lx / Ly if Ly > 0 else 0
is_one_way = aspect_ratio <= 0.5 # ทิศทางเดียวเมื่อยาวเป็น 2 เท่าของด้านสั้น (Lx/Ly <= 0.5)

t = t_cm / 100
ab = (math.pi / 4) * ((rebar_dia / 10) ** 2)
d = t_cm - covering_cm - (rebar_dia / 20) # Effective depth (cm)

# คำนวณน้ำหนักและการรวมน้ำหนักบรรทุกตามมาตรฐานควบคุม
DL_self = t * 2400
w_dead = DL_self + SDL

if method == "วิธีวิเคราะห์กำลัง (SDM / USD)":
    w_u = (1.2 * w_dead) + (1.6 * LL)
    phi_flexure, phi_shear = 0.90, 0.75
else:
    w_u = w_dead + LL

# วิเคราะห์หาค่าแรงภายใน (Force Analysis)
if is_one_way:
    st.sidebar.subheader("📌 เงื่อนไขขอบพื้นทางเดียว")
    bc_1way = st.sidebar.selectbox("สภาพขอบ", ["Simply Supported", "One End Continuous", "Both Ends Continuous"])
    if bc_1way == "Simply Supported":
        M_x_pos, M_x_neg = (w_u * (Lx ** 2)) / 8, 0.0
    elif bc_1way == "One End Continuous":
        M_x_pos, M_x_neg = (w_u * (Lx ** 2)) / 11, (w_u * (Lx ** 2)) / 10
    else:
        M_x_pos, M_x_neg = (w_u * (Lx ** 2)) / 16, (w_u * (Lx ** 2)) / 11
    M_y_pos, M_y_neg = 0.0, 0.0
    V_u = (w_u * Lx) / 2
else:
    st.sidebar.subheader("📌 เงื่อนไขขอบพื้นสองทาง")
    bc_2way = st.sidebar.selectbox("สภาพขอบพื้นตามระบบ ACI", [
        "Case 1: ขอบอิสระรอบด้าน (Isolated)",
        "Case 2: ขอบต่อเนื่องกันทั้ง 4 ด้าน (Interior)",
        "Case 3: ขอบไม่ต่อเนื่องด้านสั้น 1 ด้าน",
        "Case 4: ขอบไม่ต่อเนื่องด้านยาว 1 ด้าน"
    ])
    case_mapping = {"Case 1: ขอบอิสระรอบด้าน (Isolated)": 1, "Case 2: ขอบต่อเนื่องกันทั้ง 4 ด้าน (Interior)": 2, "Case 3: ขอบไม่ต่อเนื่องด้านสั้น 1 ด้าน": 3, "Case 4: ขอบไม่ต่อเนื่องด้านยาว 1 ด้าน": 4}
    cx_p, cx_n, cy_p, cy_n = get_aci_coeffs(case_mapping[bc_2way], aspect_ratio)
    
    M_x_pos = cx_p * w_u * (Lx ** 2)
    M_x_neg = cx_n * w_u * (Lx ** 2)
    M_y_pos = cy_p * w_u * (Lx ** 2)
    M_y_neg = cy_n * w_u * (Lx ** 2)
    V_u = (w_u * Lx) / 2 * (aspect_ratio / (1 + aspect_ratio)) # แรงเฉือนวิกฤตสูงสุดด้านสั้น

# คำนวณขีดจำกัดหน้าตัดเสริมเหล็กตามเกณฑ์ความปลอดภัย
as_min_ratio = 0.0018 if fy >= 4000 else 0.0020
As_min = as_min_ratio * 100.0 * t_cm

# ตรวจสอบขีดจำกัดสูงสุดพฤติกรรมหน้าตัดเหนียว (SDM)
beta_1 = max(0.85 - (0.05 * (fc_prime - 280) / 70), 0.65) if fc_prime > 280 else 0.85
rho_b = (0.85 * beta_1 * fc_prime / fy) * (6120 / (6120 + fy))
rho_max = 0.75 * rho_b

def structural_design_engine(M_kgm, d_eff, f_c, f_y, mth, r_max):
    if M_kgm <= 0: return 0.0
    M_cm = M_kgm * 100.0
    if mth == "วิธีวิเคราะห์กำลัง (SDM / USD)":
        Rn = M_cm / (0.90 * 100.0 * (d_eff ** 2))
        inside_sqrt = 1.0 - (2.0 * Rn) / (0.85 * f_c)
        if inside_sqrt < 0: return -1.0 # ประลัย คอนกรีตรับแรงบีบไม่พอ
        rho = (0.85 * f_c / f_y) * (1.0 - math.sqrt(inside_sqrt))
        if rho > r_max: return -2.0 # หน้าตัดเปราะเกินไป ผิดเกณฑ์ความเหนียว
        return rho * 100.0 * d_eff
    else: # วิธีหน่วยแรงใช้งาน WSD
        fc_wsd = 0.375 * f_c
        fs_wsd = 1500.0 if f_y >= 3000 else 1200.0
        n_ratio = 11.0
        k_val = n_ratio / (n_ratio + (fs_wsd / fc_wsd))
        j_val = 1.0 - (k_val / 3.0)
        R_val = 0.5 * fc_wsd * k_val * j_val
        if d_eff < math.sqrt(M_cm / (R_val * 100.0)): return -1.0
        return M_cm / (fs_wsd * j_val * d_eff)

# ประมวลผลพื้นที่เหล็กเสริมเรียงตามแกน
fail_flag = 0
as_x_b_req = structural_design_engine(M_x_pos, d, fc_prime, fy, method, rho_max)
as_x_t_req = structural_design_engine(M_x_neg, d, fc_prime, fy, method, rho_max)
as_y_b_req = structural_design_engine(M_y_pos, d, fc_prime, fy, method, rho_max)
as_y_t_req = structural_design_engine(M_y_neg, d, fc_prime, fy, method, rho_max)

if any(v == -1.0 for v in [as_x_b_req, as_x_t_req, as_y_b_req, as_y_t_req]): fail_flag = 1 # Thickness Failure
if any(v == -2.0 for v in [as_x_b_req, as_x_t_req, as_y_b_req, as_y_t_req]): fail_flag = 2 # Brittle Failure

As_X_Bottom = max(as_x_b_req, As_min)
As_X_Top = max(as_x_t_req, As_min) if M_x_neg > 0 else 0.0
As_Y_Bottom = max(as_y_b_req, As_min) if not is_one_way else As_min
As_Y_Top = max(as_y_t_req, As_min) if (not is_one_way and M_y_neg > 0) else 0.0

# ฟังก์ชันคำนวณระยะห่างตามข้อกำหนด วสท./ACI และการโก่งตัวเชิงควบคุม
def strict_spacing(as_target, bar_area, thickness):
    if as_target <= 0: return 0.0
    s_calc = (bar_area / as_target) * 100.0
    s_max = min(3 * thickness, 45.0) # เกณฑ์ระยะสูงสุดเพื่อควบคุมรอยร้าวและแรงยึดเกาะ
    return min(s_calc, s_max)

s_xb = strict_spacing(As_X_Bottom, ab, t_cm)
s_xt = strict_spacing(As_X_Top, ab, t_cm)
s_yb = strict_spacing(As_Y_Bottom, ab, t_cm)
s_yt = strict_spacing(As_Y_Top, ab, t_cm)

# ตรวจสอบขีดความสามารถแรงเฉือนประลัย (Shear Capacity Verification)
if method == "วิธีวิเคราะห์กำลัง (SDM / USD)":
    V_c = 0.53 * math.sqrt(fc_prime) * 100.0 * d
    V_allow = phi_shear * V_c
else:
    V_c = 0.29 * math.sqrt(fc_prime) * 100.0 * d
    V_allow = V_c

shear_passed = V_u <= V_allow

# ตรวจสอบเกณฑ์ความหนาขั้นต่ำควบคุมการโก่งตัวสะสม (Deflection Control Minimum Thickness)
t_min_modifier = (0.4 + fy / 7000) if fy != 4000 else 1.0
if is_one_way:
    t_min_threshold = (Lx / 24) * t_min_modifier * 100.0 # สมมติกรณีต่อเนื่องปลายด้านเดียวเป็นเกณฑ์ทั่วไป
else:
    t_min_threshold = (2 * (Lx + Ly) / 180) * 100.0
deflection_safe = t_cm >= t_min_threshold

# --- ฟังก์ชันเขียนแบบดีเทลวิศวกรรมชั้นสูง (Advanced Structural Plotting Engine) ---
def draw_engineering_blueprint(t_h, cov, db_size, sp_xb, sp_xt):
    fig, ax = plt.subplots(figsize=(12, 3.8))
    # ก้อนคอนกรีตพื้นและฐานคานรองรับรองพื้นด้านข้าง
    ax.add_patch(plt.Rectangle((10, 0), 80, t_h, facecolor='#f8f9fa', edgecolor='#2c3e50', linewidth=2.5, hatch='/'))
    ax.add_patch(plt.Rectangle((0, -15), 10, t_h + 15, facecolor='#bdc3c7', edgecolor='#34495e', linewidth=2))
    ax.add_patch(plt.Rectangle((90, -15), 10, t_h + 15, facecolor='#bdc3c7', edgecolor='#34495e', linewidth=2))
    
    # วาดเหล็กเสริมล่าง (Main Bottom Rebars)
    ax.plot([2, 98], [cov, cov], color='#d35400', linewidth=2.5, linestyle='-', label='Bottom Main Rebar')
    for x in range(15, 90, int(sp_xb) if sp_xb > 0 else 20):
        ax.plot(x, cov, marker='o', markersize=6, color='#c0392b')
        
    # วาดเหล็กเสริมบนบริเวณหัวคาน (Negative Top Rebars)
    if sp_xt > 0:
        # ระยะล้วงเหล็กหักงอ 0.25 ของความยาวช่วงตามมาตรฐาน
        ax.plot([0, 32], [t_h - cov, t_h - cov], color='#2980b9', linewidth=2.5)
        ax.plot([68, 100], [t_h - cov, t_h - cov], color='#2980b9', linewidth=2.5, label='Top Support Rebar')
        for x in list(range(2, 30, int(sp_xt))) + list(range(70, 98, int(sp_xt))):
            ax.plot(x, t_h - cov, marker='o', markersize=6, color='#2c3e50')
            
    # เพิ่มสัญลักษณ์เส้นมิติและลูกศรกำกับระยะจัด
    ax.annotate(f'Clear Cover {cov} cm', xy=(50, 0), xytext=(50, -6), arrowprops=dict(arrowstyle="->", color="black"))
    ax.text(35, t_h/2, f"🔥 DB{db_size} @ {sp_xb:.1f} cm", color='#d35400', weight='bold', fontsize=11)
    
    ax.set_xlim(-5, 105)
    ax.set_ylim(-18, t_h + 8)
    ax.axis('off')
    return fig

# --- ส่วนติดต่อผู้ใช้งานหลัก (Main App Layout Dashboard) ---
m_col1, m_col2 = st.columns([7, 3])

with m_col1:
    st.subheader("📊 ผลลัพธ์และระบบตรวจสอบสถานะความปลอดภัยวิกฤต")
    
    # แผงตรวจสอบสถานะความเสียหาย (Fail-Safe Traffic Lights)
    stat_flexure = "🟢 ผ่าน" if fail_flag == 0 else ("🔴 ล้มเหลว (ความหนาหน้าตัดคอนกรีตไม่พอ)" if fail_flag == 1 else "🟡 ผิดเกณฑ์ความเหนียว (Over-Reinforced)")
    stat_shear = "🟢 ผ่าน" if shear_passed else "🔴 ล้มเหลว (เกิดแรงเฉือนทะลุหน้าตัด)"
    stat_deflect = "🟢 ผ่านเกณฑ์ความหนาขั้นต่ำ" if deflection_safe else "🟡 เสี่ยงแอ่นตัว (ความหนาน้อยกว่าข้อแนะนำมาตรฐาน)"
    
    status_df = pd.DataFrame({
        "รายการตรวจสอบเชิงโครงสร้าง": ["กำลังรับแรงดัด (Flexural Capacity Checking)", "กำลังรับแรงเฉือน (Shear Validation)", "เกณฑ์การโก่งตัวในระยะยาว (Deflection Control)"],
        "สถานะการตรวจสอบ": [stat_flexure, stat_shear, stat_deflect]
    })
    st.table(status_df)
    
    if fail_flag == 0 and shear_passed:
        st.write("📐 **แบบแสดงรายละเอียดการจัดเรียงเหล็กเส้นโครงสร้างจริง (Structural Engineering Blueprint Detail):**")
        st.pyplot(draw_engineering_blueprint(t_cm, covering_cm, rebar_dia, s_xb, s_xt))

with m_col2:
    st.subheader("🎯 บันทึกรายการจัดเหล็ก (BBS)")
    
    bbs_data = {
        "ประเภทหน้าตัด/ตำแหน่ง": ["เหล็กเสริมแกน X (ล่าง)", "เหล็กเสริมหัวคาน X (บน)", "เหล็กเสริมแกน Y (ล่าง)", "เหล็กเสริมหัวคาน Y (บน)"],
        "ระยะจัดทำจริงหน้างาน": [
            f"DB{rebar_dia} @ {s_xb:.1f} ซม." if s_xb > 0 else "จัดตามเหล็กกันร้าว",
            f"DB{rebar_dia} @ {s_xt:.1f} ซม." if s_xt > 0 else "ไม่ต้องเสริมเหล็กโครงสร้าง",
            f"DB{rebar_dia} @ {s_yb:.1f} ซม." if s_yb > 0 else "จัดตามเหล็กกันร้าว",
            f"DB{rebar_dia} @ {s_yt:.1f} ซม." if s_yt > 0 else "ไม่ต้องมีเหล็กโครงสร้าง"
        ],
        "พื้นที่เหล็กจริง ($cm^2/m$)": [f"{As_X_Bottom:.2f}", f"{As_X_Top:.2f}", f"{As_Y_Bottom:.2f}", f"{As_Y_Top:.2f}"]
    }
    st.table(pd.DataFrame(bbs_data))

# --- ระบบจัดพิมพ์เล่มคำนวณทางวิศวกรรมอิเล็กทรอนิกส์ (Professional Verification Sheet) ---
st.markdown("---")
with st.expander("📑 เปิดดูเอกสารรายการคำนวณและสัมประสิทธิ์เพื่อใช้แนบขออนุมัติ"):
    
    calc_sheet_text = f"""======================================================================
         PROFESSIONAL STRUCTURAL DESIGN REPORT: REINFORCED CONCRETE SLAB
======================================================================
สเปกและพฤติกรรมโครงสร้างอาคาร: {slab_type_str if 'slab_type_str' in locals() else "Slab Panel"}
เกณฑ์ข้อกำหนดมาตรฐานที่เลือกใช้: {method}
----------------------------------------------------------------------
[PART 1] พารามิเตอร์และมิติทางเรขาคณิต:
- มิติแผ่นพื้นโครงสร้าง: Lx = {Lx:.2f} m, Ly = {Ly:.2f} m | อัตราส่วนสัดส่วนช่วง (m) = {aspect_ratio:.2f}
- ความหนาของแผ่นพื้นแนะแนว (t): {t_cm:.1f} cm | ระยะลึกประสิทธิผลปฏิบัติงานจริง (d) = {d:.2f} cm
- กำลังแรงอัดประลัยวัสดุคอนกรีต (fc'): {fc_prime} kg/cm²
- กำลังจุดคลิตจุดทลายวัสดุเหล็กเสริม (fy): {fy} kg/cm²

[PART 2] ผลการประเมินแรงภายในและเสถียรภาพความปลอดภัย:
- น้ำหนักบรรทุกรวมแผ่กระจาย (w_u): {w_u:.2f} kg/m²
- โมเมนต์ดัดบวกประลัยแกนสั้น (Mx +): {M_x_pos:.2f} kg-m
- โมเมนต์ดัดลบประลัยขอบริมคาน (Mx -): {M_x_neg:.2f} kg-m
- แรงเฉือนแบบแผ่ประลัยสูงสุดที่ขอบหน้าตัด (V_u): {V_u:.2f} kg
- แรงเฉือนสูงสุดที่เนื้อคอนกรีตสามารถต้านทานได้ (Phi*Vc): {V_allow:.2f} kg -> {"[ผ่านเกณฑ์ความปลอดภัย]" if shear_passed else "[ไม่ผ่านเกณฑ์แรงเฉือนพังทลาย]"}

[PART 3] ข้อกำหนดสรุปรายการผูกเหล็กและระยะเว้นหน้างานจริง (ต่อความกว้าง 1 เมตร):
- เหล็กล่าง แนวช่วงสั้น (Main X): DB{rebar_dia} @ {s_xb:.1f} ซม. (As,req = {As_X_Bottom:.2f} cm²/m)
- เหล็กบน หัวคานช่วงสั้น (Top X) : DB{rebar_dia} @ {s_xt:.1f} ซม. (As,req = {As_X_Top:.2f} cm²/m)
- เหล็กล่าง แนวช่วงยาว (Main Y): DB{rebar_dia} @ {s_yb:.1f} ซม. (As,req = {As_Y_Bottom:.2f} cm²/m)
- เหล็กบน หัวคานช่วงยาว (Top Y) : DB{rebar_dia} @ {s_yt:.1f} ซม. (As,req = {As_Y_Top:.2f} cm²/m)
----------------------------------------------------------------------
*รายงานนี้ออกโดยระบบคำนวณอัตโนมัติอ้างอิงสมการสมดุลหน่วยแรงจำกัดตามข้อกำหนดสากล วสท./ACI*
"""
    st.code(calc_sheet_text, language="text")
    st.download_button(label="📥 Download Official Calculation Sheet (.txt)", data=calc_sheet_text, file_name="RC_Slab_Design_Report.txt", mime="text/plain")
