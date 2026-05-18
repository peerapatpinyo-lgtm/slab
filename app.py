import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# 1. ตั้งค่าหน้าเว็บให้รองรับการทำงานระดับสูง
st.set_page_config(page_title="Ultimate RC Slab Designer", layout="wide")

st.title("🚀 Ultimate RC Slab Designer (Enterprise Edition)")
st.caption("ระบบคำนวณ ตรวจสอบ และเขียนแบบรายละเอียดแผ่นพื้น ค.ส.ล. ตามมาตรฐานสากล")

# ใช้ระบบ Session State สำหรับเก็บรายงานคำนวณไว้ดาวน์โหลด
if 'report_text' not in st.session_state:
    st.session_state.report_text = ""

# 2. ส่วนป้อนข้อมูล (Input Panels) แยกเป็นคอลัมน์เพื่อความสะอาดตา
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    st.subheader("📐 มิติและระยะช่วง")
    Lx = st.number_input("ความยาวช่วงสั้น Lx (เมตร)", min_value=0.5, max_value=10.0, value=3.0, step=0.1)
    Ly = st.number_input("ความยาวช่วงยาว Ly (เมตร)", min_value=0.5, max_value=20.0, value=4.0, step=0.1)
    t_cm = st.slider("ความหนาพื้น t (เซนติเมตร)", min_value=5.0, max_value=30.0, value=12.0, step=0.5)
    covering_cm = st.number_input("ระยะหุ้มคอนกรีต (เซนติเมตร)", min_value=1.5, max_value=5.0, value=2.0, step=0.5)

with col_in2:
    st.subheader("⚖️ น้ำหนักและวิธีออกแบบ")
    SDL = st.number_input("น้ำหนักบรรทุกคงที่เพิ่มเติ่ม (กก./ตร.ม.)", min_value=0, max_value=500, value=100)
    LL = st.number_input("น้ำหนักบรรทุกจร (กก./ตร.ม.)", min_value=0, max_value=2000, value=200)
    method = st.selectbox("ระเบียบวิธีออกแบบ", ["วิธีวิเคราะห์กำลัง (SDM / USD)", "วิธีหน่วยแรงใช้งาน (WSD)"])

with col_in3:
    st.subheader("🛠️ คุณสมบัติวัสดุ")
    fc_prime = st.number_input("กำลังอัดคอนกรีต fc' (กก./ตร.ซม.)", min_value=140, max_value=450, value=240)
    fy = st.selectbox("กำลังดึงจุดคลิตเหล็กเสริม fy (กก./ตร.ซม.)", options=[2400, 3000, 4000], index=2)
    rebar_option = st.selectbox("ขนาดเหล็กที่ใช้หน้างาน", ["RB6", "RB9", "DB12", "DB16"], index=2)

# --- ส่วนประมวลผลทางวิศวกรรม (Engineering Core) ---
aspect_ratio = Ly / Lx if Lx > 0 else 0
is_one_way = aspect_ratio > 2.0
slab_type_str = "One-Way Slab" if is_one_way else "Two-Way Slab"

t = t_cm / 100
db_map = {"RB6": 6, "RB9": 9, "DB12": 12, "DB16": 16}
db = db_map[rebar_option]
ab = (math.pi / 4) * ((db / 10) ** 2) # Area of 1 bar in cm^2
d = t_cm - covering_cm - (db / 20)   # Effective depth (cm)

# คำนวณโหลดตามวิธีที่เลือก
DL_slab = t * 2400
w_dead = DL_slab + SDL
if method == "วิธีวิเคราะห์กำลัง (SDM / USD)":
    w_u = (1.2 * w_dead) + (1.6 * LL)
    phi_flexure = 0.90
    phi_shear = 0.75
else:
    w_u = w_dead + LL

# คำนวณโมเมนต์และแรงเฉือนสูงสุด (Worst-case Envelope สำหรับงานใช้งานจริง)
# คิดแบบต่อเนื่องปลายเปิดทั่วไปเพื่อให้ครอบคลุมความปลอดภัยสูงสุด
if is_one_way:
    M_pos = (w_u * (Lx ** 2)) / 11
    M_neg = (w_u * (Lx ** 2)) / 10
    V_u = (w_u * Lx) / 2 # แรงเฉือนสูงสุดที่ขอบคาน
    M_x_pos, M_x_neg, M_y_pos, M_y_neg = M_pos, M_neg, 0.0, 0.0
else:
    # สัมประสิทธิ์โมเมนต์เฉลี่ยสำหรับพื้นสองทางต่อเนื่องทั่วไป (Case 3/4 ACI)
    M_x_pos = 0.036 * w_u * (Lx ** 2)
    M_x_neg = 0.048 * w_u * (Lx ** 2)
    M_y_pos = 0.028 * w_u * (Lx ** 2)
    M_y_neg = 0.037 * w_u * (Lx ** 2)
    V_u = (w_u * Lx) / 3 # แรงเฉือนเฉลี่ยด้านสั้นที่รับโหลดมากสุด

# ฟังก์ชันคำนวณพื้นที่เหล็กเสริม (As)
def calc_as(M_kgm, d_eff, f_c, f_y, mth):
    if M_kgm <= 0: return 0.0
    M_cm = M_kgm * 100.0
    if mth == "วิธีวิเคราะห์กำลัง (SDM / USD)":
        Rn = M_cm / (0.90 * 100.0 * (d_eff ** 2))
        inside = 1.0 - (2.0 * Rn) / (0.85 * f_c)
        if inside < 0: return -1.0 # ความหนาไม่พอ
        rho = (0.85 * f_c / f_y) * (1.0 - math.sqrt(inside))
        return rho * 100.0 * d_eff
    else: # WSD
        fc_wsd = 0.375 * f_c
        fs_wsd = 1500.0 if f_y >= 3000 else 1200.0
        n_ratio = 11.0
        k_val = n_ratio / (n_ratio + (fs_wsd / fc_wsd))
        j_val = 1.0 - (k_val / 3.0)
        R_val = 0.5 * fc_wsd * k_val * j_val
        if d_eff < math.sqrt(M_cm / (R_val * 100.0)): return -1.0
        return M_cm / (fs_wsd * j_val * d_eff)

# คำนวณเหล็กขั้นต่ำกันร้าว
as_min_ratio = 0.0018 if fy >= 4000 else 0.0020
As_min = as_min_ratio * 100.0 * t_cm

# สรุปปริมาณเหล็กเสริมที่ต้องใช้จริง
error_concrete = False
if is_one_way:
    as_x_p = calc_as(M_x_pos, d, fc_prime, fy, method)
    as_x_n = calc_as(M_x_neg, d, fc_prime, fy, method)
    if as_x_p < 0 or as_x_n < 0: error_concrete = True
    As_X_Bottom = max(as_x_p, As_min)
    As_X_Top = max(as_x_n, As_min)
    As_Y_Bottom = As_min # เหล็กอุณหภูมิ
    As_Y_Top = 0.0
else:
    as_x_p = calc_as(M_x_pos, d, fc_prime, fy, method)
    as_x_n = calc_as(M_x_neg, d, fc_prime, fy, method)
    as_y_p = calc_as(M_y_pos, d, fc_prime, fy, method)
    as_y_n = calc_as(M_y_neg, d, fc_prime, fy, method)
    if any(v < 0 for v in [as_x_p, as_x_n, as_y_p, as_y_n]): error_concrete = True
    As_X_Bottom = max(as_x_p, As_min)
    As_X_Top = max(as_x_n, As_min)
    As_Y_Bottom = max(as_y_p, As_min)
    As_Y_Top = max(as_y_n, As_min)

# ฟังก์ชันคำนวณระยะห่างหน้างาน
def calc_spacing(as_req, bar_area, t_thickness):
    if as_req <= 0: return 0.0
    s = (bar_area / as_req) * 100.0
    return min(s, 3 * t_thickness, 45.0)

s_xb = calc_spacing(As_X_Bottom, ab, t_cm)
s_xt = calc_spacing(As_X_Top, ab, t_cm)
s_yb = calc_spacing(As_Y_Bottom, ab, t_cm)
s_yt = calc_spacing(As_Y_Top, ab, t_cm)

# --- การตรวจสอบแรงเฉือนเชิงโครงสร้าง (Shear Capacity Verification) ---
if method == "วิธีวิเคราะห์กำลัง (SDM / USD)":
    Vc = 0.53 * math.sqrt(fc_prime) * 100.0 * d # หน่วยเป็นกิโลกรัม
    V_allowable = phi_shear * Vc
else:
    vc = 0.29 * math.sqrt(fc_prime)
    V_allowable = vc * 100.0 * d

shear_passed = V_u <= V_allowable

# --- ส่วนการสร้างรูปภาพดีเทลหน้าตัดเหล็กเสริม (Matplotlib Sketch) ---
def draw_slab_section(t_h, cov, d_bar, sp_xb, sp_xt):
    fig, ax = plt.subplots(figsize=(10, 3))
    # วาดก้อนคอนกรีตพื้น
    ax.add_patch(plt.Rectangle((0, 0), 100, t_h, facecolor='#eaeaea', edgecolor='#7f8c8d', linewidth=2))
    
    # วาดเหล็กล่าง (Bottom Bars) - จุดสีแดง
    for x in range(5, 100, int(sp_xb) if sp_xb > 0 else 20):
        ax.plot(x, cov + (d_bar/20), 'ro', markersize=8, label="Bottom Rebar" if x==5 else "")
    ax.plot([2, 98], [cov, cov], 'r-', linewidth=1.5) # เส้นโครงเหล็กล่าง
    
    # วาดเหล็กบน (Top Bars) - จุดสีน้ำเงิน (ถ้ามีโมเมนต์ลบ)
    if sp_xt > 0:
        for x in range(5, 100, int(sp_xt)):
            ax.plot(x, t_h - cov - (d_bar/20), 'bo', markersize=8, label="Top Rebar" if x==5 else "")
        ax.plot([2, 98], [t_h - cov, t_h - cov], 'b-', linewidth=1.5)
        
    ax.set_xlim(-5, 105)
    ax.set_ylim(-2, t_h + 5)
    ax.set_title(f"Cross-Section Detail (Width 1.00 m) / Thickness = {t_h} cm", fontsize=10, fontweight='bold')
    ax.axis('off')
    return fig

# --- ส่วนการแสดงผลส่วนหน้าเบราว์เซอร์ (Main Dashboard UI) ---
col_m1, col_m2 = st.columns([2, 1])

with col_m1:
    st.subheader("📊 ผลลัพธ์และการตรวจสอบความปลอดภัย")
    
    if error_concrete:
        st.error("🚨 วิกฤต: หน้าตัดคอนกรีตบางเกินไป (Over-reinforced failure risk)! ไม่สามารถคำนวณเหล็กเสริมได้ โปรดเพิ่มความหนาพื้นทันที")
    elif not shear_passed:
        st.error(f"🚨 วิกฤต: แผ่นพื้นพังทลายด้วยแรงเฉือน! แรงเฉือนที่เกิด {V_u:.1f} กก. เกินกว่าที่ยอมรับได้ {V_allowable:.1f} กก. (โปรดเพิ่มความหนาพื้นหรือเพิ่มกำลังอัดคอนกรีต)")
    else:
        st.success(f"✅ โครงสร้างปลอดภัยสมบูรณ์: ความหนาและกำลังวัสดุผ่านการตรวจสอบทั้งแรงดัดและแรงเฉือน (V_u = {V_u:.1f} kg ≤ Allowable = {V_allowable:.1f} kg)")
        
        # แสดงรูปภาพแบบขยายหน้าตัดเหล็กเสริมจริง
        st.write("📐 **แบบขยายการจัดเรียงเหล็กเส้นหน้างาน (Section Sketch):**")
        fig_section = draw_slab_section(t_cm, covering_cm, db, s_xb, s_xt)
        st.pyplot(fig_section)

with col_m2:
    st.subheader("🎯 สรุปใบสั่งใบจัดเหล็ก")
    
    summary_data = {
        "ตำแหน่งเหล็ก": ["เหล็กล่าง แนวช่วงสั้น (Main X)", "เหล็กบน หัวคานช่วงสั้น (Top X)", "เหล็กล่าง แนวช่วงยาว (Main Y)", "เหล็กบน หัวคานช่วงยาว (Top Y)"],
        "ขนาดและระยะห่าง": [
            f"{rebar_option} @ {s_xb:.1f} ซม." if s_xb > 0 else "เหล็กกันร้าวขั้นต่ำ",
            f"{rebar_option} @ {s_xt:.1f} ซม." if s_xt > 0 else "ไม่ต้องมีเหล็กโครงสร้าง",
            f"{rebar_option} @ {s_yb:.1f} ซม." if s_yb > 0 else "เหล็กกันร้าวขั้นต่ำ",
            f"{rebar_option} @ {s_yt:.1f} ซม." if s_yt > 0 else "ไม่ต้องมีเหล็กโครงสร้าง"
        ]
    }
    st.table(pd.DataFrame(summary_data))

# --- ระบบสร้างเล่มรายงานคำนวณอัตโนมัติ (Automated Report Generator) ---
st.markdown("---")
with st.expander("📄 เปิดระบบออกรายงานการคำนวณ (Calculation Sheet Report)"):
    
    report = f"""==================================================
CALCULATION SHEET: REINFORCED CONCRETE SLAB DESIGN
==================================================
ประเภทพฤติกรรมแผ่นพื้น: {slab_type_str}
ระเบียบวิธีการคำนวณ: {method}
--------------------------------------------------
[1] ข้อมูลทางเรขาคณิตและวัสดุ:
- มิติตัวแผ่นพื้น: Lx = {Lx:.2f} ม. , Ly = {Ly:.2f} ม.
- ความหนาพื้น (t): {t_cm:.1f} ซม. (d_eff = {d:.2f} ซม.)
- กำลังอัดคอนกรีต (fc'): {fc_prime} กก./ตร.ซม.
- กำลังดึงเหล็กเสริม (fy): {fy} กก./ตร.ซม.

[2] การวิเคราะห์น้ำหนักบรรทุกและแรงภายใน:
- น้ำหนักบรรทุกรวม (w_u): {w_u:.2f} กก./ตร.ม.
- โมเมนต์ดัดบวกสูงสุด: {M_x_pos:.2f} กก.-ม.
- โมเมนต์ดัดลบสูงสุด: {M_x_neg:.2f} กก.-ม.
- แรงเฉือนสูงสุดที่เกิดขึ้น (V_u): {V_u:.2f} กก.
- แรงเฉือนที่หน้าตัดรับได้คุ้มครองความปลอดภัย: {V_allowable:.2f} กก. -> {"[PASSED]" if shear_passed else "[FAILED]"}

[3] สรุปผลการจัดเหล็กเสริมใช้งานจริง (ต่อความกว้าง 1 เมตร):
- เหล็กล่าง แนวช่วงสั้น (Main X): {rebar_option} @ {s_xb:.1f} ซม. (As = {As_X_Bottom:.2f} sq.cm)
- เหล็กบน หัวคานช่วงสั้น (Top X) : {rebar_option} @ {s_xt:.1f} ซม. (As = {As_X_Top:.2f} sq.cm)
- เหล็กล่าง แนวช่วงยาว (Main Y): {rebar_option} @ {s_yb:.1f} ซม. (As = {As_Y_Bottom:.2f} sq.cm)
- เหล็กบน หัวคานช่วงยาว (Top Y) : {rebar_option} @ {s_yt:.1f} ซม. (As = {As_Y_Top:.2f} sq.cm)
==================================================
"""
    st.code(report, language="text")
    st.download_button(label="📥 ดาวน์โหลดเล่มรายการคำนวณ (.txt)", data=report, file_name="Slab_Design_Report.txt", mime="text/plain")
