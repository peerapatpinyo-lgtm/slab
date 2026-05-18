import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# 1. การตั้งค่าหน้าจอและ Theme สไตล์ซอฟต์แวร์วิศวกรรม
st.set_page_config(page_title="SlabMaster Pro - Advanced RC Slab Designer", layout="wide")
st.title("🦅 SlabMaster Pro (Ultimate Industrial Edition)")
st.caption("ซอฟต์แวร์วิเคราะห์ ออกแบบ ถอดแบบวัสดุ และออกรายงานแผ่นพื้น ค.ส.ล. ตามมาตรฐาน ACI 318 และ วสท.")

# 2. ฟังก์ชันระบบจำลองสัมประสิทธิ์ ACI Method 3 แบบแยก Dead Load / Live Load (ตัวอย่างกรณี Interior & Edge Panels)
def get_aci_method3_coeffs(case, m_ratio):
    # โครงสร้างตาราง: { case: { m: (Cx_neg, Cx_pos_dl, Cx_pos_ll, Cy_neg, Cy_pos_dl, Cy_pos_ll) } }
    aci_table_m3 = {
        1: { # Case 1: ขอบอิสระรอบด้าน
            1.0: (0.000, 0.036, 0.036, 0.000, 0.036, 0.036),
            0.9: (0.000, 0.040, 0.044, 0.000, 0.031, 0.030),
            0.8: (0.000, 0.045, 0.053, 0.000, 0.025, 0.023),
            0.7: (0.000, 0.050, 0.064, 0.000, 0.020, 0.016),
            0.6: (0.000, 0.056, 0.075, 0.000, 0.014, 0.010),
            0.5: (0.000, 0.061, 0.086, 0.000, 0.009, 0.006)
        },
        2: { # Case 2: ต่อเนื่องกันทั้ง 4 ด้าน (Interior Panel)
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

# 3. การจัดวางหน้าต่างอินพุตด้วยระบบ Sidebar
st.sidebar.header("📐 มิติสัดส่วนอาคาร")
Lx = st.sidebar.number_input("ความยาวช่วงสั้น Lx (ม.)", min_value=1.0, max_value=12.0, value=4.0, step=0.1)
Ly = st.sidebar.number_input("ความยาวช่วงยาว Ly (ม.)", min_value=1.0, max_value=24.0, value=5.0, step=0.1)
t_cm = st.sidebar.slider("ความหนาแผ่นพื้น t (ซม.)", min_value=8.0, max_value=35.0, value=15.0, step=0.5)
covering_cm = st.sidebar.slider("ระยะหุ้มคอนกรีต (ซม.)", min_value=1.5, max_value=5.0, value=2.0, step=0.5)

st.sidebar.header("🛠️ กำลังวัสดุควบคุม")
method = st.sidebar.selectbox("ระเบียบวิธีออกแบบ", ["วิธีวิเคราะห์กำลัง (SDM / USD)", "วิธีหน่วยแรงใช้งาน (WSD)"])
fc_prime = st.sidebar.number_input("กำลังอัดคอนกรีต fc' (กก./ตร.ซม.)", min_value=140, max_value=450, value=280)
fy = st.sidebar.selectbox("กำลังดึงจุดคลิตเหล็กเสริมหลัก fy (กก./ตร.ซม.)", [2400, 3000, 4000], index=2)

st.sidebar.header("⚖️ น้ำหนักบรรทุกแยกประเภท")
SDL = st.sidebar.number_input("น้ำหนักคงที่เพิ่มเติม (Superimposed DL) (กก./ตร.ม.)", min_value=0, max_value=500, value=120)
LL = st.sidebar.number_input("น้ำหนักบรรทุกจรใช้งาน (Live Load) (กก./ตร.ม.)", min_value=0, max_value=1500, value=300)

st.sidebar.header("💰 ประมาณการต้นทุน")
unit_concrete_cost = st.sidebar.number_input("ราคาคอนกรีต (บาท/คิว)", value=2200)
unit_steel_cost = st.sidebar.number_input("ราคาเหล็กเสริม (บาท/กิโลกรัม)", value=28)

# --- แกนประมวลผลทางวิศวกรรมหลัก (Engineering Computation) ---
m_ratio = Lx / Ly if Ly > 0 else 0
is_one_way = m_ratio < 0.5
slab_type_str = "One-Way Slab" if is_one_way else "Two-Way Slab"

t = t_cm / 100
w_dl_self = t * 2400
w_dl_total = w_dl_self + SDL

# คำนวณโมเมนต์แยกตามทฤษฎีพฤติกรรมจริง
if is_one_way:
    if method == "วิธีวิเคราะห์กำลัง (SDM / USD)":
        w_u = (1.2 * w_dl_total) + (1.6 * LL)
    else:
        w_u = w_dl_total + LL
    M_x_pos = (w_u * (Lx ** 2)) / 11
    M_x_neg = (w_u * (Lx ** 2)) / 10
    M_y_pos = M_y_neg = 0.0
    V_u = (w_u * Lx) / 2
else:
    # คืนค่าจากตารางสัมประสิทธิ์แยกประเภทโหลดของ ACI Method 3
    case_select = 2 # สมมติเคส Interior Panel เป็นค่าหลัก
    cx_n, cx_p_dl, cx_p_ll, cy_n, cy_p_dl, cy_p_ll = get_aci_method3_coeffs(case_select, m_ratio)
    
    if method == "วิธีวิเคราะห์กำลัง (SDM / USD)":
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

# ตรวจสอบความหนาขั้นต่ำตามเกณฑ์ควบคุมการโก่งตัวของ ACI Code
if is_one_way:
    t_min_req = (Lx / 24) * (0.4 + fy/7000) * 100 # อ้างอิงกรณี One End Continuous
else:
    t_min_req = (2 * (Lx + Ly) / 180) * 100 # อ้างอิงเกณฑ์พื้นสองทางขอบต่อเนื่องทั่วไป
deflection_passed = t_cm >= t_min_req

# เลือกขนาดเหล็กและคำนวณพื้นที่
main_bar = st.selectbox("ระบุขนาดเหล็กเสริมใช้งานในระบบ:", [9, 12, 16], index=1, key="main_bar_select")
ab = (math.pi / 4) * ((main_bar / 10) ** 2)
d = t_cm - covering_cm - (main_bar / 20)

as_min_ratio = 0.0018 if fy >= 4000 else 0.0020
As_min = as_min_ratio * 100 * t_cm

def design_as(M, d_eff, fc, fy_g, mth):
    if M <= 0: return 0.0
    M_cm = M * 100
    if mth == "วิธีวิเคราะห์กำลัง (SDM / USD)":
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

# ส่วนเลือกป้อนระยะห่างหน้างานเองเพื่อควบคุมและตรวจสอบ (Manual Override)
st.markdown("### 🛠️ ปรับแต่งการจัดระยะพิทช์เหล็กเส้น (@ ซม.)")
col_ui1, col_ui2, col_ui3, col_ui4 = st.columns(4)
with col_ui1: s_xb = st.number_input("เหล็กล่าง แนว X (@ ซม.)", value=15.0, step=1.0)
with col_ui2: s_xt = st.number_input("เหล็กบน แนว X (@ ซม.)", value=15.0, step=1.0)
with col_ui3: s_yb = st.number_input("เหล็กล่าง แนว Y (@ ซม.)", value=20.0, step=1.0)
with col_ui4: s_yt = st.number_input("เหล็กบน แนว Y (@ ซม.)", value=20.0, step=1.0)

# คำนวณกลับเป็นพื้นที่เหล็กเสริมจริงหน้างาน (As Provided)
As_xb_prov = (ab / s_xb) * 100
As_xt_prov = (ab / s_xt) * 100
As_yb_prov = (ab / s_yb) * 100
As_yt_prov = (ab / s_yt) * 100 if s_yt > 0 else 0.0

# คำนวณปริมาณและน้ำหนักเหล็กเสริมรวมทั้งแผง (BOM Engine)
weight_per_meter = (math.pi / 4) * ((main_bar / 1000) ** 2) * 7850 # น้ำหนักเหล็กต่อเมตร (kg/m)
total_area = Lx * Ly
concrete_volume = total_area * t

# คิดความยาวเหล็กต่อตารางเมตรโดยประมาณ รวมระยะงอและระยะล้วง
steel_length_x = (100 / s_xb * Lx) + (100 / s_xt * Lx * 0.5) 
steel_length_y = (100 / s_yb * Ly) + (100 / s_yt * Ly * 0.5 if s_yt > 0 else 0)
total_steel_weight = (steel_length_x * Ly + steel_length_y * Lx) * weight_per_meter

cost_concrete = concrete_volume * unit_concrete_cost
cost_steel = total_steel_weight * unit_steel_cost
total_cost = cost_concrete + cost_steel

# --- ส่วนติดต่อผู้ใช้งานยุคใหม่ด้วยระบบแถบจัดการ (Tabs Workspace) ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 การตรวจสอบทางวิศวกรรม", "🎨 แบบขยายโครงสร้าง (Detailing)", "💰 รายการถอดแบบและมูลค่า (BOM)", "📑 เล่มคำนวณอย่างเป็นทางการ"])

with tab1:
    st.subheader("🚧 ตารางแสดงผลลัพธ์และความปลอดภัยเชิงโครงสร้าง")
    
    val_thickness = "🟢 ผ่านเกณฑ์การควบคุมการแอ่นตัว" if deflection_safe else f"⚠️ เสี่ยงแอ่นตัวในระยะยาว (ACI แนะนำหนาขั้นต่ำ {t_min_req:.1f} ซม.)"
    val_xb = "🟢 ผ่าน" if As_xb_prov >= As_xb_req else "🔴 ปริมาณเหล็กน้อยกว่าคำนวณ"
    val_xt = "🟢 ผ่าน" if As_xt_prov >= As_xt_req else "🔴 ปริมาณเหล็กน้อยกว่าคำนวณ"
    
    summary_df = pd.DataFrame({
        "เกณฑ์การตรวจสอบคุณภาพ": ["ความหนาควบคุมการโก่งตัว (Deflection Thickness)", "เหล็กเสริมล่างแกน X (Bottom Rebar X)", "เหล็กเสริมบนขอบริม X (Top Rebar X)"],
        "ค่าที่ต้องการตามมาตรฐาน": [f"≥ {t_min_req:.1f} ซม.", f"{As_xb_req:.2f} ตร.ซม./ม.", f"{As_xt_req:.2f} ตร.ซม./ม."],
        "ค่าที่ออกแบบจริงหน้างาน": [f"{t_cm:.1f} ซม.", f"{As_xb_prov:.2f} ตร.ซม./ม.", f"{As_xt_prov:.2f} ตร.ซม./ม."],
        "บทสรุปผล": [val_thickness, val_xb, val_xt]
    })
    st.table(summary_df)

with tab2:
    st.subheader("📐 แบบหล่อและรายละเอียดการผูกเหล็กเสริม (Engineering Sketch)")
    
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.add_patch(plt.Rectangle((10, 0), 80, t_cm, facecolor='#f1f2f6', edgecolor='#2f3542', linewidth=2, hatch='.'))
    # คานรับน้ำหนักด้านข้าง
    ax.add_patch(plt.Rectangle((0, -12), 10, t_cm+12, facecolor='#ced6e0', edgecolor='#57606f'))
    ax.add_patch(plt.Rectangle((90, -12), 10, t_cm+12, facecolor='#ced6e0', edgecolor='#57606f'))
    
    # พล็อตลายเส้นเหล็กเส้น
    ax.plot([2, 98], [covering_cm, covering_cm], color='#ff4757', linewidth=2.5, label='Main Rebar')
    ax.plot([0, 25], [t_cm-covering_cm, t_cm-covering_cm], color='#1e90ff', linewidth=2.5)
    ax.plot([75, 100], [t_cm-covering_cm, t_cm-covering_cm], color='#1e90ff', linewidth=2.5)
    
    ax.text(35, t_cm/2, f"DB{main_bar} @ {s_xb:.0f} cm", color='#ff4757', weight='bold')
    ax.set_xlim(-5, 105)
    ax.set_ylim(-15, t_cm + 10)
    ax.axis('off')
    st.pyplot(fig)

with tab3:
    st.subheader("📊 ใบสรุปรายการประมาณการปริมาณวัสดุและราคา (BOQ)")
    
    bom_df = pd.DataFrame({
        "รายการวัสดุ": ["คอนกรีตโครงสร้าง (Concrete Volume)", "เหล็กเสริมหลักทั้งหมด (Total Rebar Weight)", "รวมงบประมาณค่าวัสดุเบื้องต้น"],
        "ปริมาณคำนวณได้": [f"{concrete_volume:.2f} ลบ.ม. (คิว)", f"{total_steel_weight:.1f} กิโลกรัม (kg)", f"{total_cost:,.2f} บาท"],
        "หมายเหตุ": ["คิดตามปริมาตรรูปทรงเรขาคณิต", f"คำนวณรวมระยะล้วงเฉลี่ยจากพิกัด @ DB{main_bar}", "ไม่รวมค่าแรงและเศษสูญเสียหน้างาน"]
    })
    st.table(bom_df)

with tab4:
    st.subheader("📄 เอกสารรายงานผลคำนวณฉบับเป็นทางการสำหรับแนบขออนุญาต")
    
    official_txt = f"""======================================================================
               STRUCTURAL DESIGN & VERIFICATION REPORT (ACI 318)
======================================================================
ประเภทการกระจายแรงโครงสร้าง: {slab_type_str}
ระเบียบวิธีการวิเคราะห์โมเมนต์ดัด: มาตรฐานสากล ACI Method 3 (แยกสัดส่วนโหลดจริง)
----------------------------------------------------------------------
[1] ข้อมูลคุณสมบัติและการวินิจฉัยพฤติกรรม (Slab Diagnostics):
- ขนาดแผ่นพื้น: ช่วงสั้น Lx = {Lx:.2f} ม. | ช่วงยาว Ly = {Ly:.2f} ม.
- อัตราส่วนความกว้างเชิงโครงสร้าง (m) = {m_ratio:.2f} -> พฤติกรรมแบบ {slab_type_str}
- ความหนาที่ระบุใช้งาน: {t_cm:.1f} ซม.
- เกณฑ์ความหนาขั้นต่ำของมาตรฐานเพื่อป้องกันการแอ่นตัว (ACI Minimum Thickness): {t_min_req:.1f} ซม.
- บทสรุปด้านการแอ่นตัวในระยะยาว: {"[PASSED - ความหนาผ่านเกณฑ์ต้านการแอ่นตัว]" if deflection_safe else "[WARNING - ควรเพิ่มความหนาเพื่อลดการโก่งตัว]"}

[2] ข้อมูลน้ำหนักและการรวมโหลดเชิงวิศวกรรม (Load Combinations):
- น้ำหนักบรรทุกคงที่แผ่รวม (Dead Load + SDL): {w_dl_total:.2f} กก./ตร.ม.
- น้ำหนักบรรทุกจรใช้งาน (Live Load): {LL:.2f} กก./ตร.ม.
- น้ำหนักบรรทุกประลัยรวมกรณีวิเคราะห์ (w_u): {w_u:.2f} กก./ตร.ม.
- แรงบิดโมเมนต์ดัดประลัยสูงสุดแกนใช้งานหลัก (Mx Positive): {M_x_pos:.2f} กก.-ม.
- แรงบิดโมเมนต์ดัดลบตรงแนวหัวคานริม (Mx Negative): {M_x_neg:.2f} กก.-ม.

[3] สรุปผลการคำนวณและตรวจสอบปริมาณเหล็กเสริมจริง:
- หน้าตัดความกว้างวิเคราะห์อ้างอิง: 1.00 เมตร
- เหล็กล่าง แนวสั้น (Main Bottom X): DB{main_bar} @ {s_xb:.1f} ซม. [พื้นที่จริง: {As_xb_prov:.2f} / ที่ต้องการ: {As_xb_req:.2f} cm²/m] -> {"ผ่าน" if As_xb_prov >= As_xb_req else "ไม่ผ่าน"}
- เหล็กบน หัวคาน (Top Support X) : DB{main_bar} @ {s_xt:.1f} ซม. [พื้นที่จริง: {As_xt_prov:.2f} / ที่ต้องการ: {As_xt_req:.2f} cm²/m] -> {"ผ่าน" if As_xt_prov >= As_xt_req else "ไม่ผ่าน"}

[4] การถอดแบบประมาณราคาวัสดุขั้นต้น (BOM Summary):
- ปริมาตรเนื้อคอนกรีตสุทธิ: {concrete_volume:.2f} ลบ.ม.
- น้ำหนักเหล็กเส้นรวมโครงสร้าง: {total_steel_weight:.1f} กก.
======================================================================
"""
    st.code(official_txt, language="text")
    st.download_button(label="📥 ดาวน์โหลดเล่มรายการคำนวณและ BOQ (.txt)", data=official_txt, file_name="Ultimate_Slab_Report.txt", mime="text/plain")
