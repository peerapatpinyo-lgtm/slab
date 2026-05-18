import streamlit as st
import math

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="RC Slab Design (WSD)", layout="centered")

st.title("🏗️ โปรแกรมออกแบบแผ่นพื้น ค.ส.ล. ทางเดียว")
st.subheader("วิธีหน่วยแรงใช้งาน (Working Stress Design - WSD)")
st.write("พัฒนาด้วย Streamlit สำหรับวิศวกรและผู้สนใจ")

# สร้างแถบด้านข้าง (Sidebar) สำหรับรับค่าอินพุต
st.sidebar.header("📥 ป้อนข้อมูลการออกแบบ")

# 1. มิติของโครงสร้าง
L = st.sidebar.slider("ความยาวช่วงพื้น L (เมตร)", min_value=1.0, max_value=8.0, value=3.0, step=0.1)
t_cm = st.sidebar.number_input("ความหนาของแผ่นพื้น t (เซนติเมตร)", min_value=5, max_value=30, value=10, step=1)
t = t_cm / 100 # แปลงเป็นเมตร

# 2. น้ำหนักบรรทุก
LL = st.sidebar.number_input("น้ำหนักบรรทุกจร Live Load (กก./ตร.ม.)", min_value=0, max_value=1000, value=150, step=50)

# 3. คุณสมบัติวัสดุ
st.sidebar.subheader("🛠️ คุณสมบัติวัสดุ")
fc_prime = st.sidebar.number_input("กำลังอัดคอนกรีต fc' (กก./ตร.ซม.)", min_value=100, max_value=400, value=173)
fy = st.sidebar.selectbox("กำลังรับแรงดึงของเหล็ก fy (กก./ตร.ซม.)", options=[2400, 3000, 4000], index=1)

# --- ส่วนการคำนวณทางวิศวกรรม ---
# ข้อกำหนด WSD
fc = 0.375 * fc_prime
fs = 0.5 * fy
n = 11

# ค่าคงที่ k, j, R
k = n / (n + (fs / fc))
j = 1 - (k / 3)
R = 0.5 * fc * k * j

# คำนวณน้ำหนักบรรทุก (คิดต่อความกว้าง b = 1 เมตร)
b = 1.0 # เมตร
DL_slab = t * 1.0 * 2400 # น้ำหนักคอนกรีต 2400 กก./ลบ.ม.
W = DL_slab + LL

# คำนวณโมเมนต์สูงสุด (กรณี Simply Supported)
M_max = (W * (L ** 2)) / 8
M_max_cm = M_max * 100

# ตรวจสอบความหนา (d_required) สมมติระยะหุ้ม 2 ซม.
d = t_cm - 2
d_required = math.sqrt(M_max_cm / (R * (b * 100)))

# พื้นที่เหล็กเสริม (As)
As = M_max_cm / (fs * j * d)
# เหล็กเสริมขั้นต่ำกันร้าว
As_min = 0.0025 * (b * 100) * t_cm if fy == 3000 else 0.0020 * (b * 100) * t_cm
As_final = max(As, As_min)

# เลือกขนาดเหล็กอัตโนมัติเบื้องต้นตามความหนาพื้น
bar_dia = 9 if t_cm < 15 else 12
bar_area = (math.pi / 4) * ((bar_dia/10) ** 2)

# คำนวณระยะห่าง (Spacing)
spacing = (bar_area / As_final) * 100
spacing = min(spacing, 3 * t_cm, 45) # ตรวจสอบเงื่อนไขระยะห่างสูงสุด

# --- ส่วนการแสดงผลบนหน้าเว็บ (UI) ---
col1, col2 = st.columns(2)

with col1:
    st.metric(label="น้ำหนักบรรทุกรวม (W)", value=f"{W:.2f} กก./ตร.ม.")
with col2:
    st.metric(label="โมเมนต์ดัดสูงสุด (M_max)", value=f"{M_max:.2f} กก.-เมตร")

st.markdown("---")
st.subheader("📋 ผลการตรวจสอบและออกแบบ")

# ตรวจสอบความหนาแผ่นพื้น
if d < d_required:
    st.error(f"❌ **ความหนาพื้นไม่เพียงพอ!** ความลึกที่ต้องการคือ {d_required:.2f} ซม. แต่ปัจจุบันมีเพียง {d:.2f} ซม. (กรุณาเพิ่มความหนาของแผ่นพื้นในแถบด้านข้าง)")
else:
    st.success(f"✔️ **ความหนาพื้นผ่านเกณฑ์:** ความลึกประสิทธิผลจริง ({d:.2f} ซม.) มากกว่าค่าที่ต้องการ ({d_required:.2f} ซม.)")
    
    # แสดงข้อแนะนำการจัดเหล็กเสริม
    st.info(f"💡 **พื้นที่เหล็กเสริมที่ต้องการ (As):** {As_final:.2f} ตร.ซม./เมตร")
    
    # กล่องข้อความขนาดใหญ่สำหรับผลลัพธ์การจัดเหล็ก
    st.markdown(f"""
    <div style="background-color:#e1f5fe; padding:20px; border-radius:10px; border-left: 8px solid #0288d1;">
        <h4 style="color:#01579b; margin-top:0;">🎯 ข้อแนะนำการเสริมเหล็ก:</h4>
        <p style="font-size:20px; color:#01579b; font-weight:bold; margin-bottom:0;">
            ใช้เหล็กเส้นขนาด <b>Ø {bar_dia} มม. @ {spacing:.1f} ซม.</b>
        </p>
        <small style="color:#555;">*คำนวณต่อความกว้างแผ่นพื้น 1 เมตร และรวมเหล็กเสริมขั้นต่ำกันร้าวแล้ว</small>
    </div>
    """, unsafe_allow_index=True)

# แสดงรายละเอียดการคำนวณภายใน (สำหรับผู้ที่ต้องการตรวจสอบ)
with st.expander("🔍 ดูรายละเอียดพารามิเตอร์การคำนวณ (Engineering Parameters)"):
    st.write(f"- หน่วยแรงอัดคอนกรีตที่ยอมให้ ($f_c$): {fc:.2f} กก./ตร.ซม.")
    st.write(f"- หน่วยแรงดึงเหล็กที่ยอมให้ ($f_s$): {fs:.2f} กก./ตร.ซม.")
    st.write(f"- ค่าตัวแปรคงที่: $k$ = {k:.3f}, $j$ = {j:.3f}, $R$ = {R:.2f}")
    st.write(f"- น้ำหนักจากน้ำหนักบรรทุกคงที่ของพื้น (DL): {DL_slab:.2f} กก./ตร.ม.")
