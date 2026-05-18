import streamlit as st
import math
import pandas as pd

# 1. ตั้งค่าหน้าเว็บหน้าตาแบบมืออาชีพ
st.set_page_config(page_title="Pro RC Slab Designer", layout="wide", initial_sidebar_state="expanded")

st.title("🏗️ โปรแกรมออกแบบแผ่นพื้น ค.ส.ล. ครบวงจร (Professional Edition)")
st.caption("คำนวณตามมาตรฐานวิศวกรรมสถานแห่งประเทศไทย (EIT) และ ACI Standard")

# 2. แถบด้านข้างสำหรับป้อนข้อมูล (Sidebar Input)
st.sidebar.header("📥 1. ข้อมูลทางเรขาคณิตและน้ำหนัก")
Lx = st.sidebar.number_input("ความยาวช่วงสั้น Lx (เมตร)", min_value=0.5, max_value=10.0, value=3.0, step=0.1)
Ly = st.sidebar.number_input("ความยาวช่วงยาว Ly (เมตร)", min_value=0.5, max_value=20.0, value=4.0, step=0.1)
t_cm = st.sidebar.slider("ความหนาของแผ่นพื้น t (เซนติเมตร)", min_value=5.0, max_value=30.0, value=12.0, step=0.5)
covering_cm = st.sidebar.number_input("ระยะคอนกรีตหุ้มเคลียร์ริ่ง (เซนติเมตร)", min_value=1.5, max_value=5.0, value=2.0, step=0.5)

st.sidebar.subheader("⚖️ น้ำหนักบรรทุก")
SDL = st.sidebar.number_input("น้ำหนักบรรทุกคงที่เพิ่มเติ่ม / วัสดุปูผิว (กก./ตร.ม.)", min_value=0, max_value=500, value=100)
LL = st.sidebar.number_input("น้ำหนักบรรทุกจร Live Load (กก./ตร.ม.)", min_value=0, max_value=2000, value=200)

st.sidebar.header("🛠️ 2. คุณสมบัติวัสดุและวิธีออกแบบ")
method = st.sidebar.selectbox("วิธีออกแบบ (Design Method)", ["วิธีวิเคราะห์กำลัง (SDM / USD)", "วิธีหน่วยแรงใช้งาน (WSD)"])
fc_prime = st.sidebar.number_input("กำลังอัดของคอนกรีตทรงกระบอก fc' (กก./ตร.ซม.)", min_value=140, max_value=450, value=240)
fy = st.sidebar.selectbox("กำลังรับแรงดึงที่จุดคลิตของเหล็กเสริม fy (กก./ตร.ซม.)", options=[2400, 3000, 4000], index=2)

# 3. ตรวจสอบประเภทแผ่นพื้นอัตโนมัติ
aspect_ratio = Ly / Lx if Lx > 0 else 0
slab_type = "One-Way Slab (พื้นทางเดียว)" if aspect_ratio > 2.0 else "Two-Way Slab (พื้นสองทาง)"

# 4. เลือกเงื่อนไขจุดรองรับตามประเภทพื้น
st.sidebar.header("📌 3. เงื่อนไขจุดรองรับ (Boundary Conditions)")
if aspect_ratio > 2.0:
    condition = st.sidebar.selectbox("สภาพขอบพื้นทางเดียว", [
        "Simply Supported (ปลายอิสระสองข้าง)",
        "One End Continuous (ต่อเนื่องปลายด้านเดียว)",
        "Both Ends Continuous (ต่อเนื่องทั้งสองด้าน)",
        "Cantilever (ยื่นอิสระ)"
    ])
else:
    condition = st.sidebar.selectbox("สภาพขอบพื้นสองทาง (กรณีทั่วไป)", [
        "Case 1: ปลายอิสระทั้ง 4 ด้าน (Isolated Slab)",
        "Case 2: ต่อเนื่องกันทั้ง 4 ด้าน (Interior Panel)",
        "Case 3: ต่อเนื่อง 3 ด้าน (Discontinuous 1 Short Edge)",
        "Case 4: ต่อเนื่อง 2 ด้านมุม (Discontinuous 2 Adjacent Edges)"
    ])

# --- ส่วนของการคำนวณหลัก (Engineering Engine) ---
t = t_cm / 100
d = t_cm - covering_cm - 0.6 # d โดยประมาณ (ลบระยะหุ้มและครึ่งหนึ่งของเส้นผ่านศูนย์กลางเหล็ก)
b_cm = 100.0 # คิดต่อความกว้าง 1 เมตร

# 4.1 คำนวณน้ำหนักบรรทุกแผ่ลงพื้น
DL_slab = t * 2400 # น้ำหนักคอนกรีตเสริมเหล็ก
w_dead = DL_slab + SDL

if method == "วิธีวิเคราะห์กำลัง (SDM / USD)":
    w_u = (1.2 * w_dead) + (1.6 * LL)
else: # WSD
    w_u = w_dead + LL

# 4.2 คำนวณโมเมนต์ดัดออกแบบสูงสุด (Design Moments)
M_pos, M_neg = 0.0, 0.0
M_x_pos, M_x_neg, M_y_pos, M_y_neg = 0.0, 0.0, 0.0, 0.0

if aspect_ratio > 2.0:
    # พฤติกรรมพื้นทางเดียว (คิดวิเคราะห์คล้ายคานกว้าง 1 เมตร)
    if "Simply Supported" in condition:
        M_pos = (w_u * (Lx ** 2)) / 8
    elif "One End Continuous" in condition:
        M_pos = (w_u * (Lx ** 2)) / 11
        M_neg = (w_u * (Lx ** 2)) / 10
    elif "Both Ends Continuous" in condition:
        M_pos = (w_u * (Lx ** 2)) / 16
        M_neg = (w_u * (Lx ** 2)) / 11
    else: # Cantilever
        M_neg = (w_u * (Lx ** 2)) / 2
else:
    # พฤติกรรมพื้นสองทาง (ใช้สัมประสิทธิ์โมเมนต์แบบจำลองตัวคูณอย่างง่ายเพื่อความเสถียร)
    m_ratio = Lx / Ly
    if "Case 1" in condition: # ปลายอิสระทั้งหมด
        C_x_pos, C_y_pos = 0.050, 0.035
        C_x_neg, C_y_neg = 0.000, 0.000
    elif "Case 2" in condition: # ต่อเนื่องทุกด้าน
        C_x_pos, C_y_pos = 0.018, 0.015
        C_x_neg, C_y_neg = 0.033, 0.025
    elif "Case 3" in condition:
        C_x_pos, C_y_pos = 0.028, 0.020
        C_x_neg, C_y_neg = 0.040, 0.030
    else: # Case 4 มุมต่อเนื่อง
        C_x_pos, C_y_pos = 0.035, 0.025
        C_x_neg, C_y_neg = 0.045, 0.035
        
    M_x_pos = C_x_pos * w_u * (Lx ** 2)
    M_x_neg = C_x_neg * w_u * (Lx ** 2)
    M_y_pos = C_y_pos * w_u * (Lx ** 2)
    M_y_neg = C_y_neg * w_u * (Lx ** 2)

# 4.3 ฟังก์ชันคำนวณพื้นที่เหล็กเสริม (As)
def calculate_As_required(M_kgm, design_method, f_c, f_y, d_eff):
    if M_kgm <= 0:
        return 0.0
    M_kgcm = M_kgm * 100.0
    if design_method == "วิธีวิเคราะห์กำลัง (SDM / USD)":
        phi = 0.90
        # Check depth sufficiency
        Rn = M_kgcm / (phi * 100.0 * (d_eff ** 2))
        inside_sqrt = 1.0 - (2.0 * Rn) / (0.85 * f_c)
        if inside_sqrt < 0:
            return -1.0 # Section inadequate
        rho = (0.85 * f_c / f_y) * (1.0 - math.sqrt(inside_sqrt))
        return rho * 100.0 * d_eff
    else: # WSD
        f_concrete = 0.375 * f_c
        f_steel = 1500.0 if f_y >= 3000 else 1200.0
        n_ratio = 11.0
        k_val = n_ratio / (n_ratio + (f_steel / f_concrete))
        j_val = 1.0 - (k_val / 3.0)
        R_val = 0.5 * f_concrete * k_val * j_val
        d_req = math.sqrt(M_kgcm / (R_val * 100.0))
        if d_eff < d_req:
            return -1.0
        return M_kgcm / (f_steel * j_val * d_eff)

# คำนวณหาเหล็กเสริมกันร้าวขั้นต่ำ (Shrinkage Steel)
as_min_ratio = 0.0018 if fy >= 4000 else 0.0020
As_min = as_min_ratio * 100.0 * t_cm

# แปลงผลลัพธ์คำนวณออกแยกตามเคสพื้น
error_flag = False
if aspect_ratio > 2.0:
    As_pos_req = calculate_As_required(M_pos, method, fc_prime, fy, d)
    As_neg_req = calculate_As_required(M_neg, method, fc_prime, fy, d)
    if As_pos_req < 0 or As_neg_req < 0: error_flag = True
    As_x_pos = max(As_pos_req, As_min)
    As_x_neg = max(As_neg_req, As_min)
    As_y_pos = As_min # พื้นทางเดียวเหล็กทิศทางยาวคือเหล็กกันร้าว
    As_y_neg = 0.0
else:
    As_x_pos_req = calculate_As_required(M_x_pos, method, fc_prime, fy, d)
    As_x_neg_req = calculate_As_required(M_x_neg, method, fc_prime, fy, d)
    As_y_pos_req = calculate_As_required(M_y_pos, method, fc_prime, fy, d)
    As_y_neg_req = calculate_As_required(M_y_neg, method, fc_prime, fy, d)
    if any(v < 0 for v in [As_x_pos_req, As_x_neg_req, As_y_pos_req, As_y_neg_req]): error_flag = True
    As_x_pos = max(As_x_pos_req, As_min)
    As_x_neg = max(As_x_neg_req, As_min)
    As_y_pos = max(As_y_pos_req, As_min)
    As_y_neg = max(As_y_neg_req, As_min)

# --- ส่วนการแสดงผลส่วนหน้าจอหลัก (Main UI) ---
tab1, tab2, tab3 = st.tabs(["📊 สรุปผลการวิเคราะห์โครงสร้าง", "🦾 รายละเอียดการเสริมเหล็ก", "📐 ข้อกำหนดตามมาตรฐานวิศวกรรม"])

with tab1:
    st.header("📉 ข้อมูลพฤติกรรมโครงสร้าง")
    c1, c2, c3 = st.columns(3)
    c1.metric("ประเภทแผ่นพื้นแนะแนว", slab_type)
    c2.metric("อัตราส่วนช่วงพื้น (Ly / Lx)", f"{aspect_ratio:.2f}")
    c3.metric("น้ำหนักแผ่ออกแบบรวม (w)", f"{w_u:.2f} กก./ตร.ม.")

    st.markdown("---")
    st.subheader("📌 ค่าโมเมนต์ดัดสูงสุดที่เกิดขึ้นบนแผ่นพื้น")
    
    if aspect_ratio > 2.0:
        cc1, cc2 = st.columns(2)
        cc1.metric("โมเมนต์บวกสูงสุด (กลางช่วง)", f"{M_pos:.2f} กก.-ม.")
        cc2.metric("โมเมนต์ลบสูงสุด (ที่ขอบ)", f"{M_neg:.2f} กก.-ม.")
    else:
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric("Mx (+) กลางช่วงสั้น", f"{M_x_pos:.2f} กก.-ม.")
        cc2.metric("Mx (-) ขอบช่วงสั้น", f"{M_x_neg:.2f} กก.-ม.")
        cc3.metric("My (+) กลางช่วงยาว", f"{M_y_pos:.2f} กก.-ม.")
        cc4.metric("My (-) ขอบช่วงยาว", f"{M_y_neg:.2f} กก.-ม.")

with tab2:
    st.header("🛠️ แนะนำการจัดระยะเหล็กเสริมจริง")
    if error_flag:
        st.error("❌ ข้อผิดพลาด: หน้าตัดคอนกรีตบางเกินไป ไม่สามารถรับโมเมนต์ดัดฝืนนี้ได้! โปรดกลับไปเพิ่มความหนาของแผ่นพื้น (t) ที่แถบเมนูด้านซ้าย")
    else:
        rebar_option = st.selectbox("เลือกขนาดเส้นผ่านศูนย์กลางเหล็กเสริมหลักที่จะใช้งานหน้างาน", ["RB6 (เหล็กผิวเรียบ)", "RB9 (เหล็กผิวเรียบ)", "DB12 (เหล็กข้ออ้อย)", "DB16 (เหล็กข้ออ้อย)"])
        db_map = {"RB6 (เหล็กผิวเรียบ)": 6, "RB9 (เหล็กผิวเรียบ)": 9, "DB12 (เหล็กข้ออ้อย)": 12, "DB16 (เหล็กข้ออ้อย)": 16}
        db = db_map[rebar_option]
        ab = (math.pi / 4) * ((db / 10) ** 2) # พื้นที่หน้าตัดเหล็ก 1 เส้น (ตร.ซม.)

        def get_spacing(as_target, bar_area, slab_thick):
            if as_target <= 0: return "ไม่ต้องเสริมเหล็กโครงสร้าง"
            s = (bar_area / as_target) * 100.0
            s_max = min(3 * slab_thick, 45.0) # เกณฑ์ระยะห่างมากสุดตามมาตรฐานสยท.
            return f"@ {min(s, s_max):.1f} ซม."

        # ตารางสรุปรายการเสริมเหล็ก
        st.subheader("📋 ตารางระยะจัดเหล็กเสริมจริง (คิดต่อความกว้างพื้น 1 เมตร)")
        
        if aspect_ratio > 2.0:
            data = {
                "ตำแหน่งเหล็กเสริม": ["เหล็กเสริมหลักกลางช่วงพื้น (+)", "เหล็กเสริมพิเศษรับโมเมนต์ลบที่คาน (-)", "เหล็กเสริมอุณหภูมิทิศทางยาว (กันร้าว)"],
                "พื้นที่เหล็กที่ต้องการ (ตร.ซม./ม.)": [f"{As_x_pos:.2f}", f"{As_x_neg:.2f}", f"{As_y_pos:.2f}"],
                "ระยะจัดทำหน้างาน": [get_spacing(As_x_pos, ab, t_cm), get_spacing(As_x_neg, ab, t_cm), get_spacing(As_y_pos, ab, t_cm)]
            }
        else:
            data = {
                "ตำแหน่งเหล็กเสริม": [
                    "ทิศทางสั้น Lx: เหล็กล่างกลางช่วง (+)", 
                    "ทิศทางสั้น Lx: เหล็กบนหัวคาน (-)", 
                    "ทิศทางยาว Ly: เหล็กล่างกลางช่วง (+)", 
                    "ทิศทางยาว Ly: เหล็กบนหัวคาน (-)"
                ],
                "พื้นที่เหล็กที่ต้องการ (ตร.ซม./ม.)": [f"{As_x_pos:.2f}", f"{As_x_neg:.2f}", f"{As_y_pos:.2f}", f"{As_y_neg:.2f}"],
                "ระยะจัดทำหน้างาน": [
                    get_spacing(As_x_pos, ab, t_cm), 
                    get_spacing(As_x_neg, ab, t_cm), 
                    get_spacing(As_y_pos, ab, t_cm), 
                    get_spacing(As_y_neg, ab, t_cm)
                ]
            }
            
        df = pd.DataFrame(data)
        st.table(df)
        
        st.markdown("""
        <div style="background-color:#fff3cd; padding:15px; border-radius:8px; border-left: 6px solid #ffc107; color: #856404;">
            ⚠️ <b>ข้อแนะนำหน้างานวิศวกรรม:</b> ระยะห่างห้ามเกิน <b>45 ซม.</b> หรือ <b>3 เท่าของความหนาพื้น</b> และควรกระจายเหล็กให้สม่ำเสมอ สำหรับเหล็กบนหัวคานให้ดัดตะขอปลายนึกยึดลงในคานให้แน่นหนา
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.header("📐 การตรวจสอบความหนาขั้นต่ำเพื่อควบคุมการโก่งตัว")
    
    # คำนวณความหนาขั้นต่ำตามเกณฑ์สยท./ACI โดยไม่ต้องคำนวณการโก่งตัวจริง
    if aspect_ratio > 2.0:
        if "Simply Supported" in condition: t_min = Lx / 20
        elif "One End Continuous" in condition: t_min = Lx / 24
        elif "Both Ends Continuous" in condition: t_min = Lx / 28
        else: t_min = Lx / 10 # Cantilever
    else:
        t_min = (2 * (Lx + Ly)) / 180 # สูตรประมาณการพื้นสองทางอย่างง่ายสากล
        
    t_min_cm = t_min * 100
    
    st.write(f"- มาตรฐานกำหนดความหนาขั้นต่ำสำหรับกรณีนี้: **{t_min_cm:.1f} ซม.**")
    st.write(f"- ความหนาของแผ่นพื้นที่ระบุในระบบปัจจุบัน: **{t_cm:.1f} ซม.**")
    
    if t_cm >= t_min_cm:
        st.success("✔️ ความหนาพื้นผ่านเกณฑ์มาตรฐานควบคุมการโก่งตัวเชิงโครงสร้าง (ไม่ต้องทดสอบการโก่งเพิ่ม)")
    else:
        st.warning("⚠️ ความหนาพื้นน้อยกว่าที่เกณฑ์แนะนำ อาจเกิดปัญหาแอ่นตัวในระยะยาวได้ ควรพิจารณาเพิ่มความหนาพื้นหรือปรึกษาวิศวกรโครงสร้างอาวุโส")

    # ส่วนสรุปตัวเลขทางทฤษฎีเพิ่มเติม
    with st.expander("🛠️ ตัวแปรคงที่ทางวิศวกรรมที่ใช้ในระบบ"):
        st.write(f"• น้ำหนักบรรทุกคงที่ตัวแผ่นพื้นเอง (Slab Self-Weight): {DL_slab:.2f} กก./ตร.ม.")
        st.write(f"• พื้นที่เหล็กเสริมขั้นต่ำกันร้าว (As,min): {As_min:.2f} ตร.ซม./เมตร")
        if method == "วิธีหน่วยแรงใช้งาน (WSD)":
            st.write(f"• หน่วยแรงอัดคอนกรีตยอมให้ (fc): {0.375*fc_prime:.2f} กก./ตร.ซม.")
            st.write(f"• หน่วยแรงดึงเหล็กยอมให้ (fs): {1500.0 if fy>=3000 else 1200.0:.2f} กก./ตร.ซม.")
