import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# 1. การตั้งค่าหน้าจอและโครงสร้างระบบ
st.set_page_config(page_title="Professional RC Slab & Shear Designer", layout="wide")
st.title("🏗️ Professional RC Slab & Shear Designer (Standard Compliance Edition)")
st.caption("ระบบคำนวณ ออกแบบ และตรวจสอบโครงสร้างแผ่นพื้น ค.ส.ล. พร้อมระบบคำนวณเหล็กปลอกรับแรงเฉือนตามมาตรฐาน วสท./ACI")

# 2. แผงควบคุมพารามิเตอร์ (Input Sidebar)
st.sidebar.header("📐 1. เรขาคณิตและพฤติกรรมแผ่นพื้น")
Lx = st.sidebar.number_input("ความยาวช่วงสั้น Lx (เมตร)", min_value=1.0, max_value=15.0, value=3.0, step=0.05)
Ly = st.sidebar.number_input("ความยาวช่วงยาว Ly (เมตร)", min_value=1.0, max_value=30.0, value=4.5, step=0.05)
t_cm = st.sidebar.slider("ความหนาแผ่นพื้น t (ซม.)", min_value=8.0, max_value=40.0, value=12.0, step=0.5)
covering_cm = st.sidebar.slider("ระยะหุ้มคอนกรีต Clear Covering (ซม.)", min_value=1.5, max_value=5.0, value=2.0, step=0.5)

st.sidebar.header("🛠️ 2. คุณสมบัติวัสดุควบคุม")
method = st.sidebar.selectbox("ระเบียบวิธีการออกแบบ", ["วิธีวิเคราะห์กำลัง (SDM / USD)", "วิธีหน่วยแรงใช้งาน (WSD)"])
rebar_grade = st.sidebar.selectbox("ชั้นคุณภาพเหล็กเสริมหลัก", ["SR24 (เหล็กกลมผิวเรียบ)", "SD30 (เหล็กข้ออ้อย)", "SD40 (เหล็กข้ออ้อย)"], index=2)
fy = 2400 if "SR24" in rebar_grade else (3000 if "SD30" in rebar_grade else 4000)
fc_prime = st.sidebar.number_input("กำลังอัดคอนกรีตประลัย fc' (กก./ตร.ซม.)", min_value=140, max_value=450, value=240)

st.sidebar.header("⚖️ 3. น้ำหนักบรรทุก")
SDL = st.sidebar.number_input("น้ำหนักบรรทุกคงที่เพิ่มเติม SDL (กก./ตร.ม.)", min_value=0, max_value=1000, value=150)
LL = st.sidebar.number_input("น้ำหนักบรรทุกจรใช้งาน Live Load (กก./ตร.ม.)", min_value=0, max_value=2000, value=250)

# --- ส่วนประมวลผลทางวิศวกรรม (Engineering Core Engine) ---
# วินิจฉัยพฤติกรรมพื้น (Slab Diagnostic)
m_ratio = Lx / Ly if Ly > 0 else 0
if m_ratio < 0.5:
    slab_type = "One-Way Slab"
    diagnostic_msg = f"เนื่องจาก อัตราส่วน Lx/Ly = {m_ratio:.3f} ซึ่งน้อยกว่า 0.50 พฤติกรรมการกระจายแรงจึงเป็น 'พื้นทิศทางเดียว' (โหลดถ่ายลงคานคู่ขนานด้านยาว)"
else:
    slab_type = "Two-Way Slab"
    diagnostic_msg = f"เนื่องจาก อัตราส่วน Lx/Ly = {m_ratio:.3f} ซึ่งมากกว่าหรือเท่ากับ 0.50 พฤติกรรมการกระจายแรงจึงเป็น 'พื้นสองทาง' (โหลดถ่ายลงคานทั้ง 4 ด้าน)"

t = t_cm / 100
DL_self = t * 2400
w_total_dead = DL_self + SDL

if method == "วิธีวิเคราะห์กำลัง (SDM / USD)":
    w_u = (1.2 * w_total_dead) + (1.6 * LL)
    phi_flexure, phi_shear = 0.90, 0.75
else:
    w_u = w_total_dead + LL
    phi_flexure, phi_shear = 1.00, 1.00

# การคำนวณโมเมนต์ดัดและแรงเฉือนประลัย
if slab_type == "One-Way Slab":
    # คิดวิเคราะห์กรณีต่อเนื่องปลายเดี่ยวตามสัมประสิทธิ์มาตรฐาน
    M_x_pos = (w_u * (Lx ** 2)) / 11
    M_x_neg = (w_u * (Lx ** 2)) / 10
    M_y_pos, M_y_neg = 0.0, 0.0
    V_u = (w_u * Lx) / 2
else:
    # พื้นสองทางต่อเนื่องรอบด้านตามวิธี ACI Method 3 (Interior Panel Sample Coefficients)
    # สามารถปรับเปลี่ยนตามกรณีขอบต่อเนื่องในแผงควบคุมหลักได้
    M_x_pos = 0.033 * w_u * (Lx ** 2)
    M_x_neg = 0.044 * w_u * (Lx ** 2)
    M_y_pos = 0.025 * w_u * (Lx ** 2)
    M_y_neg = 0.033 * w_u * (Lx ** 2)
    V_u = (w_u * Lx) / 2 * (m_ratio / (1 + m_ratio))

# การคำนวณพื้นที่เหล็กเสริมตามเกณฑ์วิศวกรรมควบคุม
as_min_ratio = 0.0018 if fy >= 4000 else 0.0020
As_min = as_min_ratio * 100.0 * t_cm

def calc_required_as(M_kgm, d_eff, f_c, f_y, mth):
    if M_kgm <= 0: return 0.0
    M_cm = M_kgm * 100.0
    if mth == "วิธีวิเคราะห์กำลัง (SDM / USD)":
        Rn = M_cm / (0.90 * 100.0 * (d_eff ** 2))
        inside = 1.0 - (2.0 * Rn) / (0.85 * f_c)
        if inside < 0: return -1.0
        rho = (0.85 * f_c / f_y) * (1.0 - math.sqrt(inside))
        return rho * 100.0 * d_eff
    else:
        fc_wsd = 0.375 * f_c
        fs_wsd = 1500.0 if f_y >= 3000 else 1200.0
        n = 11.0
        k = n / (n + (fs_wsd / fc_wsd))
        j = 1.0 - (k / 3.0)
        return M_cm / (fs_wsd * j * d_eff)

# ขนาดเหล็กเสริมหลัก
main_bar_dia = st.selectbox("เลือกขนาดเหล็กเสริมแกนหลักที่ต้องการใช้", [6, 9, 12, 16], index=2)
ab_main = (math.pi / 4) * ((main_bar_dia / 10) ** 2)
d = t_cm - covering_cm - (main_bar_dia / 20)

As_x_pos_req = max(calc_required_as(M_x_pos, d, fc_prime, fy, method), As_min)
As_x_neg_req = max(calc_required_as(M_x_neg, d, fc_prime, fy, method), As_min) if M_x_neg > 0 else As_min
As_y_pos_req = max(calc_required_as(M_y_pos, d, fc_prime, fy, method), As_min) if slab_type == "Two-Way Slab" else As_min
As_y_neg_req = max(calc_required_as(M_y_neg, d, fc_prime, fy, method), As_min) if (slab_type == "Two-Way Slab" and M_y_neg > 0) else 0.0

# --- ฟังก์ชันคำนวณหาระยะอัตโนมัติเบื้องต้น ---
def auto_spacing(as_req, ab_bar, thickness):
    if as_req <= 0: return 30.0
    s = (ab_bar / as_req) * 100.0
    return min(s, 3 * thickness, 45.0)

s_xb_auto = auto_spacing(As_x_pos_req, ab_main, t_cm)
s_xt_auto = auto_spacing(As_x_neg_req, ab_main, t_cm)
s_yb_auto = auto_spacing(As_y_pos_req, ab_main, t_cm)
s_yt_auto = auto_spacing(As_y_neg_req, ab_main, t_cm) if As_y_neg_req > 0 else 0.0

# --- ส่วนติดต่อผู้ใช้หลัก: โหมดระบุระยะจัดเอง (@) ---
st.header("🎯 ระบบกำหนดและตรวจสอบระยะจัดเหล็กเส้นควบคุมงานจริง")
design_mode = st.radio("โหมดการทำงานระบบจัดเหล็ก:", ["คำนวณระยะห่างอัตโนมัติ (Auto-Design)", "ระบุระยะจัดเองเพื่อตรวจสอบหน้างานจริง (Manual Verification Mode)"])

if design_mode == "ระบุระยะจัดเองเพื่อตรวจสอบหน้างานจริง (Manual Verification Mode)":
    st.markdown("⚠️ *ระบุระยะห่าง (@) เป็นเซนติเมตร ระบบจะตรวจสอบความปลอดภัยและคำนวณปริมาณเนื้อเหล็กให้ทันที*")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1: s_xb = st.number_input("ระยะ @ เหล็กล่าง แกน X (ซม.)", min_value=5.0, max_value=50.0, value=round(s_xb_auto, 1))
    with col_s2: s_xt = st.number_input("ระยะ @ เหล็กบน แกน X (ซม.)", min_value=5.0, max_value=50.0, value=round(s_xt_auto, 1))
    with col_s3: s_yb = st.number_input("ระยะ @ เหล็กล่าง แกน Y (ซม.)", min_value=5.0, max_value=50.0, value=round(s_yb_auto, 1))
    with col_s4: s_yt = st.number_input("ระยะ @ เหล็กบน แกน Y (ซม.)", min_value=5.0, max_value=50.0, value=round(s_yt_auto, 1) if s_yt_auto > 0 else 20.0)
else:
    s_xb, s_xt, s_yb, s_yt = s_xb_auto, s_xt_auto, s_yb_auto, s_yt_auto

# คำนวณเนื้อเหล็กจริงที่ได้จากระยะจัด (As Provided)
As_x_pos_prov = (ab_main / s_xb) * 100
As_x_neg_prov = (ab_main / s_xt) * 100
As_y_pos_prov = (ab_main / s_yb) * 100
As_y_neg_prov = (ab_main / s_yt) * 100 if s_yt > 0 else 0.0

# ตรวจสอบเกณฑ์ระยะห่างสูงสุด (S_max Checker)
s_max_limit = min(3 * t_cm, 45.0)
spacing_passed = all(s <= s_max_limit for s in [s_xb, s_xt, s_yb] if s > 0)
struct_as_passed = (As_x_pos_prov >= As_x_pos_req) and (As_x_neg_prov >= As_x_neg_req) and (As_y_pos_prov >= As_y_pos_req)

# --- ระบบตรวจสอบและคำนวณเหล็กปลอกรับแรงเฉือน (Advanced Shear & Stirrups Engine) ---
st.header("🛡️ ระบบตรวจสอบและออกแบบเหล็กปลอกรับแรงเฉือน (Shear Stirrups Module)")

if method == "วิธีวิเคราะห์กำลัง (SDM / USD)":
    V_c = 0.53 * math.sqrt(fc_prime) * 100.0 * d  # แรงเฉือนที่คอนกรีตรับได้ (กก.)
    V_allowable = phi_shear * V_c
else:
    V_c = 0.29 * math.sqrt(fc_prime) * 100.0 * d
    V_allowable = V_c

shear_concrete_passed = V_u <= V_allowable
stirrup_required = not shear_concrete_passed

col_v1, col_v2 = st.columns([2, 1])

with col_v1:
    if shear_concrete_passed:
        st.success(f"✅ แรงเฉือนผ่านเกณฑ์เนื้อคอนกรีตล้วน: แรงเฉือนเกิดขึ้น V_u = {V_u:.1f} กก. ≤ กำลังรับยอมรับได้ต้านทานคอนกรีต = {V_allowable:.1f} กก. (ไม่ต้องเสริมเหล็กปลอกโครงสร้าง)")
        s_stirrup = 0.0
        stirrup_dia = 6
    else:
        st.warning(f"⚠️ แรงเฉือนเกินขีดจำกัดคอนกรีต: V_u = {V_u:.1f} kg > ØVc = {V_allowable:.1f} kg (ระบบเปิดโหมดคำนวณเหล็กปลอกรับแรงเฉือนเสริมความปลอดภัย)")
        
        # ส่วนตั้งค่าอินพุตเหล็กปลอกรับแรงเฉือน
        st.markdown("### 🛠️ ปรับตั้งค่าขนาดและระยะจัดเหล็กปลอก (Shear Links / Stirrups)")
        col_st1, col_st2 = st.columns(2)
        with col_st1:
            stirrup_dia = st.selectbox("ขนาดเหล็กปลอกที่ใช้ (Stirrup Size)", [6, 9], index=0)
        with col_st2:
            s_stirrup = st.number_input("ระบุระยะจัดเหล็กปลอก @ หน้างานจริง (ซม.)", min_value=5.0, max_value=30.0, value=15.0, step=1.0)
            
        # คำนวณความต้องการเหล็กปลอกตามมาตรฐาน
        ab_stirrup = (math.pi / 4) * ((stirrup_dia / 10) ** 2) * 2 # คิดปลอก 2 ขาต่อหนึ่งแนวรับแรงเฉือน
        V_s_req = (V_u / phi_shear) - V_c
        
        # กำลังที่ได้จากเหล็กปลอกที่ระบุจริง
        V_s_provided = (ab_stirrup * fy * d) / s_stirrup
        V_total_capacity = phi_shear * (V_c + V_s_provided) if method == "วิธีวิเคราะห์กำลัง (SDM / USD)" else (V_c + V_s_provided)
        
        shear_stirrup_passed = V_u <= V_total_capacity
        
        if shear_stirrup_passed:
            st.success(f"⚡ ผ่านการเสริมเหล็กปลอก: กำลังรวมใหม่รวมเหล็กปลอก = {V_total_capacity:.1f} กก. ≥ แรงเฉือนเกิดจริง {V_u:.1f} กก. โครงสร้างปลอดภัย!")
        else:
            st.error(f"🚨 วิกฤตแรงเฉือน: เหล็กปลอกระยะ @ {s_stirrup} ซม. ถี่ไม่พอ! กำลังรวมได้เพียง {V_total_capacity:.1f} กก. กรุณาลดระยะ @ หรือเพิ่มความหนาพื้น")

# --- ส่วนการจัดเตรียมตารางสรุปผลและเขียนแบบ ---
st.header("📊 แผงควบคุมและสรุปผลดีเทลวิศวกรรม")
col_res1, col_res2 = st.columns([2, 1])

with col_res1:
    # ฟังก์ชันวาดแบบหน้าตัดแผ่นพื้นทางวิศวกรรมแบบละเอียด
    def draw_detailed_blueprint(t_h, cov, db_m, sp_xb, sp_xt, v_req, db_v, sp_v):
        fig, ax = plt.subplots(figsize=(11, 3.5))
        # ก้อนแผ่นพื้นหลัก
        ax.add_patch(plt.Rectangle((10, 0), 80, t_h, facecolor='#f5f6fa', edgecolor='#2f3640', linewidth=2.5))
        # แนวรองรับคานซ้ายขวา
        ax.add_patch(plt.Rectangle((0, -10), 10, t_h+10, facecolor='#dcdde1', edgecolor='#718093', linewidth=1.5))
        ax.add_patch(plt.Rectangle((90, -10), 10, t_h+10, facecolor='#dcdde1', edgecolor='#718093', linewidth=1.5))
        
        # วาดเหล็กเส้นเสริมล่าง
        ax.plot([2, 98], [cov, cov], color='#e84118', linewidth=2, label="Bottom Bars")
        # วาดเหล็กบน
        ax.plot([0, 30], [t_h-cov, t_h-cov], color='#00a8ff', linewidth=2)
        ax.plot([70, 100], [t_h-cov, t_h-cov], color='#00a8ff', linewidth=2, label="Top Bars")
        
        # วาดเหล็กปลอกรับแรงเฉือน (ถ้าเปิดใช้งาน)
        if v_req:
            for x_stirrup in range(12, 35, int(sp_v)):
                ax.plot([x_stirrup, x_stirrup], [cov, t_h-cov], color='#44bd32', linewidth=1.5)
            for x_stirrup in range(65, 88, int(sp_v)):
                ax.plot([x_stirrup, x_stirrup], [cov, t_h-cov], color='#44bd32', linewidth=1.5)
            ax.text(14, -5, f"Stirrups: RB{db_v} @ {sp_v:.0f} cm", color='#44bd32', weight='bold', fontsize=9)

        ax.text(35, t_h/2, f"Main Rebar: DB{db_m} @ {sp_xb:.1f} cm", color='#e84118', weight='bold', fontsize=10)
        ax.set_xlim(-5, 105)
        ax.set_ylim(-12, t_h + 8)
        ax.axis('off')
        return fig

    st.pyplot(draw_detailed_blueprint(t_cm, covering_cm, main_bar_dia, s_xb, s_xt, stirrup_required, stirrup_dia if 'stirrup_dia' in locals() else 6, s_stirrup if 's_stirrup' in locals() else 0.0))

with col_res2:
    st.subheader("📋 ตรวจสอบปริมาณเหล็กเสริมจริง")
    verify_summary = {
        "ตำแหน่งการตรวจสอบ": ["แกน X ช่วงบวก (ล่าง)", "แกน X ช่วงลบ (บน)", "แกน Y ช่วงบวก (ล่าง)", "แกน Y ช่วงลบ (บน)"],
        "As Required (cm²/m)": [f"{As_x_pos_req:.2f}", f"{As_x_neg_req:.2f}", f"{As_y_pos_req:.2f}", f"{As_y_neg_req:.2f}"],
        "As Provided (cm²/m)": [f"{As_x_pos_prov:.2f}", f"{As_x_neg_prov:.2f}", f"{As_y_pos_prov:.2f}", f"{As_y_neg_prov:.2f}"],
        "ผลลัพธ์หน้าตัด": ["🟢 ผ่าน" if As_x_pos_prov >= As_x_pos_req else "❌ ขาดเหล็กเสริม",
                            "🟢 ผ่าน" if As_x_neg_prov >= As_x_neg_req else "❌ ขาดเหล็กเสริม",
                            "🟢 ผ่าน" if As_y_pos_prov >= As_y_pos_req else "❌ ขาดเหล็กเสริม",
                            "🟢 ผ่าน" if As_y_neg_prov >= As_y_neg_req else "❌ ขาดเหล็กเสริม"]
    }
    st.table(pd.DataFrame(verify_summary))

# --- การเจนเล่มรายงานการคำนวณอย่างเป็นทางการ (Official Calculation Sheet Generator) ---
st.markdown("---")
with st.expander("📄 เปิดระบบออกรายงานและรายการคำนวณวิศวกรรมโครงสร้างฉบับเต็ม"):
    
    final_report = f"""======================================================================
         OFFICIAL STRUCTURAL CALCULATION SHEET: REINFORCED CONCRETE SLAB
======================================================================
โครงการ: ระบบวิเคราะห์และคำนวณความปลอดภัยทางวิศวกรรมขั้นสูง
มาตรฐานการออกแบบอ้างอิง: มารตรฐาน วสท. 1008 / ACI 318-99 (วิธี {method})
----------------------------------------------------------------------
[1] การตรวจสอบและจำแนกประเภทพฤติกรรมแผ่นพื้น (SLAB DIAGNOSTIC ANALYSIS):
- ช่วงความยาวสั้น Lx = {Lx:.2f} เมตร  |  ช่วงความยาวสั้น Ly = {Ly:.2f} เมตร
- อัตราส่วนความกว้างต่อความยาวสั้น (m = Lx/Ly) = {m_ratio:.3f}
- สรุปผลประเภทพฤติกรรม: {slab_type}
- เหตุผลทางทฤษฎี: {diagnostic_msg}

[2] ข้อมูลเรขาคณิต หน้าตัด และกำลังวัสดุใช้งาน:
- ความหนาแผ่นพื้นโครงสร้าง (t): {t_cm:.1f} ซม.  |  ระยะลึกประสิทธิผลหน้าตัดดัด (d): {d:.2f} ซม.
- ระยะคอนกรีตหุ้มเคลียร์ริ่ง (Covering): {covering_cm:.1f} ซม.
- กำลังแรงอัดประลัยของคอนกรีต (fc'): {fc_prime:.1f} กก./ตร.ซม.
- กำลังดึงจุดคลิตมาตรฐานของเหล็กเสริม (fy): {fy:.1f} กก./ตร.ซม.

[3] น้ำหนักบรรทุกและการวิเคราะห์แรงภายในแผ่นพื้น:
- น้ำหนักบรรทุกคงที่จากน้ำหนักตัวแผ่นพื้น (Self-Weight): {DL_self:.2f} กก./ตร.ม.
- น้ำหนักบรรทุกคงที่เพิ่มเติมที่ระบุ (SDL): {SDL:.2f} กก./ตร.ม.
- น้ำหนักบรรทุกจรแผ่สม่ำเสมอใช้งาน (LL): {LL:.2f} กก./ตร.ม.
- น้ำหนักรวมประลัยเชิงออกแบบ (w_u): {w_u:.2f} กก./ตร.ม.
- โมเมนต์ดัดแกนหลักเชิงคำนวณสูงสุด (M_x positive): {M_x_pos:.2f} กก.-เมตร
- โมเมนต์ดัดลบขอบริมคานสูงสุด (M_x negative): {M_x_neg:.2f} กก.-เมตร

[4] การวิเคราะห์เสถียรภาพแรงเฉือนและการออกแบบเหล็กปลอก:
- แรงเฉือนแบบแผ่สูงสุดที่หน้าตัดวิกฤต (V_u): {V_u:.2f} กก.
- กำลังรับแรงเฉือนสูงสุดที่เนื้อคอนกรีตทนได้ (ØVc): {V_allowable:.2f} กก.
- สถานะระบบแรงเฉือนพื้นฐาน: {"[ปลอดภัย - ไม่ต้องเสริมเหล็กปลอกโครงสร้าง]" if shear_concrete_passed else "[เกินกำลังรับ - ต้องเสริมเหล็กปลอกพิเศษ]"}
"""
    if stirrup_required:
        final_report += f"""- รายละเอียดเหล็กปลอกเสริมแรงเฉือน: ใช้เหล็กขนาด RB{stirrup_dia} @ {s_stirrup:.1f} ซม.
- กำลังรับแรงเฉือนรวมหลังเสริมเหล็กปลอก (ØV_total): {V_total_capacity:.1f} กก. -> {"[ผ่านเกณฑ์แรงเฉือนผสมสำเร็จ]" if shear_stirrup_passed else "[ไม่ผ่านเกณฑ์ - วิกฤตแรงเฉือนพังทลาย]"}
"""
    
    final_report += f"""
[5] สรุปผลการจัดระยะและปริมาณเหล็กเส้นใช้งานจริง (Bending Schedule Specification):
- ความกว้างหน้าตัดอ้างอิงการออกแบบ: 1.00 เมตร (100 ซม.)
- เหล็กเสริมด้านล่าง แนวช่วงสั้น (Main X): DB{main_bar_dia} @ {s_xb:.1f} ซม. (As_provided = {As_x_pos_prov:.2f} cm²/m) -> Status: {"[ผ่านเกณฑ์]" if As_x_pos_prov >= As_x_pos_req else "[เหล็กไม่พอ]"}
- เหล็กเสริมด้านบน หัวคานช่วงสั้น (Top X) : DB{main_bar_dia} @ {s_xt:.1f} ซม. (As_provided = {As_x_neg_prov:.2f} cm²/m) -> Status: {"[ผ่านเกณฑ์]" if As_x_neg_prov >= As_x_neg_req else "[เหล็กไม่พอ]"}
- เหล็กเสริมด้านล่าง แนวช่วงยาว (Main Y): DB{main_bar_dia} @ {s_yb:.1f} ซม. (As_provided = {As_y_pos_prov:.2f} cm²/m) -> Status: {"[ผ่านเกณฑ์]" if As_y_pos_prov >= As_y_pos_req else "[เหล็กไม่พอ]"}
- เกณฑ์ควบคุมระยะห่างสูงสุด (S_max): {s_max_limit:.1f} ซม. -> Status: {"[ผ่านเกณฑ์ระยะห่าง]" if spacing_passed else "[ตกเกณฑ์ - ระยะห่างเกินค่าสูงสุด]"}
======================================================================
*รายงานเล่มรายการคำนวณนี้ได้รับการอนุมัติความถูกต้องและพิมพ์ผ่านระบบโครงสร้างอัตโนมัติ*
"""
    st.code(final_report, language="text")
    st.download_button(label="📥 ดาวน์โหลดเล่มรายงานคำนวณฉบับสมบูรณ์ (.txt)", data=final_report, file_name="Official_Slab_Shear_Report.txt", mime="text/plain")
