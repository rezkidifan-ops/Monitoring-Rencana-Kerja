from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# =========================================================
# KONFIGURASI URL GOOGLE SHEET
# =========================================================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1qJMHdTkURQV7LQE_DfO3UiX_txepHVCXqRct3mrQlxs/edit?usp=drivesdk"

# 1. PENGATURAN HALAMAN
st.set_page_config(
    page_title="Eucasystem Monitoring",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. TEMA DESAIN & CUSTOM CSS (MENCEGAH KOLOM MENUMPUK DI ANDROID)
st.markdown(
    """<style>
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

/* ================= PAKSA KOLOM TETAP SEJAJAR DI MOBILE ================= */
@media (max-width: 640px) {
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        align-items: center !important;
        gap: 8px !important;
    }
    div[data-testid="stColumn"] {
        flex: 1 !important;
        min-width: 0 !important;
    }
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

@keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
.alert-sidebar-panel {
    animation: slideInRight 0.3s ease-out;
    background-color: #1e1e1e;
    padding: 20px;
    border-radius: 10px;
    border-left: 4px solid #C8102E;
    margin-bottom: 20px;
    color: white;
}
</style>""",
    unsafe_allow_html=True,
)

# 3. KONEKSI GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

COLUMNS = [
    "No",
    "ID Petak",
    "SPK",
    "Jenis Kegiatan",
    "Luas",
    "Lokasi",
    "Keterangan",
    "Username",
    "Tanggal Rencana Kerja",
    "Tanggal Mulai Bekerja",
    "Tanggal Selesai Kerja",
    "Rencana Tenaga Kerja",
    "Actual Tenaga Kerja",
    "Rencana Produktivitas",
    "Actual Produktivitas",
    "Produktivitas Sampai Hari ini",
    "Sisa luas belum dikerjakan",
    "Rincian",
]

USER_COLUMNS = ["Username", "Password", "Role"]


def safe_gsheets_update(worksheet_name, data_df):
  try:
    conn.update(
        spreadsheet=SPREADSHEET_URL, worksheet=worksheet_name, data=data_df
    )
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
    df_users["Password"] = (
        df_users["Password"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )
    return df_users[USER_COLUMNS]
  except Exception as e:
    return pd.DataFrame(columns=USER_COLUMNS)


# 4. INISIALISASI SESI LOGIN & NAVIGASI
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
if "user_pj" not in st.session_state:
  st.session_state["user_pj"] = ""
if "user_role" not in st.session_state:
  st.session_state["user_role"] = "User"
if "active_menu" not in st.session_state:
  st.session_state["active_menu"] = "Input ID Petak"
if "show_alert_sidebar" not in st.session_state:
  st.session_state["show_alert_sidebar"] = False

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
  st.markdown(
      f"""<div class="intro-banner-eucalyptus">
<div class="banner-content">
<div class="motto-badge-red">WE CARE • WE DO • WE WIN</div>
<h1>Eucasystem Monitoring</h1>
<p>DISTRIK PULAU PUSAT</p>
</div>
{EUCALYPTUS_SVG}
</div>""",
      unsafe_allow_html=True,
  )

  tab_login, tab_register = st.tabs(["Login", "Daftar"])

  with tab_login:
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
                (
                    df_users["Username"].str.upper()
                    == pj_input.strip().upper()
                )
                & (df_users["Password"] == kode_input.strip())
            ]
            if not matched.empty:
              st.session_state["logged_in"] = True
              st.session_state["user_pj"] = matched.iloc[0]["Username"]
              role_val = matched.iloc[0].get("Role", "User")
              st.session_state["user_role"] = (
                  role_val if pd.notna(role_val) else "User"
              )
              st.success(f"Selamat datang, {st.session_state['user_pj']}.")
              st.rerun()
            else:
              st.error("Username atau Password tidak valid.")
          else:
            st.error(
                "Data pengguna tidak ditemukan. Silakan lakukan pendaftaran"
                " akun."
            )

  with tab_register:
    with st.form("form_register"):
      reg_pj = st.text_input(
          "Username", placeholder="Contoh: Rezki Difan Arshaf"
      )
      reg_kode = st.text_input(
          "Password", type="password", placeholder="Minimal 4 karakter"
      )
      btn_reg = st.form_submit_button("Daftar Akun", use_container_width=True)

      if btn_reg:
        if not reg_pj.strip() or not reg_kode.strip():
          st.error("Username dan Password wajib diisi.")
        else:
          df_users = load_users()
          if not df_users.empty and "Username" in df_users.columns:
            exists = df_users[
                df_users["Username"].str.upper() == reg_pj.strip().upper()
            ]
            if not exists.empty:
              st.error(
                  f"Username '{reg_pj}' sudah terdaftar. Silakan gunakan menu"
                  " Login."
              )
              st.stop()

          new_user = pd.DataFrame([{
              "Username": reg_pj.strip(),
              "Password": str(reg_kode.strip()),
              "Role": "User",
          }])
          updated_users = pd.concat([df_users, new_user], ignore_index=True)
          try:
            safe_gsheets_update("Users", updated_users)
            st.success("Pendaftaran berhasil! Silakan pindah ke tab Login.")
          except Exception as e:
            st.error(f"Gagal menyimpan data pengguna: {e}")

  st.stop()

# =========================================================
# DASHBOARD & OPERASIONAL UTAMA (SETELAH LOGIN)
# =========================================================
st.markdown(
    """<style>
.stApp {
    background: 
        radial-gradient(circle at 10% 15%, rgba(46, 90, 54, 0.22) 0%, transparent 45%),
        radial-gradient(circle at 90% 85%, rgba(200, 16, 46, 0.18) 0%, transparent 45%),
        radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.9) 0%, rgba(240, 247, 242, 1) 100%) !important;
    background-attachment: fixed !important;
}
</style>""",
    unsafe_allow_html=True,
)

df = load_data()
is_admin = (
    str(st.session_state.get("user_role", "User")).strip().lower() == "admin"
)
role_badge = "Administrator" if is_admin else "Field Officer"

# Hitung jumlah Alert SPK Kosong
alert_count = 0
if not df.empty:
  spk_series = df["SPK"].astype(str).str.strip()
  empty_spk = (
      df["SPK"].isna()
      | (spk_series == "")
      | (spk_series == "-")
      | (spk_series == "None")
      | (spk_series == "nan")
  )
  has_prod = (
      pd.to_numeric(df["Actual Produktivitas"], errors="coerce").fillna(0) > 0
  ) | (
      df["Jenis Kegiatan"].notnull() & (df["Jenis Kegiatan"] != "")
  )
  alert_count = len(df[has_prod & empty_spk])

# Top Bar: Banner, Tombol Lonceng Alert, dan Tombol Keluar (Sejajar)
col_banner, col_alert, col_logout = st.columns(
    [7.8, 1.1, 1.1], vertical_alignment="center"
)

with col_banner:
  st.markdown(
      f"""<div class="intro-banner-eucalyptus" style="margin-bottom: 0;">
    <div class="banner-content">
    <div class="motto-badge-red">WE CARE • WE DO • WE WIN</div>
    <h1>Eucasystem Monitoring</h1>
    <p>DISTRIK PULAU PUSAT</p>
    <hr style="border-color: rgba(255,255,255,0.2); margin: 6px 0;">
    <p style="font-size: 13px;">{st.session_state['user_pj']} | {role_badge}</p>
    </div>
    </div>""",
      unsafe_allow_html=True,
  )

with col_alert:
  bell_label = f"🔔 {alert_count}" if alert_count > 0 else "🔔"
  if st.button(
      bell_label, use_container_width=True, help="Alert Petak Belum Ada SPK"
  ):
    st.session_state["show_alert_sidebar"] = not st.session_state[
        "show_alert_sidebar"
    ]
    st.rerun()

with col_logout:
  if st.button("🚪 Keluar", use_container_width=True, type="secondary"):
    st.session_state["logged_in"] = False
    st.session_state["user_pj"] = ""
    st.session_state["user_role"] = "User"
    st.rerun()

st.write("")

# Panel Sidebar Alert
if st.session_state["show_alert_sidebar"]:
  st.markdown(
      """
        <div class="alert-sidebar-panel">
            <h3>🚨 Alert: Petak Belum Memiliki SPK</h3>
            <p style="font-size: 13px; color: #ccc;">Daftar ID Petak yang sudah terisi kegiatan/produktivitas namun nomor SPK-nya masih kosong:</p>
        </div>
    """,
      unsafe_allow_html=True,
  )
  if not df.empty:
    spk_series = df["SPK"].astype(str).str.strip()
    empty_spk = (
        df["SPK"].isna()
        | (spk_series == "")
        | (spk_series == "-")
        | (spk_series == "None")
        | (spk_series == "nan")
    )
    has_prod = (
        pd.to_numeric(df["Actual Produktivitas"], errors="coerce").fillna(0) > 0
    ) | (df["Jenis Kegiatan"].notnull() & (df["Jenis Kegiatan"] != ""))
    alert_df = df[has_prod & empty_spk]
    if not alert_df.empty:
      st.dataframe(
          alert_df[[
              "ID Petak",
              "Jenis Kegiatan",
              "Tanggal Rencana Kerja",
              "Actual Produktivitas",
          ]],
          use_container_width=True,
          hide_index=True,
      )
    else:
      st.success("Tidak ada petak yang memerlukan perhatian SPK.")
  else:
    st.info("Belum ada data di database.")

  if st.button("Tutup Panel Alert"):
    st.session_state["show_alert_sidebar"] = False
    st.rerun()
  st.markdown("---")

# =========================================================
# NAVIGASI MENU UTAMA (SEJAJAR DALAM 1 BARIS)
# =========================================================
b_col1, b_col2, b_col3 = st.columns(3)

with b_col1:
  if st.button("📝 Input ID Petak", use_container_width=True):
    st.session_state["active_menu"] = "Input ID Petak"
    st.rerun()

with b_col2:
  if st.button("📊 Rencana Kerja", use_container_width=True):
    st.session_state["active_menu"] = "Rencana Kerja"
    st.rerun()

with b_col3:
  if st.button("📅 Jadwal Kerja Selanjutnya", use_container_width=True):
    st.session_state["active_menu"] = "Jadwal Kerja Selanjutnya"
    st.rerun()

st.write("")

active_menu = st.session_state["active_menu"]

# =========================================================
# KONTEN 1: INPUT ID PETAK
# =========================================================
if active_menu == "Input ID Petak":
  st.subheader("Formulir Pendaftaran ID Petak")

  with st.form("form_input_id_petak", clear_on_submit=True):
    col_f1, col_f2 = st.columns(2)

    with col_f1:
      id_petak = st.text_input("ID Petak", placeholder="Contoh: EUC-A01")
      jenis_kegiatan = st.selectbox(
          "Jenis Kegiatan",
          [
              "Established - PLTB",
              "Established - Kuku Macan",
              "Established - Parit",
              "Established - Teras",
              "Established - Lining+Sticking",
              "Established - Tanam",
              "Established - Tanam & Aquasorb",
              "Established - Sulam",
              "Established - PPS",
              "Established - PPS Dron",
              "Maintenance - MW 1",
              "Maintenance - CW 1",
              "Maintenance - CW 2",
              "Maintenance - CW 3",
              "Maintenance - CW 4",
              "Maintenance - CW 5",
              "Maintenance - CW 6",
              "Maintenance - CW 7",
              "Maintenance - MW 2",
              "Maintenance - MW 3",
              "Maintenance - PS1",
              "Maintenance - PS1 drone",
              "Maintenance - HPT",
              "Maintenance - HPT Drone",
              "Maintenance - PS2 Drone",
              "Maintenance - PS 2",
              "Lainnya",
          ],
      )
      luas = st.number_input("Luas Area (Ha)", min_value=0.0, step=0.1)

    with col_f2:
      lokasi = st.text_input("Lokasi / Wilayah", placeholder="Contoh: Sektor Utara")
      keterangan = st.text_area("Keterangan Tambahan", height=105)

    submitted_petak = st.form_submit_button(
        "Simpan ID Petak", use_container_width=True
    )

    if submitted_petak:
      if not id_petak.strip() or luas <= 0:
        st.error("ID Petak dan Luas wajib diisi dengan benar.")
      else:
        pj_final = st.session_state["user_pj"]
        no_baru = len(df) + 1 if not df.empty else 1

        new_row = pd.DataFrame([{
            "No": no_baru,
            "ID Petak": id_petak.strip(),
            "SPK": "-",
            "Jenis Kegiatan": jenis_kegiatan,
            "Luas": luas,
            "Lokasi": lokasi.strip(),
            "Keterangan": keterangan.strip(),
            "Username": pj_final,
            "Tanggal Rencana Kerja": str(datetime.date.today()),
            "Tanggal Mulai Bekerja": str(datetime.date.today()),
            "Tanggal Selesai Kerja": str(datetime.date.today()),
            "Rencana Tenaga Kerja": 0,
            "Actual Tenaga Kerja": 0,
            "Rencana Produktivitas": 0.0,
            "Actual Produktivitas": 0.0,
            "Produktivitas Sampai Hari ini": 0.0,
            "Sisa luas belum dikerjakan": luas,
            "Rincian": "On Progres - Petak terdaftar",
        }])

        updated_df = pd.concat([df, new_row], ignore_index=True)
        safe_gsheets_update("Sheet1", updated_df)
        st.success(
            f"ID Petak '{id_petak}' dengan jenis kegiatan '{jenis_kegiatan}'"
            " berhasil didaftarkan."
        )
        st.rerun()

  st.markdown("### Daftar ID Petak Terdaftar")
  if not df.empty:
    st.dataframe(
        df[["ID Petak", "Jenis Kegiatan", "Luas", "Lokasi", "Keterangan"]],
        use_container_width=True,
        hide_index=True,
    )
  else:
    st.info("Belum ada data petak yang terdaftar.")

# =========================================================
# KONTEN 2: RENCANA KERJA
# =========================================================
elif active_menu == "Rencana Kerja":
  st.subheader("Rencana Kerja & Alokasi Tenaga Kerja")

  if df.empty:
    st.warning(
        "Silakan daftarkan ID Petak terlebih dahulu pada menu 'Input ID Petak'."
    )
  else:
    list_petak_tersedia = df["ID Petak"].dropna().unique().tolist()

    with st.form("form_rencana_kerja"):
      selected_petak = st.selectbox(
          "Pilih ID Petak Terdaftar", list_petak_tersedia
      )

      col_rk1, col_rk2 = st.columns(2)
      with col_rk1:
        spk_input = st.text_input(
            "Nomor SPK", placeholder="Contoh: SPK/EUC/2026/001"
        )
        tgl_rencana = st.date_input(
            "Tanggal Rencana Kerja", value=datetime.date.today()
        )
        tgl_mulai = st.date_input(
            "Tanggal Mulai Bekerja", value=datetime.date.today()
        )
        tgl_selesai = st.date_input(
            "Tanggal Selesai Kerja", value=datetime.date.today()
        )
      with col_rk2:
        rencana_tk = st.number_input(
            "Rencana Tenaga Kerja (Orang)", min_value=0, step=1
        )
        actual_tk = st.number_input(
            "Aktual Tenaga Kerja (Orang)", min_value=0, step=1
        )
        rencana_prod = st.number_input(
            "Rencana Produktivitas (Ha)", min_value=0.0, step=0.1
        )
        actual_prod = st.number_input(
            "Aktual Produktivitas (Ha)", min_value=0.0, step=0.1
        )

      rincian_input = st.text_area("Catatan Operasional", height=80)

      submit_rencana = st.form_submit_button(
          "Simpan Rencana Kerja", use_container_width=True
      )

      if submit_rencana:
        matched_idx = df[
            df["ID Petak"].astype(str).str.strip()
            == str(selected_petak).strip()
        ].index
        if not matched_idx.empty:
          idx = matched_idx[0]
          luas_petak = float(
              df.loc[idx, "Luas"] if pd.notna(df.loc[idx, "Luas"]) else 0.0
          )

          prev_actual = pd.to_numeric(
              df.loc[idx, "Actual Produktivitas"], errors="coerce"
          )
          if pd.isna(prev_actual):
            prev_actual = 0.0

          prod_kumulatif = prev_actual + actual_prod
          prod_hari_ini = min(
              prod_kumulatif,
              luas_petak if luas_petak > 0 else prod_kumulatif,
          )
          sisa_luas = max(
              0.0,
              (luas_petak - prod_hari_ini) if luas_petak > 0 else 0.0,
          )

          status_kerja = "Complete" if sisa_luas <= 0 else "On Progres"
          final_rincian = (
              f"{status_kerja} - {rincian_input.strip()}"
              if rincian_input.strip()
              else status_kerja
          )

          df.loc[idx, "SPK"] = (
              spk_input.strip() if spk_input.strip() else df.loc[idx, "SPK"]
          )
          df.loc[idx, "Tanggal Rencana Kerja"] = tgl_rencana.strftime("%Y-%m-%d")
          df.loc[idx, "Tanggal Mulai Bekerja"] = tgl_mulai.strftime("%Y-%m-%d")
          df.loc[idx, "Tanggal Selesai Kerja"] = tgl_selesai.strftime("%Y-%m-%d")
          df.loc[idx, "Rencana Tenaga Kerja"] = rencana_tk
          df.loc[idx, "Actual Tenaga Kerja"] = actual_tk
          df.loc[idx, "Rencana Produktivitas"] = rencana_prod
          df.loc[idx, "Actual Produktivitas"] = actual_prod
          df.loc[idx, "Produktivitas Sampai Hari ini"] = prod_kumulatif
          df.loc[idx, "Sisa luas belum dikerjakan"] = sisa_luas
          df.loc[idx, "Rincian"] = final_rincian

          safe_gsheets_update("Sheet1", df)
          st.success(
              f"Rencana kerja untuk ID Petak '{selected_petak}' berhasil"
              " diperbarui."
          )
          st.rerun()

    st.markdown("### Rekapitulasi Rencana Kerja")
    if not df.empty:
      df_display = df.copy()
      df_display["Bulan"] = (
          pd.to_datetime(df_display["Tanggal Rencana Kerja"], errors="coerce")
          .dt.to_period("M")
          .astype(str)
      )
      df_display["Hari"] = pd.to_datetime(
          df_display["Tanggal Rencana Kerja"], errors="coerce"
      ).dt.day

      st.dataframe(
          df_display[[
              "Bulan",
              "Hari",
              "ID Petak",
              "SPK",
              "Jenis Kegiatan",
              "Rencana Tenaga Kerja",
              "Actual Tenaga Kerja",
              "Rencana Produktivitas",
              "Actual Produktivitas",
              "Rincian",
          ]],
          use_container_width=True,
          hide_index=True,
      )

# =========================================================
# KONTEN 3: JADWAL KERJA SELANJUTNYA
# =========================================================
elif active_menu == "Jadwal Kerja Selanjutnya":
  st.subheader("Jadwal Kerja Selanjutnya")
  st.write("Kelengkapan nomor SPK dan pemantauan operasional lanjutan.")

  if df.empty:
    st.info("Belum terdapat data kegiatan.")
  else:
    spk_series = df["SPK"].astype(str).str.strip()
    empty_spk_mask = (
        df["SPK"].isna()
        | (spk_series == "")
        | (spk_series == "-")
        | (spk_series == "None")
        | (spk_series == "nan")
    )
    user_mask = (
        df["Username"].astype(str).str.strip().str.upper()
        == st.session_state["user_pj"].strip().upper()
    )

    unfilled_df = df[user_mask & empty_spk_mask]

    if unfilled_df.empty:
      st.info("Seluruh kegiatan Anda telah memiliki Nomor SPK.")
    else:
      options_spk = {}
      for idx, row in unfilled_df.iterrows():
        label = f"ID: {row['ID Petak']} | Kegiatan: {row['Jenis Kegiatan']} | Luas: {row['Luas']} Ha"
        options_spk[label] = idx

      selected_label = st.selectbox(
          "Pilih Kegiatan Tanpa SPK", list(options_spk.keys())
      )
      target_idx = options_spk[selected_label]

      with st.form("form_update_spk_user"):
        input_spk_baru = st.text_input(
            "Nomor SPK Baru", placeholder="Contoh: SPK/EUC/2026/001"
        )
        btn_spk_submit = st.form_submit_button(
            "Perbarui SPK", use_container_width=True
        )

        if btn_spk_submit:
          if not input_spk_baru.strip():
            st.error("Nomor SPK tidak boleh kosong.")
          else:
            df.at[target_idx, "SPK"] = input_spk_baru.strip()
            safe_gsheets_update("Sheet1", df)
            st.success("Nomor SPK berhasil diperbarui.")
            st.rerun()
