import pandas as pd
from datetime import datetime
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# =========================================================
# KONFIGURASI URL GOOGLE SHEET
# =========================================================
SPREADSHEET_URL = "MASUKKAN_URL_GOOGLE_SHEET_ANDA_DI_SINI"

# 1. PENGATURAN HALAMAN
st.set_page_config(
    page_title="HTI Eucalyptus System", 
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. TEMA DESAIN & CUSTOM CSS (RESPONSIF ANDROID & DESKTOP)
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

header[data-testid="stHeader"],
div[data-testid="stToolbar"],
#MainMenu,
footer,
.stAppHeader,
[data-testid="stHeaderActionElements"] {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background: linear-gradient(180deg, #F4F7F4 0%, #E9EFE9 100%);
}

.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 1200px;
}

/* ================= BANNER UTAMA RESPONSIF ================= */
.intro-banner-eucalyptus {
    background: linear-gradient(135deg, #1B3B22 0%, #2E5A36 60%, #990000 100%);
    color: #FFFFFF;
    padding: 1.2rem 1.5rem;
    border-radius: 16px;
    box-shadow: 0 8px 20px rgba(46, 90, 54, 0.2);
    margin-bottom: 1.2rem;
    border-bottom: 4px solid #C8102E;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    box-sizing: border-box;
    width: 100%;
}

.banner-content {
    flex: 1;
    min-width: 0;
}

.motto-badge-red {
    display: inline-block;
    background: #C8102E;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 0.75rem !important;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    white-space: nowrap;
}

.intro-banner-eucalyptus h1 {
    color: #FFFFFF !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    line-height: 1.2;
    word-wrap: break-word;
}

.intro-banner-eucalyptus p {
    color: #F8F9FA !important;
    margin: 0.4rem 0 0 0 !important;
    font-size: 0.85rem;
    font-weight: 500;
    opacity: 0.95;
    word-break: break-word;
}

.eucalyptus-tree-svg {
    width: 65px;
    height: 65px;
    flex-shrink: 0;
    filter: drop-shadow(0px 3px 6px rgba(0,0,0,0.2));
}

@media (max-width: 640px) {
    .intro-banner-eucalyptus {
        padding: 1rem !important;
        gap: 8px !important;
    }
    .intro-banner-eucalyptus h1 {
        font-size: 1.15rem !important;
    }
    .intro-banner-eucalyptus p {
        font-size: 0.78rem !important;
    }
    .motto-badge-red {
        font-size: 0.65rem !important;
        padding: 0.2rem 0.5rem !important;
    }
    .eucalyptus-tree-svg {
        width: 45px !important;
        height: 45px !important;
    }
}
/* ========================================================= */

div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    padding: 0.9rem 1rem !important;
    border-radius: 14px !important;
    border-left: 5px solid #2E5A36 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.25s ease !important;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-left: 5px solid #C8102E !important;
    box-shadow: 0 6px 16px rgba(200, 16, 46, 0.15) !important;
}
div[data-testid="stMetricLabel"] > div {
    color: #334155 !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="stMetricValue"] > div {
    color: #1E293B !important;
    font-weight: 800 !important;
    font-size: 1.4rem !important;
}

div.stButton > button {
    background: linear-gradient(135deg, #2E5A36 0%, #1B3B22 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-left: 4px solid #C8102E !important;
    border-radius: 12px !important;
    height: 3.2rem !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(46, 90, 54, 0.25) !important;
    transition: all 0.25s ease !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #C8102E 0%, #990000 100%) !important;
    border-left: 4px solid #FFFFFF !important;
    box-shadow: 0 6px 18px rgba(200, 16, 46, 0.35) !important;
}

div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border-color: #CBD5E1 !important;
    background-color: #FFFFFF !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background-color: #E2E8F0;
    padding: 5px;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    height: 2.8rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.88rem;
    color: #475569;
}
.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #2E5A36 !important;
    border-bottom: 3px solid #C8102E;
}

div[data-testid="stDataFrame"] {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 0.4rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    border: 1px solid #E2E8F0;
}

@media (max-width: 768px) {
    .main .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
    }
    div[data-testid="stMetric"] {
        padding: 0.7rem 0.8rem !important;
        margin-bottom: 0.4rem;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.25rem !important;
    }
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.72rem !important;
    }
}
</style>""", unsafe_allow_html=True)

# 3. KONEKSI GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

COLUMNS = [
    "No", "ID Petak", "SPK", "Jenis Kegiatan", "Luas", "Username",
    "Tanggal Rencana Kerja", "Tanggal Mulai Bekerja", "Tanggal Selesai Kerja",
    "Rencana Tenaga Kerja", "Actual Tenaga Kerja", "Rencana Produktivitas",
    "Actual Produktivitas", "Produktivitas Sampai Hari ini", 
    "Sisa luas belum dikerjakan", "Rincian"
]

USER_COLUMNS = ["Username", "Password", "Role"]

def safe_gsheets_update(worksheet_name, data_df):
    try:
        conn.update(spreadsheet=SPREADSHEET_URL, worksheet=worksheet_name, data=data_df)
        return True
    except Exception as e:
        if "Response [200]" in str(e):
            return True
        else:
            raise e

def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=COLUMNS)
            
        if "Penanggung Jawab" in df.columns and "Username" not in df.columns:
            df.rename(columns={"Penanggung Jawab": "Username"}, inplace=True)
            
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[COLUMNS]
    except Exception as e:
        return pd.DataFrame(columns=COLUMNS)

def load_users():
    try:
        df_users = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Users", ttl=0)
        if df_users is None or df_users.empty:
            return pd.DataFrame(columns=USER_COLUMNS)
            
        rename_map = {}
        if "Penanggung Jawab" in df_users.columns:
            rename_map["Penanggung Jawab"] = "Username"
        if "Kode Unik" in df_users.columns:
            rename_map["Kode Unik"] = "Password"
        if rename_map:
            df_users.rename(columns=rename_map, inplace=True)
            
        for col in USER_COLUMNS:
            if col not in df_users.columns:
                df_users[col] = "User" if col == "Role" else None
        
        df_users["Username"] = df_users["Username"].astype(str).str.strip()
        df_users["Password"] = df_users["Password"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df_users[USER_COLUMNS]
    except Exception as e:
        return pd.DataFrame(columns=USER_COLUMNS)

# 4. INISIALISASI SESI LOGIN
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_pj" not in st.session_state:
    st.session_state["user_pj"] = ""
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "User"

EUCALYPTUS_SVG = """<svg class="eucalyptus-tree-svg" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M48 92 C 48 60, 52 40, 50 10 C 50 10, 47 35, 45 92 Z" fill="#FFFFFF" opacity="0.95"/>
<path d="M50 55 C 60 45, 75 42, 82 38 C 72 46, 58 52, 50 58 Z" fill="#FFFFFF" opacity="0.9"/>
<path d="M49 42 C 38 32, 22 30, 15 25 C 25 32, 40 38, 48 45 Z" fill="#FFFFFF" opacity="0.9"/>
<path d="M50 28 C 62 20, 72 16, 78 12 C 68 18, 56 22, 50 30 Z" fill="#FFFFFF" opacity="0.9"/>
<ellipse cx="82" cy="38" rx="8" ry="4" transform="rotate(-20 82 38)" fill="#FFFFFF"/>
<ellipse cx="70" cy="42" rx="7" ry="3.5" transform="rotate(-15 70 42)" fill="#FFFFFF" opacity="0.9"/>
<ellipse cx="15" cy="25" rx="8" ry="4" transform="rotate(20 15 25)" fill="#FFFFFF"/>
<ellipse cx="28" cy="32" rx="7" ry="3.5" transform="rotate(15 28 32)" fill="#FFFFFF" opacity="0.9"/>
<ellipse cx="78" cy="12" rx="7" ry="3.5" transform="rotate(-25 78 12)" fill="#FFFFFF"/>
<ellipse cx="64" cy="18" rx="6" ry="3" transform="rotate(-20 64 18)" fill="#FFFFFF" opacity="0.9"/>
<ellipse cx="50" cy="8" rx="7" ry="3.5" transform="rotate(-90 50 8)" fill="#FFFFFF"/>
</svg>"""

# =========================================================
# TAMPILAN LOGIN / REGISTRASI AKUN
# =========================================================
if not st.session_state["logged_in"]:
    st.markdown(f"""<div class="intro-banner-eucalyptus">
<div class="banner-content">
<div class="motto-badge-red">WE CARE • WE DO • WE WIN</div>
<h1>HTI Eucalyptus System</h1>
<p>Sistem Monitoring & Rencana Kerja Operasional Lapangan</p>
</div>
{EUCALYPTUS_SVG}
</div>""", unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["Masuk Sistem", "Pendaftaran Akun"])
    
    with tab_login:
        st.subheader("Autentikasi Pengguna")
        with st.form("form_login"):
            pj_input = st.text_input("Username")
            kode_input = st.text_input("Password", type="password")
            btn_login = st.form_submit_button("Masuk", use_container_width=True)
            
            if btn_login:
                if not pj_input.strip() or not kode_input.strip():
                    st.error("Username dan Password wajib diisi.")
                else:
                    df_users = load_users()
                    if not df_users.empty:
                        matched = df_users[
                            (df_users["Username"].str.upper() == pj_input.strip().upper()) &
                            (df_users["Password"] == kode_input.strip())
                        ]
                        if not matched.empty:
                            st.session_state["logged_in"] = True
                            st.session_state["user_pj"] = matched.iloc[0]["Username"]
                            role_val = matched.iloc[0].get("Role", "User")
                            st.session_state["user_role"] = role_val if pd.notna(role_val) else "User"
                            st.success(f"Selamat datang, {st.session_state['user_pj']}.")
                            st.rerun()
                        else:
                            st.error("Username atau Password tidak valid.")
                    else:
                        st.error("Data pengguna tidak ditemukan. Silakan lakukan pendaftaran akun.")

    with tab_register:
        st.subheader("Registrasi Akun Baru")
        with st.form("form_register"):
            reg_pj = st.text_input("Username", placeholder="Contoh: Rezki Difan Arshaf")
            reg_kode = st.text_input("Password", type="password", placeholder="Minimal 4 karakter")
            btn_reg = st.form_submit_button("Daftar", use_container_width=True)
            
            if btn_reg:
                if not reg_pj.strip() or not reg_kode.strip():
                    st.error("Username dan Password wajib diisi.")
                else:
                    df_users = load_users()
                    if not df_users.empty and "Username" in df_users.columns:
                        exists = df_users[df_users["Username"].str.upper() == reg_pj.strip().upper()]
                        if not exists.empty:
                            st.error(f"Username '{reg_pj}' sudah terdaftar. Silakan gunakan menu Masuk.")
                            st.stop()
                    
                    new_user = pd.DataFrame([{
                        "Username": reg_pj.strip(), 
                        "Password": str(reg_kode.strip()),
                        "Role": "User"
                    }])
                    updated_users = pd.concat([df_users, new_user], ignore_index=True)
                    try:
                        safe_gsheets_update("Users", updated_users)
                        st.success("Akun berhasil didaftarkan. Silakan pindah ke tab Masuk.")
                    except Exception as e:
                        st.error(f"Gagal menyimpan data pengguna: {e}")

        st.stop()

# =========================================================
# DASHBOARD & OPERASIONAL UTAMA
# =========================================================
df = load_data()
is_admin = str(st.session_state.get("user_role", "User")).strip().lower() == "admin"

role_badge = "Administrator" if is_admin else "Field Officer"
st.markdown(f"""<div class="intro-banner-eucalyptus">
<div class="banner-content">
<div class="motto-badge-red">WE CARE • WE DO • WE WIN</div>
<h1>Monitoring Silvikultur Eucalyptus</h1>
<p>Username: <b>{st.session_state['user_pj']}</b> | Akses: <b>{role_badge}</b></p>
</div>
{EUCALYPTUS_SVG}
</div>""", unsafe_allow_html=True)

col_space, col_logout = st.columns([3, 1.5])
with col_logout:
    if st.button("Keluar", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["user_pj"] = ""
        st.session_state["user_role"] = "User"
        st.rerun()

st.write("")

# =========================================================
# 3 MENU UTAMA (TAB NAVIGASI DI PALING ATAS)
# =========================================================
tab_input, tab_rencana, tab_jadwal = st.tabs([
    "Input Data", 
    "Rencana Kerja", 
    "Jadwal Kerja Selanjutnya"
])

# TAB 1: INPUT DATA
with tab_input:
    st.subheader("Formulir Input Data Lapangan")
    list_petak_existing = []
    if not df.empty and "ID Petak" in df.columns:
        list_petak_existing = [str(x).strip() for x in df["ID Petak"].dropna().unique() if str(x).strip() != ""]

    mode_input_petak = st.radio(
        "Metode Input ID Petak", 
        ["Pilih Petak Tersedia", "Input Petak Baru"], 
        horizontal=True
    )

    with st.form("form_monitoring", clear_on_submit=True):
        st.write("Informasi Petak")
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            if mode_input_petak == "Pilih Petak Tersedia" and list_petak_existing:
                id_petak = st.selectbox("ID Petak", list_petak_existing)
            else:
                id_petak = st.text_input("ID Petak", placeholder="Contoh: EUC-A01")
                
            luas = st.number_input("Luas Area (Ha)", min_value=0.0, step=0.1)
            
        with col_f2:
            spk_input = st.text_input("Nomor SPK", placeholder="Contoh: SPK/EUC/2026/001")
            pj = st.text_input("Username", value=st.session_state["user_pj"], disabled=True)
            
        jenis_kegiatan = st.selectbox("Jenis Kegiatan", [
            "Established - PLTB", "Established - Kuku Macan", "Established - Parit",
            "Established - Teras", "Established - Lining+Sticking", "Established - Tanam",
            "Established - Tanam & Aquasorb", "Established - Sulam", "Established - PPS",
            "Established - PPS Dron", "Maintenance - MW 1", "Maintenance - CW 1",
            "Maintenance - CW 2", "Maintenance - CW 3", "Maintenance - CW 4",
            "Maintenance - CW 5", "Maintenance - CW 6", "Maintenance - CW 7",
            "Maintenance - MW 2", "Maintenance - MW 3", "Maintenance - PS1",
            "Maintenance - PS1 drone", "Maintenance - HPT", "Maintenance - HPT Drone",
            "Maintenance - PS2 Drone", "Maintenance - PS 2", "Lainnya"
        ])
        
        st.markdown("---")
        st.write("Jadwal Operasional")
        c_tgl1, c_tgl2, c_tgl3 = st.columns(3)
        with c_tgl1:
            tgl_rencana = st.date_input("Tanggal Rencana")
        with c_tgl2:
            tgl_mulai = st.date_input("Tanggal Mulai")
        with c_tgl3:
            tgl_selesai = st.date_input("Tanggal Selesai")
        
        st.markdown("---")
        st.write("Alokasi Tenaga Kerja & Target")
        
        col_tk1, col_tk2 = st.columns(2)
        with col_tk1:
            rencana_tk = st.number_input("Rencana TK (Orang)", min_value=0, step=1)
            rencana_prod = st.number_input("Rencana Produktivitas (Ha)", min_value=0.0, step=0.1)
        with col_tk2:
            actual_tk = st.number_input("Aktual TK (Orang)", min_value=0, step=1)
            actual_prod = st.number_input("Aktual Produktivitas (Ha)", min_value=0.0, step=0.1)
            
        rincian_input = st.text_area("Catatan Lapangan", height=80)
        
        submitted = st.form_submit_button("Simpan Data", use_container_width=True)

        if submitted:
            pj_final = st.session_state["user_pj"]
            
            if not id_petak.strip() or luas <= 0:
                st.error("ID Petak dan Luas wajib diisi dengan benar.")
            else:
                prev_actual = 0.0
                if not df.empty and "ID Petak" in df.columns and "Actual Produktivitas" in df.columns:
                    mask = df["ID Petak"].astype(str).str.strip().str.upper() == id_petak.strip().upper()
                    prev_actual = pd.to_numeric(df[mask]["Actual Produktivitas"], errors="coerce").fillna(0).sum()
                
                prod_kumulatif = prev_actual + actual_prod
                prod_hari_ini = min(prod_kumulatif, luas)
                sisa_luas = max(0.0, luas - prod_hari_ini)
                
                status_kerja = "Complete" if sisa_luas <= 0 else "On Progres"
                final_rincian = f"{status_kerja} - {rincian_input.strip()}" if rincian_input.strip() else status_kerja

                spk_val = spk_input.strip() if spk_input.strip() else "-"
                no_baru = len(df) + 1 if not df.empty else 1
                
                new_row = pd.DataFrame([{
                    "No": no_baru,
                    "ID Petak": id_petak.strip(),
                    "SPK": spk_val,
                    "Jenis Kegiatan": jenis_kegiatan,
                    "Luas": luas,
                    "Username": pj_final,
                    "Tanggal Rencana Kerja": tgl_rencana.strftime("%Y-%m-%d"),
                    "Tanggal Mulai Bekerja": tgl_mulai.strftime("%Y-%m-%d"),
                    "Tanggal Selesai Kerja": tgl_selesai.strftime("%Y-%m-%d"),
                    "Rencana Tenaga Kerja": rencana_tk,
                    "Actual Tenaga Kerja": actual_tk,
                    "Rencana Produktivitas": rencana_prod,
                    "Actual Produktivitas": actual_prod,
                    "Produktivitas Sampai Hari ini": prod_kumulatif,
                    "Sisa luas belum dikerjakan": sisa_luas,
                    "Rincian": final_rincian
                }])
                
                updated_df = pd.concat([df, new_row], ignore_index=True)
                safe_gsheets_update("Sheet1", updated_df)
                st.success(f"Data petak '{id_petak}' berhasil disimpan.")
                st.rerun()

    # Panel Admin di dalam tab Input Data jika role admin
    if is_admin:
        st.markdown("---")
        st.subheader("Panel Administrator")
        if not df.empty:
            options_list = [f"Baris {idx + 1} | ID: {row['ID Petak']} | SPK: {row.get('SPK', '-')} | User: {row['Username']}" for idx, row in df.iterrows()]
            selected_option = st.selectbox("Pilih Data untuk Dihapus", options_list)
            selected_idx = options_list.index(selected_option)
            
            if st.button("Hapus Data Terpilih", use_container_width=True):
                df_dropped = df.drop(selected_idx).reset_index(drop=True)
                df_dropped["No"] = range(1, len(df_dropped) + 1)
                safe_gsheets_update("Sheet1", df_dropped)
                st.success("Data berhasil dihapus.")
                st.rerun()

# TAB 2: RENCANA KERJA
with tab_rencana:
    st.subheader("Monitoring Rencana Kerja")
    
    # RINGKASAN METRIK
    total_luas = pd.to_numeric(df["Luas"], errors="coerce").fillna(0).sum() if not df.empty else 0
    total_r_tk = pd.to_numeric(df["Rencana Tenaga Kerja"], errors="coerce").fillna(0).sum() if not df.empty else 0
    total_a_tk = pd.to_numeric(df["Actual Tenaga Kerja"], errors="coerce").fillna(0).sum() if not df.empty else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Petak", f"{len(df)} Unit")
    m2.metric("Total Luas", f"{total_luas:,.1f} Ha")
    m3.metric("Rencana TK", f"{int(total_r_tk)} Orang")
    m4.metric("Aktual TK", f"{int(total_a_tk)} Orang")

    st.write("")
    view_option = st.radio("Tampilkan Data", ["Data Saya", "Semua Data Tim"], horizontal=True)

    filtered_df = df.copy()
    if view_option == "Data Saya" and not filtered_df.empty:
        filtered_df = filtered_df[
            filtered_df["Username"].astype(str).str.strip().str.upper() == st.session_state["user_pj"].strip().upper()
        ]

    search_term = st.text_input("Pencarian", placeholder="Ketik kata kunci...")
    if search_term and not filtered_df.empty:
        filtered_df = filtered_df[
            filtered_df["ID Petak"].astype(str).str.contains(search_term, case=False, na=False) |
            filtered_df["SPK"].astype(str).str.contains(search_term, case=False, na=False) |
            filtered_df["Username"].astype(str).str.contains(search_term, case=False, na=False) |
            filtered_df["Jenis Kegiatan"].astype(str).str.contains(search_term, case=False, na=False) |
            filtered_df["Rincian"].astype(str).str.contains(search_term, case=False, na=False)
        ]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# TAB 3: JADWAL KERJA SELANJUTNYA
with tab_jadwal:
    st.subheader("Jadwal Kerja Selanjutnya")
    st.write("Kelengkapan nomor SPK dan agenda operasional lanjutan.")
    
    if df.empty:
        st.info("Belum terdapat data kegiatan.")
    else:
        spk_series = df["SPK"].astype(str).str.strip()
        empty_spk_mask = df["SPK"].isna() | (spk_series == "") | (spk_series == "-") | (spk_series == "None") | (spk_series == "nan")
        user_mask = df["Username"].astype(str).str.strip().str.upper() == st.session_state["user_pj"].strip().upper()
        
        unfilled_df = df[user_mask & empty_spk_mask]
        
        if unfilled_df.empty:
            st.info("Seluruh kegiatan Anda telah memiliki Nomor SPK.")
        else:
            options_spk = {}
            for idx, row in unfilled_df.iterrows():
                label = f"ID: {row['ID Petak']} | Kegiatan: {row['Jenis Kegiatan']} | Luas: {row['Luas']} Ha"
                options_spk[label] = idx
            
            selected_label = st.selectbox("Pilih Kegiatan Tanpa SPK", list(options_spk.keys()))
            target_idx = options_spk[selected_label]
            
            with st.form("form_update_spk_user"):
                input_spk_baru = st.text_input("Nomor SPK Baru", placeholder="Contoh: SPK/EUC/2026/001")
                btn_spk_submit = st.form_submit_button("Perbarui SPK", use_container_width=True)
                
                if btn_spk_submit:
                    if not input_spk_baru.strip():
                        st.error("Nomor SPK tidak boleh kosong.")
                    else:
                        df.at[target_idx, "SPK"] = input_spk_baru.strip()
                        safe_gsheets_update("Sheet1", df)
                        st.success("Nomor SPK berhasil diperbarui.")
                        st.rerun()
