import pandas as pd
from datetime import datetime
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 🔗 URL GOOGLE SHEET ANDA
# =========================================================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1qJMHdTkURQV7LQE_DfO3UiX_txepHVCXqRct3mrQlxs/edit?usp=drivesdk"

# 1. PENGATURAN HALAMAN
st.set_page_config(
    page_title="HTI Eucalyptus - We Care We Do We Win", 
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CUSTOM CSS
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

header[data-testid="stHeader"], div[data-testid="stToolbar"], #MainMenu, footer, .stAppHeader {
    display: none !important;
    visibility: hidden !important;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp {
    background: linear-gradient(180deg, #F4F7F4 0%, #E9EFE9 100%);
}

.intro-banner-eucalyptus {
    background: linear-gradient(135deg, #1B3B22 0%, #2E5A36 60%, #990000 100%);
    color: #FFFFFF;
    padding: 1.5rem 1.8rem;
    border-radius: 18px;
    box-shadow: 0 10px 25px rgba(46, 90, 54, 0.25);
    margin-bottom: 1.2rem;
    border-bottom: 4px solid #C8102E;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
}

.motto-badge-red {
    display: inline-block;
    background: #C8102E;
    color: #FFFFFF !important;
    font-weight: 900 !important;
    font-size: 0.8rem !important;
    padding: 0.3rem 0.8rem;
    border-radius: 30px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

div.stButton > button {
    background: linear-gradient(135deg, #2E5A36 0%, #1B3B22 100%) !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    height: 3.2rem !important;
    font-weight: 700 !important;
}
</style>""", unsafe_allow_html=True)

# 3. KONEKSI GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

COLUMNS = [
    "No", "ID Petak", "SPK", "Jenis Kegiatan", "Luas", "Penanggung Jawab",
    "Tanggal Rencana Kerja", "Tanggal Mulai Bekerja", "Tanggal Selesai Kerja",
    "Rencana Tenaga Kerja", "Actual Tenaga Kerja", "Rencana Produktivitas",
    "Actual Produktivitas", "Produktivitas Sampai Hari ini", 
    "Sisa luas belum dikerjakan", "Rincian"
]

USER_COLUMNS = ["Penanggung Jawab", "Kode Unik", "Role"]

def load_users():
    try:
        df_users = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Users", ttl=0)
        if df_users is None or df_users.empty:
            return pd.DataFrame(columns=USER_COLUMNS)
        for col in USER_COLUMNS:
            if col not in df_users.columns:
                df_users[col] = "User" if col == "Role" else None
        return df_users[USER_COLUMNS]
    except Exception as e:
        st.error(f"⚠️ Gagal membaca tab 'Users': {e}")
        return pd.DataFrame(columns=USER_COLUMNS)

def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=COLUMNS)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[COLUMNS]
    except Exception as e:
        return pd.DataFrame(columns=COLUMNS)

# 4. SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_pj" not in st.session_state:
    st.session_state["user_pj"] = ""
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "User"

# ----------------- TAMPILAN LOGIN & REGISTRASI -----------------
if not st.session_state["logged_in"]:
    st.markdown("""<div class="intro-banner-eucalyptus">
<div>
<div class="motto-badge-red">WE CARE • WE DO • WE WIN</div>
<h1>HTI Eucalyptus System</h1>
<p>Sistem Monitoring & Rencana Kerja Operasional Lapangan</p>
</div>
</div>""", unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["🔑 Login Masuk", "📝 Pendaftaran User"])
    
    with tab_login:
        st.subheader("Akses Akun Operasional")
        with st.form("form_login"):
            pj_input = st.text_input("Nama Penanggung Jawab")
            kode_input = st.text_input("Kode Unik / PIN Akun", type="password")
            btn_login = st.form_submit_button("🔑 MASUK KE SISTEM", use_container_width=True)
            
            if btn_login:
                if not pj_input.strip() or not kode_input.strip():
                    st.error("❌ Nama dan Kode Unik wajib diisi!")
                else:
                    df_users = load_users()
                    if not df_users.empty:
                        matched = df_users[
                            (df_users["Penanggung Jawab"].astype(str).str.strip().str.upper() == pj_input.strip().upper()) &
                            (df_users["Kode Unik"].astype(str).str.strip() == kode_input.strip())
                        ]
                        if not matched.empty:
                            st.session_state["logged_in"] = True
                            st.session_state["user_pj"] = matched.iloc[0]["Penanggung Jawab"]
                            role_val = matched.iloc[0].get("Role", "User")
                            st.session_state["user_role"] = role_val if pd.notna(role_val) else "User"
                            st.success("Login berhasil!")
                            st.rerun()
                        else:
                            st.error("❌ Nama Penanggung Jawab atau Kode Unik salah!")
                    else:
                        st.error("❌ Belum ada data di tab 'Users' atau gagal membaca sheet.")

    with tab_register:
        st.subheader("Registrasi Penanggung Jawab Baru")
        with st.form("form_register"):
            reg_pj = st.text_input("Nama Penanggung Jawab *", placeholder="Contoh: Budi Santoso")
            reg_kode = st.text_input("Buat Kode Unik / PIN *", type="password", placeholder="Minimal 4 karakter")
            btn_reg = st.form_submit_button("📝 DAFTAR AKUN BARU", use_container_width=True)
            
            if btn_reg:
                if not reg_pj.strip() or not reg_kode.strip():
                    st.error("❌ Nama Penanggung Jawab dan Kode Unik wajib diisi!")
                else:
                    df_users = load_users()
                    
                    new_user = pd.DataFrame([{
                        "Penanggung Jawab": reg_pj.strip(), 
                        "Kode Unik": str(reg_kode.strip()),
                        "Role": "User"
                    }])
                    
                    updated_users = pd.concat([df_users, new_user], ignore_index=True)
                    
                    try:
                        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Users", data=updated_users)
                        st.success(f"✅ Pendaftaran '{reg_pj}' berhasil dan tersimpan ke Sheet! Silakan pindah ke tab 'Login Masuk'.")
                    except Exception as e:
                        st.error(f"⚠️ Gagal menyimpan ke Google Sheet: {e}")

        st.stop()
