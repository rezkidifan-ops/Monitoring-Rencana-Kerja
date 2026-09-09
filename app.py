import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

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
        df = conn.read(ttl=0)
        # Pastikan kolom sesuai
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[COLUMNS]
    except Exception as e:
        st.error("Gagal terhubung ke Google Sheets. Pastikan header di Google Sheets sudah sesuai.")
        return pd.DataFrame(columns=COLUMNS)

df = load_data()

# 2. Form Input Data di Sidebar
st.sidebar.header("➕ Input Rencana & Realisasi Kerja")

with st.sidebar.form("form_monitoring", clear_on_submit=True):
    id_petak = st.text_input("ID Petak *")
    jenis_kegiatan = st.selectbox("Jenis Kegiatan", [
        "Persiapan Lahan", "Penanaman", "Pemeliharaan", 
        "Pemupukan", "Pemanenan", "Lainnya"
    ])
    luas = st.number_input("Luas (Ha)", min_value=0.0, step=0.1)
    pj = st.text_input("Penanggung Jawab *")
    
    st.markdown("---")
    st.subheader("📅 Jadwal Kerja")
    tgl_rencana = st.date_input("Tanggal Rencana Kerja")
    tgl_mulai = st.date_input("Tanggal Mulai Bekerja")
    tgl_selesai = st.date_input("Tanggal Selesai Kerja")
    
    st.markdown("---")
    st.subheader("👥 Tenaga Kerja & Produktivitas")
    rencana_tk = st.number_input("Rencana Tenaga Kerja (Orang)", min_value=0, step=1)
    actual_tk = st.number_input("Actual Tenaga Kerja (Orang)", min_value=0, step=1)
    
    rencana_prod = st.number_input("Rencana Produktivitas", min_value=0.0, step=0.1)
    actual_prod = st.number_input("Actual Produktivitas", min_value=0.0, step=0.1)
    prod_hari_ini = st.number_input("Produktivitas Sampai Hari Ini", min_value=0.0, step=0.1)
    sisa_luas = st.number_input("Sisa Luas Belum Dikerjakan (Ha)", min_value=0.0, step=0.1)
    
    rincian = st.text_area("Rincian / Catatan Tambahan")
    
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
            conn.update(data=updated_df)
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

# 4. Ringkasan Metrik Utama
st.markdown("---")
st.subheader("📈 Ringkasan")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Petak", len(df))
c2.metric("Total Luas", f"{df['Luas'].sum():,.2f} Ha" if not df.empty else "0 Ha")
c3.metric("Total Rencana TK", int(df['Rencana Tenaga Kerja'].sum()) if not df.empty else 0)
c4.metric("Total Actual TK", int(df['Actual Tenaga Kerja'].sum()) if not df.empty else 0)
