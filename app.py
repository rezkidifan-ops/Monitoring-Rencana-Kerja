import pandas as pd
from datetime import datetime
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Pengaturan Halaman
st.set_page_config(page_title="Monitoring & Rencana Kerja", layout="wide")

st.title("🚜 Sistem Monitoring & Rencana Kerja")
st.markdown("Pencatatan dan pemantauan kegiatan petak kerja secara real-time.")

# 1. Koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Daftar Kolom Lengkap
COLUMNS = [
    "No", "ID Petak", "Jenis Kegiatan", "Luas", "Penanggung Jawab",
    "Tanggal Rencana Kerja", "Tanggal Mulai Bekerja", "Tanggal Selesai Kerja",
    "Rencana Tenaga Kerja", "Actual Tenaga Kerja", "Rencana Produktivitas",
    "Actual Produktivitas", "Produktivitas Sampai Hari ini", 
    "Sisa luas belum dikerjakan", "Rincian"
]

def load_data():
    try:
        # Membaca tab Sheet1 secara spesifik
        df = conn.read(worksheet="Sheet1", ttl=0)
        
        if df is None or df.empty:
            return pd.DataFrame(columns=COLUMNS)
            
        # Pastikan semua kolom yang dibutuhkan ada
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
                
        return df[COLUMNS]
    except Exception as e:
        st.error(f"Eror Koneksi: {e}")
        return pd.DataFrame(columns=COLUMNS)

df = load_data()

# 2. Form Input Data di Halaman Utama (Header Lipat / Expander)
with st.expander("📝 Klik di sini untuk Input Rencana & Realisasi Kerja", expanded=False):
    with st.form("form_monitoring", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            id_petak = st.text_input("ID Petak *")
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
            luas = st.number_input("Luas (Ha)", min_value=0.0, step=0.1)
        with col2:
            pj = st.text_input("Penanggung Jawab *")
            rincian = st.text_area("Rincian / Catatan Tambahan", height=100)
        
        st.markdown("---")
        st.subheader("📅 Jadwal Kerja")
        col3, col4, col5 = st.columns(3)
        with col3:
            tgl_rencana = st.date_input("Tanggal Rencana Kerja")
        with col4:
            tgl_mulai = st.date_input("Tanggal Mulai Bekerja")
        with col5:
            tgl_selesai = st.date_input("Tanggal Selesai Kerja")
        
        st.markdown("---")
        st.subheader("👥 Tenaga Kerja & Produktivitas")
        col6, col7 = st.columns(2)
        with col6:
            rencana_tk = st.number_input("Rencana Tenaga Kerja (Orang)", min_value=0, step=1)
            rencana_prod = st.number_input("Rencana Produktivitas", min_value=0.0, step=0.1)
            prod_hari_ini = st.number_input("Produktivitas Sampai Hari Ini", min_value=0.0, step=0.1)
        with col7:
            actual_tk = st.number_input("Actual Tenaga Kerja (Orang)", min_value=0, step=1)
            actual_prod = st.number_input("Actual Produktivitas", min_value=0.0, step=0.1)
            sisa_luas = st.number_input("Sisa Luas Belum Dikerjakan (Ha)", min_value=0.0, step=0.1)
        
        submitted = st.form_submit_button("💾 Simpan Data")

        if submitted:
            if not id_petak or not pj:
                st.error("ID Petak dan Penanggung Jawab wajib diisi!")
            else:
                no_baru = len(df) + 1 if not df.empty else 1
                
                new_row = pd.DataFrame([{
                    "No": no_baru,
                    "ID Petak": id_petak,
                    "Jenis Kegiatan": jenis_kegiatan,
                    "Luas": luas,
                    "Penanggung Jawab": pj,
                    "Tanggal Rencana Kerja": tgl_rencana.strftime("%Y-%m-%d"),
                    "Tanggal Mulai Bekerja": tgl_mulai.strftime("%Y-%m-%d"),
                    "Tanggal Selesai Kerja": tgl_selesai.strftime("%Y-%m-%d"),
                    "Rencana Tenaga Kerja": rencana_tk,
                    "Actual Tenaga Kerja": actual_tk,
                    "Rencana Produktivitas": rencana_prod,
                    "Actual Produktivitas": actual_prod,
                    "Produktivitas Sampai Hari ini": prod_hari_ini,
                    "Sisa luas belum dikerjakan": sisa_luas,
                    "Rincian": rincian
                }])
                
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("Data berhasil disimpan ke Google Sheets!")
                st.rerun()

# 3. Tampilan Data Utama & Pencarian
st.subheader("📊 Tabel Data Monitoring Kerja")

search_term = st.text_input("🔍 Cari berdasarkan ID Petak, Penanggung Jawab, atau Jenis Kegiatan:")

filtered_df = df.copy()
if search_term and not filtered_df.empty:
    filtered_df = filtered_df[
        filtered_df["ID Petak"].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df["Penanggung Jawab"].astype(str).str.contains(search_term, case=False, na=False) |
        filtered_df["Jenis Kegiatan"].astype(str).str.contains(search_term, case=False, na=False)
    ]

st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# 4. Ringkasan Metrik Utama (Aman dari Eror Tipe Data Teks)
st.markdown("---")
st.subheader("📈 Ringkasan")

total_luas = pd.to_numeric(df["Luas"], errors="coerce").fillna(0).sum() if not df.empty else 0
total_r_tk = pd.to_numeric(df["Rencana Tenaga Kerja"], errors="coerce").fillna(0).sum() if not df.empty else 0
total_a_tk = pd.to_numeric(df["Actual Tenaga Kerja"], errors="coerce").fillna(0).sum() if not df.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Petak", len(df))
c2.metric("Total Luas", f"{total_luas:,.2f} Ha")
c3.metric("Total Rencana TK", int(total_r_tk))
c4.metric("Total Actual TK", int(total_a_tk))
