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
                        # Membersihkan format string dan menghilangkan desimal .0 jika dibaca angka oleh pandas
                        df_users["Penanggung Jawab Clean"] = df_users["Penanggung Jawab"].astype(str).str.strip().str.lower()
                        df_users["Kode Unik Clean"] = df_users["Kode Unik"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                        
                        matched = df_users[
                            (df_users["Penanggung Jawab Clean"] == pj_input.strip().lower()) &
                            (df_users["Kode Unik Clean"] == kode_input.strip())
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

# ----------------- DASHBOARD UTAMA & FORM OPERASIONAL (SETELAH LOGIN) -----------------
st.markdown(f"""<div class="intro-banner-eucalyptus">
<div>
<div class="motto-badge-red">WE CARE • WE DO • WE WIN</div>
<h1>Dashboard Monitoring HTI Eucalyptus</h1>
<p>Halo, <b>{st.session_state['user_pj']}</b> ({st.session_state['user_role']})</p>
</div>
</div>""", unsafe_allow_html=True)

menu_tabs = st.tabs(["📊 Lihat Data & Monitoring", "➕ Input Data Baru", "🚪 Akun / Logout"])

with menu_tabs[0]:
    st.subheader("Data Operasional Lapangan (Sheet1)")
    df_main = load_data()
    if not df_main.empty:
        st.dataframe(df_main, use_container_width=True)
    else:
        st.info("Belum ada data operasional di Sheet1.")

with menu_tabs[1]:
    st.subheader("Form Input Aktivitas Operasional")
    
    # Ambil daftar unik ID Petak dari data yang sudah ada untuk opsi dropdown pilihan cepat
    df_main_existing = load_data()
    list_petak = df_main_existing["ID Petak"].dropna().unique().tolist() if not df_main_existing.empty else []
    list_kegiatan = ["Land Clearing", "Tanam", "Planing", "Maintenance", "Pemupukan", "Penyemprotan", "Panen"]

    with st.form("form_input_ops"):
        col1, col2 = st.columns(2)
        with col1:
            id_petak = st.selectbox("ID Petak (Pilih dari data yang ada)", options=["-- Pilih --"] + list_petak)
            custom_petak = st.text_input("Atau Ketik ID Petak Baru (jika belum ada di atas)")
            
            spk = st.text_input("Nomor SPK")
            jenis_kegiatan = st.selectbox("Jenis Kegiatan", options=list_kegiatan)
            luas = st.number_input("Luas (Ha)", min_value=0.0, format="%.2f")
            tgl_rencana = st.date_input("Tanggal Rencana Kerja", value=datetime.today())
            tgl_mulai = st.date_input("Tanggal Mulai Bekerja", value=datetime.today())
            tgl_selesai = st.date_input("Tanggal Selesai Kerja", value=datetime.today())
        with col2:
            rencana_tk = st.number_input("Rencana Tenaga Kerja", min_value=0, step=1)
            actual_tk = st.number_input("Actual Tenaga Kerja", min_value=0, step=1)
            rencana_prod = st.number_input("Rencana Produktivitas", min_value=0.0, format="%.2f")
            actual_prod = st.number_input("Actual Produktivitas", min_value=0.0, format="%.2f")
            prod_hari_ini = st.number_input("Produktivitas Sampai Hari ini", min_value=0.0, format="%.2f")
            sisa_luas = st.number_input("Sisa Luas Belum Dikerjakan", min_value=0.0, format="%.2f")
            rincian = st.text_area("Rincian / Keterangan")
        
        btn_submit_ops = st.form_submit_button("💾 SIMPAN DATA OPERASIONAL", use_container_width=True)
        
        if btn_submit_ops:
            final_petak = custom_petak.strip() if (custom_petak and custom_petak.strip()) else (id_petak if id_petak != "-- Pilih --" else "")
            
            if not final_petak:
                st.error("❌ ID Petak wajib diisi atau dipilih!")
            else:
                df_existing = load_data()
                no_baru = len(df_existing) + 1
                new_row = pd.DataFrame([{
                    "No": no_baru,
                    "ID Petak": final_petak,
                    "SPK": spk,
                    "Jenis Kegiatan": jenis_kegiatan,
                    "Luas": luas,
                    "Penanggung Jawab": st.session_state["user_pj"],
                    "Tanggal Rencana Kerja": str(tgl_rencana),
                    "Tanggal Mulai Bekerja": str(tgl_mulai),
                    "Tanggal Selesai Kerja": str(tgl_selesai),
                    "Rencana Tenaga Kerja": rencana_tk,
                    "Actual Tenaga Kerja": actual_tk,
                    "Rencana Produktivitas": rencana_prod,
                    "Actual Produktivitas": actual_prod,
                    "Produktivitas Sampai Hari ini": prod_hari_ini,
                    "Sisa luas belum dikerjakan": sisa_luas,
                    "Rincian": rincian
                }])
                
                updated_df = pd.concat([df_existing, new_row], ignore_index=True)
                try:
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", data=updated_df)
                    st.success("✅ Data operasional berhasil disimpan ke Sheet1!")
                except Exception as e:
                    st.error(f"⚠️ Gagal menyimpan data ke Sheet1: {e}")

with menu_tabs[2]:
    st.subheader("Pengaturan Akun")
    st.write(f"Anda masuk sebagai: **{st.session_state['user_pj']}**")
    st.write(f"Role Akses: **{st.session_state['user_role']}**")
    if st.button("🚪 Keluar / Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["user_pj"] = ""
        st.session_state["user_role"] = "User"
        st.rerun()
