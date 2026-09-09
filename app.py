import pandas as pd
from datetime import datetime
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Pengaturan Halaman
st.set_page_config(
    page_title="Monitoring & Rencana Kerja", 
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS Tampilan HP Android
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    
    div.stButton > button {
        width: 100% !important;
        height: 3.2rem !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }
    
    h1 { font-size: 1.6rem !important; margin-bottom: 0.2rem !important; }
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; }
    
    .streamlit-expanderHeader {
        font-size: 1rem !important;
        font-weight: bold !important;
        background-color: #1e1e1e !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

COLUMNS = [
    "No", "ID Petak", "SPK", "Jenis Kegiatan", "Luas", "Penanggung Jawab",
    "Tanggal Rencana Kerja", "Tanggal Mulai Bekerja", "Tanggal Selesai Kerja",
    "Rencana Tenaga Kerja", "Actual Tenaga Kerja", "Rencana Produktivitas",
    "Actual Produktivitas", "Produktivitas Sampai Hari ini", 
    "Sisa luas belum dikerjakan", "Rincian"
]

USER_COLUMNS = ["Penanggung Jawab", "Kode Unik", "Role"]

def load_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=COLUMNS)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[COLUMNS]
    except Exception as e:
        st.error(f"⚠️ Eror Koneksi Data: {e}")
        return pd.DataFrame(columns=COLUMNS)

def load_users():
    try:
        df_users = conn.read(worksheet="Users", ttl=0)
        if df_users is None or df_users.empty:
            return pd.DataFrame(columns=USER_COLUMNS)
        for col in USER_COLUMNS:
            if col not in df_users.columns:
                df_users[col] = "User" if col == "Role" else None
        return df_users[USER_COLUMNS]
    except Exception as e:
        return pd.DataFrame(columns=USER_COLUMNS)

# 3. Pengelolaan Session State (Login)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_pj" not in st.session_state:
    st.session_state["user_pj"] = ""
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "User"

# ----------------- TAMPILAN LOGIN / REGISTRASI -----------------
if not st.session_state["logged_in"]:
    st.title("🚜 Sistem Monitoring Kerja")
    st.caption("Akses Sistem Monitoring Lapangan Real-time")
    st.markdown("---")
    
    tab_login, tab_register = st.tabs(["🔑 Login Masuk", "📝 Pendaftaran Pj Baru"])
    
    # TAB LOGIN
    with tab_login:
        st.subheader("Masuk ke Akun")
        with st.form("form_login"):
            pj_input = st.text_input("Nama Penanggung Jawab")
            kode_input = st.text_input("Kode Unik / PIN", type="password")
            btn_login = st.form_submit_button("🔑 MASUK")
            
            if btn_login:
                if not pj_input.strip() or not kode_input.strip():
                    st.error("❌ Nama Penanggung Jawab dan Kode Unik wajib diisi!")
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
                            st.success(f"Berhasil masuk! Selamat datang, {st.session_state['user_pj']}.")
                            st.rerun()
                        else:
                            st.error("❌ Nama Penanggung Jawab atau Kode Unik salah!")
                    else:
                        st.error("❌ Belum ada akun terdaftar. Silakan pendaftaran terlebih dahulu!")

    # TAB REGISTRASI
    with tab_register:
        st.subheader("Pendaftaran Akun Baru")
        with st.form("form_register"):
            reg_pj = st.text_input("Nama Penanggung Jawab *", placeholder="Contoh: Budi Santoso")
            reg_kode = st.text_input("Buat Kode Unik / PIN *", type="password", placeholder="Minimal 4 karakter")
            btn_reg = st.form_submit_button("📝 DAFTAR AKUN")
            
            if btn_reg:
                if not reg_pj.strip() or not reg_kode.strip():
                    st.error("❌ Nama Penanggung Jawab dan Kode Unik wajib diisi!")
                else:
                    df_users = load_users()
                    if not df_users.empty and "Penanggung Jawab" in df_users.columns:
                        exists = df_users[df_users["Penanggung Jawab"].astype(str).str.strip().str.upper() == reg_pj.strip().upper()]
                        if not exists.empty:
                            st.error(f"❌ Nama '{reg_pj}' sudah terdaftar! Silakan langsung Login.")
                            st.stop()
                    
                    new_user = pd.DataFrame([{
                        "Penanggung Jawab": reg_pj.strip(), 
                        "Kode Unik": reg_kode.strip(),
                        "Role": "User"
                    }])
                    updated_users = pd.concat([df_users, new_user], ignore_index=True)
                    try:
                        conn.update(worksheet="Users", data=updated_users)
                        st.success("✅ Pendaftaran berhasil! Silakan pindah ke tab 'Login Masuk' untuk masuk.")
                    except Exception as e:
                        st.error(f"⚠️ Gagal menyimpan ke Google Sheets: {e}. Pastikan tab 'Users' sudah dibuat di Google Sheet!")

        st.stop()

# ----------------- TAMPILAN UTAMA (SETELAH LOGIN) -----------------
df = load_data()
is_admin = str(st.session_state.get("user_role", "User")).strip().lower() == "admin"

# Header & Informasi Login
col_title, col_logout = st.columns([3, 1])
with col_title:
    st.title("🚜 Sistem Monitoring Kerja")
    role_badge = "👑 Admin" if is_admin else "👤 User"
    st.caption(f"Penanggung Jawab: **{st.session_state['user_pj']}** ({role_badge})")
with col_logout:
    st.write("")
    if st.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user_pj"] = ""
        st.session_state["user_role"] = "User"
        st.rerun()

st.markdown("---")

# Ringkasan Metrik Utama
total_luas = pd.to_numeric(df["Luas"], errors="coerce").fillna(0).sum() if not df.empty else 0
total_r_tk = pd.to_numeric(df["Rencana Tenaga Kerja"], errors="coerce").fillna(0).sum() if not df.empty else 0
total_a_tk = pd.to_numeric(df["Actual Tenaga Kerja"], errors="coerce").fillna(0).sum() if not df.empty else 0

m1, m2 = st.columns(2)
m1.metric("Total Petak", len(df))
m2.metric("Total Luas", f"{total_luas:,.1f} Ha")

m3, m4 = st.columns(2)
m3.metric("Rencana TK", f"{int(total_r_tk)} Orng")
m4.metric("Actual TK", f"{int(total_a_tk)} Orng")

st.markdown("---")

# 1. FORM INPUT DATA BARU
with st.expander("📝 Form Input / Tambah Data Kerja", expanded=False):
    with st.form("form_monitoring", clear_on_submit=True):
        st.subheader("📌 Informasi Utama")
        id_petak = st.text_input("ID Petak *", placeholder="Contoh: P01")
        spk_input = st.text_input("Nomor SPK (Opsional)", placeholder="Contoh: SPK/2026/001")
        pj = st.text_input("Penanggung Jawab *", value=st.session_state["user_pj"], disabled=True)
        luas = st.number_input("Luas (Ha) *", min_value=0.0, step=0.1)
        
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
        st.subheader("📅 Jadwal Kerja")
        tgl_rencana = st.date_input("Tanggal Rencana Kerja")
        tgl_mulai = st.date_input("Tanggal Mulai Bekerja")
        tgl_selesai = st.date_input("Tanggal Selesai Kerja")
        
        st.markdown("---")
        st.subheader("👥 Tenaga Kerja & Produktivitas")
        
        col_tk1, col_tk2 = st.columns(2)
        with col_tk1:
            rencana_tk = st.number_input("Rencana TK (Orang)", min_value=0, step=1)
            rencana_prod = st.number_input("Rencana Produktivitas (Ha)", min_value=0.0, step=0.1)
        with col_tk2:
            actual_tk = st.number_input("Actual TK (Orang)", min_value=0, step=1)
            actual_prod = st.number_input("Actual Produktivitas Hari Ini (Ha)", min_value=0.0, step=0.1)
            
        rincian_input = st.text_area("Catatan Tambahan (Opsional)", height=80)
        
        submitted = st.form_submit_button("💾 SIMPAN DATA", use_container_width=True)

        if submitted:
            pj_final = st.session_state["user_pj"]
            
            if not id_petak.strip() or luas <= 0:
                st.error("❌ ID Petak dan Luas (lebih dari 0) wajib diisi!")
            else:
                prev_actual = 0.0
                if not df.empty and "ID Petak" in df.columns and "Actual Produktivitas" in df.columns:
                    mask = df["ID Petak"].astype(str).str.strip().str.upper() == id_petak.strip().upper()
                    prev_actual = pd.to_numeric(df[mask]["Actual Produktivitas"], errors="coerce").fillna(0).sum()
                
                prod_kumulatif = prev_actual + actual_prod
                prod_hari_ini = min(prod_kumulatif, luas)
                sisa_luas = max(0.0, luas - prod_hari_ini)
                
                status_kerja = "Complete" if sisa_luas == 0 else "On Progres"
                final_rincian = f"{status_kerja} - {rincian_input.strip()}" if rincian_input.strip() else status_kerja

                spk_val = spk_input.strip() if spk_input.strip() else "-"

                no_baru = len(df) + 1 if not df.empty else 1
                
                new_row = pd.DataFrame([{
                    "No": no_baru,
                    "ID Petak": id_petak.strip(),
                    "SPK": spk_val,
                    "Jenis Kegiatan": jenis_kegiatan,
                    "Luas": luas,
                    "Penanggung Jawab": pj_final,
                    "Tanggal Rencana Kerja": tgl_rencana.strftime("%Y-%m-%d"),
                    "Tanggal Mulai Bekerja": tgl_mulai.strftime("%Y-%m-%d"),
                    "Tanggal Selesai Kerja": tgl_selesai.strftime("%Y-%m-%d"),
                    "Rencana Tenaga Kerja": rencana_tk,
                    "Actual Tenaga Kerja": actual_tk,
                    "Rencana Produktivitas": rencana_prod,
                    "Actual Produktivitas": actual_prod,
                    "Produktivitas Sampai Hari ini": prod_hari_ini,
                    "Sisa luas belum dikerjakan": sisa_luas,
                    "Rincian": final_rincian
                }])
                
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                
                if spk_val == "-":
                    st.warning(f"⚠️ Data ID Petak '{id_petak}' berhasil disimpan, **namun Nomor SPK belum terisi!** Silakan lengkapi di menu 'Lengkapi Nomor SPK'.")
                else:
                    st.success(f"✅ Data ID Petak '{id_petak}' (SPK: {spk_val}) berhasil disimpan!")
                
                st.rerun()

# 2. MENU KHUSUS USER: INPUT / LENGKAPI NOMOR SPK
with st.expander("📋 Lengkapi Nomor SPK yang Belum Terisi", expanded=False):
    if df.empty:
        st.info("Belum ada data kegiatan.")
    else:
        # Cari data yang SPK-nya masih kosong (-) milik user yang sedang login
        spk_series = df["SPK"].astype(str).str.strip()
        empty_spk_mask = df["SPK"].isna() | (spk_series == "") | (spk_series == "-") | (spk_series == "None") | (spk_series == "nan")
        user_mask = df["Penanggung Jawab"].astype(str).str.strip().str.upper() == st.session_state["user_pj"].strip().upper()
        
        unfilled_df = df[user_mask & empty_spk_mask]
        
        if unfilled_df.empty:
            st.success("🎉 Semua kegiatan milik Anda sudah memiliki Nomor SPK!")
        else:
            st.warning(f"📌 Terdapat **{len(unfilled_df)} kegiatan** milik Anda yang belum diisi Nomor SPK-nya.")
            
            # Buat opsi dropdown kegiatan tanpa SPK
            options_spk = {}
            for idx, row in unfilled_df.iterrows():
                label = f"ID Petak: {row['ID Petak']} | Kegiatan: {row['Jenis Kegiatan']} | Luas: {row['Luas']} Ha"
                options_spk[label] = idx
            
            selected_label = st.selectbox("Pilih Kegiatan Tanpa SPK:", list(options_spk.keys()))
            target_idx = options_spk[selected_label]
            
            with st.form("form_update_spk_user"):
                input_spk_baru = st.text_input("Masukkan Nomor SPK Baru *", placeholder="Contoh: SPK/2026/001")
                btn_spk_submit = st.form_submit_button("💾 UPDATE SPK NOW", use_container_width=True)
                
                if btn_spk_submit:
                    if not input_spk_baru.strip():
                        st.error("❌ Nomor SPK tidak boleh kosong!")
                    else:
                        df.at[target_idx, "SPK"] = input_spk_baru.strip()
                        conn.update(worksheet="Sheet1", data=df)
                        st.success(f"✅ Nomor SPK untuk ID Petak '{df.at[target_idx, 'ID Petak']}' berhasil diperbarui menjadi '{input_spk_baru.strip()}'!")
                        st.rerun()

# 3. PANEL ADMINISTRATOR (EDIT / HAPUS)
if is_admin:
    with st.expander("🛠️ Panel Administrator (Edit / Hapus Data)", expanded=False):
        if df.empty:
            st.info("Belum ada data untuk dikelola.")
        else:
            st.subheader("Edit atau Hapus Baris Data")
            
            options_list = [f"Baris {idx + 1} | ID: {row['ID Petak']} | SPK: {row.get('SPK', '-')} | PJ: {row['Penanggung Jawab']} | Kegiatan: {row['Jenis Kegiatan']}" for idx, row in df.iterrows()]
            selected_option = st.selectbox("Pilih Data yang Ingin Di-Edit / Dihapus:", options_list)
            
            selected_idx = options_list.index(selected_option)
            selected_row = df.iloc[selected_idx]
            
            col_act1, col_act2 = st.columns(2)
            
            with col_act2:
                if st.button("🗑️ HAPUS BARIS INI", use_container_width=True):
                    df_dropped = df.drop(selected_idx).reset_index(drop=True)
                    df_dropped["No"] = range(1, len(df_dropped) + 1)
                    conn.update(worksheet="Sheet1", data=df_dropped)
                    st.success("✅ Data berhasil dihapus!")
                    st.rerun()
            
            with col_act1:
                st.caption("Ubah data di bawah ini lalu klik Simpan Perubahan:")
            
            with st.form("form_edit_admin"):
                edit_id = st.text_input("ID Petak", value=str(selected_row.get("ID Petak", "")))
                edit_spk = st.text_input("Nomor SPK", value=str(selected_row.get("SPK", "")))
                edit_pj = st.text_input("Penanggung Jawab", value=str(selected_row.get("Penanggung Jawab", "")))
                edit_luas = st.number_input("Luas (Ha)", value=float(selected_row["Luas"]) if pd.notna(selected_row["Luas"]) else 0.0)
                edit_act_prod = st.number_input("Actual Produktivitas (Ha)", value=float(selected_row["Actual Produktivitas"]) if pd.notna(selected_row["Actual Produktivitas"]) else 0.0)
                
                btn_update = st.form_submit_button("✏️ SIMPAN PERUBAHAN")
                if btn_update:
                    df.at[selected_idx, "ID Petak"] = edit_id.strip()
                    df.at[selected_idx, "SPK"] = edit_spk.strip() if edit_spk.strip() else "-"
                    df.at[selected_idx, "Penanggung Jawab"] = edit_pj.strip()
                    df.at[selected_idx, "Luas"] = edit_luas
                    df.at[selected_idx, "Actual Produktivitas"] = edit_act_prod
                    
                    prod_hari_ini = min(edit_act_prod, edit_luas)
                    sisa_luas = max(0.0, edit_luas - prod_hari_ini)
                    df.at[selected_idx, "Produktivitas Sampai Hari ini"] = prod_hari_ini
                    df.at[selected_idx, "Sisa luas belum dikerjakan"] = sisa_luas
                    
                    conn.update(worksheet="Sheet1", data=df)
                    st.success("✅ Perubahan berhasil disimpan oleh Admin!")
                    st.rerun()

# 4. TABEL MONITORING DATA
st.subheader("📊 Tabel Monitoring Data")

# Alert Banner Pengingat
if not df.empty:
    # 1. Alert On Progress
    if "Sisa luas belum dikerjakan" in df.columns:
        user_mask = df["Penanggung Jawab"].astype(str).str.strip().str.upper() == st.session_state["user_pj"].strip().upper()
        user_df = df[user_mask]
        sisa_series = pd.to_numeric(user_df["Sisa luas belum dikerjakan"], errors="coerce").fillna(0)
        on_progress_count = (sisa_series > 0).sum()
        if on_progress_count > 0:
            st.warning(f"⚠️ **Alert On Progress ({st.session_state['user_pj']})**: Kamu memiliki **{on_progress_count} kegiatan** yang masih berstatus **On Progres**.")

    # 2. Alert Pengingat SPK Kosong
    if "SPK" in df.columns:
        spk_series = df["SPK"].astype(str).str.strip()
        empty_spk_mask = df["SPK"].isna() | (spk_series == "") | (spk_series == "-") | (spk_series == "None") | (spk_series == "nan")
        
        user_empty_spk = df[
            (df["Penanggung Jawab"].astype(str).str.strip().str.upper() == st.session_state["user_pj"].strip().upper()) &
            empty_spk_mask
        ]
        if not user_empty_spk.empty:
            st.error(f"🔔 **PENGINGAT SPK KOSONG**: Terdapat **{len(user_empty_spk)} data** milik kamu yang **Nomor SPK-nya belum terisi!** Silakan lengkapi pada menu **'📋 Lengkapi Nomor SPK'** di atas.")

view_option = st.radio("Tampilkan Data:", ["Khusus Data Saya", "Semua Data Tim"], horizontal=True)

filtered_df = df.copy()

if view_option == "Khusus Data Saya" and not filtered_df.empty:
    filtered_df = filtered_df[
        filtered_df["Penanggung Jawab"].astype(str).str.strip().str.upper() == st.session_state["user_pj"].strip().upper()
    ]

search_term = st.text_input("🔍 Cari Data:", placeholder="Ketik ID Petak / SPK / Kegiatan / Status...")

if search_term and not filtered_df.empty:
    filtered_df = filtered_df[
        filtered_df["ID Petak"].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df["SPK"].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df["Penanggung Jawab"].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df["Jenis Kegiatan"].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df["Rincian"].astype(str).str.contains(search_term, case=False, na=False)
    ]

st.caption("💡 *Tip: Geser tabel ke kanan/kiri untuk melihat kolom selengkapnya.*")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
