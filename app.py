import datetime
import json
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components

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

# 2. TEMA DESAIN & CUSTOM CSS
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

header[data-testid="stHeader"],
div[data-testid="stToolbar"],
#MainMenu,
footer,
.stAppHeader,
[data-testid="stHeaderActionElements"],
[data-testid="stFooter"],
div.viewerBadge_container__1QSob,
a[href*="streamlit.io/cloud"] {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
}

[data-testid="InputInstructions"] {
    display: none !important;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    font-size: 13px !important;
}

.stApp {
    background: linear-gradient(180deg, #F4F7F4 0%, #E9EFE9 100%);
}

.main .block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 2rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
    max-width: 1200px;
}

@media (max-width: 640px) {
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        align-items: center !important;
        gap: 6px !important;
    }
    div[data-testid="stColumn"] {
        flex: 1 !important;
        min-width: 0 !important;
    }
}

.stButton > button {
    font-weight: 600 !important;
    font-size: 12.5px !important;
    border-radius: 6px !important;
    border: 1px solid rgba(46, 90, 54, 0.2) !important;
    padding: 0.35rem 0.7rem !important;
}

.intro-banner-eucalyptus {
    background: linear-gradient(135deg, #1B3B22 0%, #2E5A36 60%, #990000 100%);
    color: #FFFFFF;
    padding: 1rem 1.2rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(46, 90, 54, 0.15);
    margin-bottom: 1rem;
    border-bottom: 3px solid #C8102E;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
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
    font-weight: 700 !important;
    font-size: 0.65rem !important;
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    white-space: nowrap;
}

.intro-banner-eucalyptus h1 {
    color: #FFFFFF !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    line-height: 1.2;
    word-wrap: break-word;
}

.intro-banner-eucalyptus p {
    color: #F8F9FA !important;
    margin: 0.3rem 0 0 0 !important;
    font-size: 0.78rem;
    font-weight: 400;
    opacity: 0.95;
    word-break: break-word;
}

.eucalyptus-tree-svg {
    width: 50px;
    height: 50px;
    flex-shrink: 0;
    filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.2));
}

@keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
.alert-sidebar-panel {
    animation: slideInRight 0.3s ease-out;
    background-color: #1e1e1e;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #C8102E;
    margin-bottom: 15px;
    color: white;
}

h2 {
    font-size: 1.15rem !important;
    font-weight: 600 !important;
}
h3 {
    font-size: 1rem !important;
    font-weight: 600 !important;
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
    "Rencana Alat Berat",
    "Rencana Operator",
    "Actual Tenaga Kerja",
    "Actual Alat Berat",
    "Actual Operator",
    "Rencana Produktivitas",
    "Actual Produktivitas",
    "Produktivitas Sampai Hari ini",
    "Sisa luas belum dikerjakan",
    "Rincian",
]

USER_COLUMNS = ["Username", "Password", "Role"]

SCHEDULE_RULES = [
    {"activity": "Pupuk", "days_offset": 3, "label": "Umur 0-7 hari"},
    {"activity": "Sulam", "days_offset": 3, "label": "Umur 0-7 hari"},
    {"activity": "Manual Weeding 1", "days_offset": 30, "label": "Umur 1 bulan (Optional)"},
    {"activity": "Chemical Weeding 1", "days_offset": 45, "label": "Umur 1-2 bulan"},
    {"activity": "Pupuk Susulan 1", "days_offset": 90, "label": "Umur 3 bulan"},
    {"activity": "Chemical Weeding 2", "days_offset": 135, "label": "Umur 4-5 bulan"},
    {"activity": "Chemical Weeding 3", "days_offset": 225, "label": "Umur 7-8 bulan"},
    {"activity": "Pupuk Susulan 2", "days_offset": 270, "label": "Umur 9 bulan"},
    {"activity": "Chemical Weeding 4", "days_offset": 345, "label": "Umur 11-12 bulan"},
    {"activity": "Chemical Weeding 5", "days_offset": 465, "label": "Umur 15-16 bulan"},
    {"activity": "Chemical Weeding 6", "days_offset": 615, "label": "Umur 20-21 bulan"},
    {"activity": "Chemical Weeding 7", "days_offset": 810, "label": "Umur 26-28 bulan"},
]

if "offline_queue" not in st.session_state:
  st.session_state["offline_queue"] = []

components.html(
    """
<script>
const updateOnlineStatus = () => {
    const status = navigator.onLine ? "ONLINE" : "OFFLINE";
    const parentDoc = window.parent.document;
    let badge = parentDoc.getElementById('net-status-badge');
    if (!badge) {
        badge = parentDoc.createElement('div');
        badge.id = 'net-status-badge';
        badge.style.position = 'fixed';
        badge.style.bottom = '10px';
        badge.style.right = '10px';
        badge.style.zIndex = '99999';
        badge.style.padding = '5px 10px';
        badge.style.borderRadius = '6px';
        badge.style.fontSize = '11px';
        badge.style.fontWeight = 'bold';
        badge.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
        parentDoc.body.appendChild(badge);
    }
    if (navigator.onLine) {
        badge.style.backgroundColor = '#2E5A36';
        badge.style.color = '#FFFFFF';
        badge.innerText = '🟢 Online (Server Terhubung)';
    } else {
        badge.style.backgroundColor = '#C8102E';
        badge.style.color = '#FFFFFF';
        badge.innerText = '🔴 Offline (Mode Lokal Aktif)';
    }
};
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);
updateOnlineStatus();
</script>
""",
    height=0,
)


def safe_gsheets_update(worksheet_name, data_df):
  try:
    conn.update(
        spreadsheet=SPREADSHEET_URL, worksheet=worksheet_name, data=data_df
    )
    return True
  except Exception as e:
    return False


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

    if "SPK" in df.columns:
      df["SPK"] = (
          df["SPK"]
          .astype(str)
          .str.replace(r"\.0$", "", regex=True)
          .str.strip()
      )
      df["SPK"] = df["SPK"].replace(["nan", "None", ""], "-")

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
            st.session_state["logged_in"] = True
            st.session_state["user_pj"] = pj_input.strip()
            st.session_state["user_role"] = "User"
            st.warning("Mode Offline: Login dilewati berdasarkan cache lokal.")
            st.rerun()

  with tab_register:
    with st.form("form_register"):
      reg_pj = st.text_input("Username", placeholder="Contoh: Rezki Difan Arshaf")
      reg_kode = st.text_input("Password", type="password", placeholder="Minimal 4 karakter")
      btn_reg = st.form_submit_button("Daftar Akun", use_container_width=True)

      if btn_reg:
        if not reg_pj.strip() or not reg_kode.strip():
          st.error("Username dan Password wajib diisi.")
        else:
          df_users = load_users()
          new_user = pd.DataFrame([{
              "Username": reg_pj.strip(),
              "Password": str(reg_kode.strip()),
              "Role": "User",
          }])
          updated_users = (
              pd.concat([df_users, new_user], ignore_index=True)
              if not df_users.empty
              else new_user
          )
          if safe_gsheets_update("Users", updated_users):
            st.success("Pendaftaran berhasil! Silakan login.")
          else:
            st.session_state["offline_queue"].append(
                {"type": "register", "data": new_user.to_dict()}
            )
            st.warning(
                "Offline: Akun disimpan ke antrean lokal dan akan disinkronkan"
                " saat terhubung ke jaringan."
            )

  st.stop()

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

if st.session_state["offline_queue"]:
  st.warning(
      f"⚠️ Ada {len(st.session_state['offline_queue'])} data dalam antrean"
      " offline."
  )
  if st.button("🔄 Sinkronisasi Data ke Server Sekarang"):
    try:
      current_df = load_data()
      for item in st.session_state["offline_queue"]:
        if item["type"] == "sheet1":
          row_df = pd.DataFrame([item["data"]])
          current_df = pd.concat([current_df, row_df], ignore_index=True)
      if safe_gsheets_update("Sheet1", current_df):
        st.session_state["offline_queue"] = []
        st.success("Semua data offline berhasil disinkronkan ke server!")
        st.rerun()
      else:
        st.error(
            "Gagal menyinkronkan. Pastikan perangkat terhubung ke internet."
        )
    except Exception as e:
      st.error(f"Sinkronisasi gagal: {e}")

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

col_spacer, col_alert, col_logout = st.columns([5.6, 2.2, 2.2])

with col_alert:
  alert_btn_label = f"Alert ({alert_count})" if alert_count > 0 else "Alert"
  if st.button(alert_btn_label, use_container_width=True):
    st.session_state["show_alert_sidebar"] = not st.session_state[
        "show_alert_sidebar"
    ]
    st.rerun()

with col_logout:
  if st.button("Keluar", use_container_width=True, type="secondary"):
    st.session_state["logged_in"] = False
    st.session_state["user_pj"] = ""
    st.session_state["user_role"] = "User"
    st.rerun()

st.write("")

st.markdown(
    f"""<div class="intro-banner-eucalyptus">
<div class="banner-content">
<div class="motto-badge-red">WE CARE • WE DO • WE WIN</div>
<h1>Eucasystem Monitoring</h1>
<p>DISTRIK PULAU PUSAT</p>
<hr style="border-color: rgba(255,255,255,0.2); margin: 4px 0;">
<p style="font-size: 11.5px;">{st.session_state['user_pj']} | {role_badge}</p>
</div>
{EUCALYPTUS_SVG}
</div>""",
    unsafe_allow_html=True,
)

if st.session_state["show_alert_sidebar"]:
  st.markdown(
      """
        <div class="alert-sidebar-panel">
            <h3>🚨 Alert: Petak Belum Memiliki SPK</h3>
            <p style="font-size: 12px; color: #ccc;">Daftar ID Petak yang nomor SPK-nya masih kosong:</p>
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
    alert_df = df[empty_spk]
    if not alert_df.empty:
      st.dataframe(
          alert_df[["ID Petak", "Jenis Kegiatan", "Lokasi", "Keterangan"]],
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

b_col1, b_col2, b_col3 = st.columns(3)

with b_col1:
  if st.button("Input ID Petak", use_container_width=True):
    st.session_state["active_menu"] = "Input ID Petak"
    st.rerun()

with b_col2:
  if st.button("Rencana Kerja", use_container_width=True):
    st.session_state["active_menu"] = "Rencana Kerja"
    st.rerun()

with b_col3:
  if st.button("Monitoring", use_container_width=True):
    st.session_state["active_menu"] = "Monitoring"
    st.rerun()

st.write("")

active_menu = st.session_state["active_menu"]

if active_menu == "Input ID Petak":
  sub_tab_reg, sub_tab_spk, sub_tab_lama = st.tabs(
      [
          "Formulir Pendaftaran ID Petak",
          "Update Nomor SPK",
          "Input Kegiatan Selesai",
      ]
  )

  with sub_tab_reg:
    st.subheader("Formulir Pendaftaran ID Petak")

    with st.form("form_input_id_petak", clear_on_submit=True):
      col_f1, col_f2 = st.columns(2)

      with col_f1:
        id_petak = st.text_input("ID Petak", placeholder="Contoh: URUC031305")
        spk_input = st.text_input(
            "Nomor SPK (Opsional)",
            placeholder="Contoh: 23542638253",
        )
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
                "Established - Pupuk Dasar",
                "Established - PPS",
                "Established - PPS Dron",
                "Pupuk",
                "Sulam",
                "Manual Weeding 1",
                "Chemical Weeding 1",
                "Chemical Weeding 2",
                "Chemical Weeding 3",
                "Chemical Weeding 4",
                "Chemical Weeding 5",
                "Chemical Weeding 6",
                "Chemical Weeding 7",
                "Pupuk Susulan 1",
                "Pupuk Susulan 2",
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
        keterangan = st.text_area("Keterangan Tambahan", height=135)

      submitted_petak = st.form_submit_button(
          "Simpan ID Petak", use_container_width=True
      )

      if submitted_petak:
        if not id_petak.strip() or luas <= 0:
          st.error("ID Petak dan Luas wajib diisi dengan benar.")
        else:
          pj_final = st.session_state["user_pj"]
          no_baru = len(df) + 1 if not df.empty else 1
          final_spk = spk_input.strip() if spk_input.strip() else "-"

          new_row_dict = {
              "No": no_baru,
              "ID Petak": id_petak.strip(),
              "SPK": final_spk,
              "Jenis Kegiatan": jenis_kegiatan,
              "Luas": luas,
              "Lokasi": lokasi.strip(),
              "Keterangan": keterangan.strip(),
              "Username": pj_final,
              "Tanggal Rencana Kerja": str(datetime.date.today()),
              "Tanggal Mulai Bekerja": str(datetime.date.today()),
              "Tanggal Selesai Kerja": "-",
              "Rencana Tenaga Kerja": 0,
              "Rencana Alat Berat": "-",
              "Rencana Operator": "-",
              "Actual Tenaga Kerja": 0,
              "Actual Alat Berat": "-",
              "Actual Operator": "-",
              "Rencana Produktivitas": 0.0,
              "Actual Produktivitas": 0.0,
              "Produktivitas Sampai Hari ini": 0.0,
              "Sisa luas belum dikerjakan": luas,
              "Rincian": "On Progres - Petak terdaftar",
          }

          updated_df = pd.concat([df, pd.DataFrame([new_row_dict])], ignore_index=True)
          if safe_gsheets_update("Sheet1", updated_df):
            st.success(f"ID Petak '{id_petak}' berhasil didaftarkan ke server.")
            st.rerun()
          else:
            st.session_state["offline_queue"].append(
                {"type": "sheet1", "data": new_row_dict}
            )
            st.warning(
                f"📴 Mode Offline: ID Petak '{id_petak}' disimpan ke antrean lokal."
                " Akan di-update ke server saat terhubung ke jaringan."
            )

  with sub_tab_spk:
    st.subheader("Pembaruan Nomor SPK")
    if df.empty:
      st.info("Belum ada data petak yang terdaftar.")
    else:
      df["Combo_Key_SPK"] = (
          "ID: "
          + df["ID Petak"].astype(str)
          + " | Kegiatan: "
          + df["Jenis Kegiatan"].astype(str)
          + " (SPK: "
          + df["SPK"].astype(str)
          + ")"
      )
      list_combo_spk = df["Combo_Key_SPK"].dropna().unique().tolist()

      with st.form("form_update_spk"):
        selected_combo_spk = st.selectbox(
            "🔍 Pilih Petak & Jenis Kegiatan", list_combo_spk
        )
        new_spk_input = st.text_input("Nomor SPK Baru")

        submit_update_spk = st.form_submit_button(
            "Simpan Pembaruan SPK", use_container_width=True
        )

        if submit_update_spk:
          if not new_spk_input.strip():
            st.error("Nomor SPK baru tidak boleh kosong.")
          else:
            matched_idx = df[df["Combo_Key_SPK"] == selected_combo_spk].index
            if not matched_idx.empty:
              idx = matched_idx[0]
              df.loc[idx, "SPK"] = new_spk_input.strip()
              clean_df = df.drop(columns=["Combo_Key_SPK"], errors="ignore")
              if safe_gsheets_update("Sheet1", clean_df):
                st.success("Nomor SPK berhasil diperbarui di server.")
                st.rerun()
              else:
                st.session_state["offline_queue"].append(
                    {"type": "sheet1_update", "data": clean_df.to_dict()}
                )
                st.warning(
                    "📴 Mode Offline: Pembaruan SPK disimpan ke antrean lokal."
                )

  with sub_tab_lama:
    st.subheader("Input Kegiatan Selesai")
    st.write(
        "Gunakan formulir ini untuk mencatat kegiatan yang sudah ada dan"
        " selesai."
    )

    with st.form("form_input_kegiatan_lama", clear_on_submit=True):
      col_l1, col_l2 = st.columns(2)

      with col_l1:
        id_petak_lama = st.text_input(
            "ID Petak", placeholder="Contoh: URUC031305"
        )
        spk_lama = st.text_input(
            "Nomor SPK (Opsional)", placeholder="Contoh: 23542638253"
        )
        jenis_kegiatan_lama = st.selectbox(
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
                "Established - Pupuk Dasar",
                "Established - PPS",
                "Established - PPS Dron",
                "Pupuk",
                "Sulam",
                "Manual Weeding 1",
                "Chemical Weeding 1",
                "Chemical Weeding 2",
                "Chemical Weeding 3",
                "Chemical Weeding 4",
                "Chemical Weeding 5",
                "Chemical Weeding 6",
                "Chemical Weeding 7",
                "Pupuk Susulan 1",
                "Pupuk Susulan 2",
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
            key="sel_lama",
        )
        luas_lama = st.number_input(
            "Luas Area (Ha)", min_value=0.0, step=0.1, key="luas_lama"
        )

      with col_l2:
        lokasi_lama = st.text_input(
            "Lokasi / Wilayah",
            placeholder="Contoh: Sektor Utara",
            key="lok_lama",
        )
        tgl_selesai_lama = st.date_input(
            "Tanggal Selesai Kegiatan",
            value=datetime.date.today(),
            key="tgl_lama",
        )
        keterangan_lama = st.text_area(
            "Keterangan Tambahan / Catatan", height=95, key="ket_lama"
        )

      submitted_lama = st.form_submit_button(
          "Simpan Kegiatan Selesai", use_container_width=True
      )

      if submitted_lama:
        if not id_petak_lama.strip() or luas_lama <= 0:
          st.error("ID Petak dan Luas wajib diisi dengan benar.")
        else:
          pj_final = st.session_state["user_pj"]
          no_baru = len(df) + 1 if not df.empty else 1
          final_spk = spk_lama.strip() if spk_lama.strip() else "-"
          tgl_str = tgl_selesai_lama.strftime("%Y-%m-%d")

          new_row_lama = {
              "No": no_baru,
              "ID Petak": id_petak_lama.strip(),
              "SPK": final_spk,
              "Jenis Kegiatan": jenis_kegiatan_lama,
              "Luas": luas_lama,
              "Lokasi": lokasi_lama.strip(),
              "Keterangan": (
                  f"Kegiatan Selesai. {keterangan_lama.strip()}"
              ).strip(),
              "Username": pj_final,
              "Tanggal Rencana Kerja": tgl_str,
              "Tanggal Mulai Bekerja": tgl_str,
              "Tanggal Selesai Kerja": tgl_str,
              "Rencana Tenaga Kerja": 0,
              "Rencana Alat Berat": "-",
              "Rencana Operator": "-",
              "Actual Tenaga Kerja": 0,
              "Actual Alat Berat": "-",
              "Actual Operator": "-",
              "Rencana Produktivitas": luas_lama,
              "Actual Produktivitas": luas_lama,
              "Produktivitas Sampai Hari ini": luas_lama,
              "Sisa luas belum dikerjakan": 0.0,
              "Rincian": "Complete - Kegiatan Selesai",
          }

          updated_df = pd.concat([df, pd.DataFrame([new_row_lama])], ignore_index=True)
          if safe_gsheets_update("Sheet1", updated_df):
            st.success(
                f"Kegiatan selesai untuk ID Petak '{id_petak_lama}' berhasil"
                " dicatat ke server."
            )
            st.rerun()
          else:
            st.session_state["offline_queue"].append(
                {"type": "sheet1", "data": new_row_lama}
            )
            st.warning(
                "📴 Mode Offline: Kegiatan selesai disimpan ke antrean lokal."
            )

  st.markdown("### Daftar ID Petak Terdaftar")
  if not df.empty:
    st.dataframe(
        df[["ID Petak", "SPK", "Jenis Kegiatan", "Luas", "Lokasi", "Keterangan"]],
        use_container_width=True,
        hide_index=True,
    )
  else:
    st.info("Belum ada data petak yang terdaftar.")

elif active_menu == "Rencana Kerja":
  st.subheader("Rencana Kerja & Realisasi Operasional")

  if df.empty:
    st.warning("Silakan daftarkan ID Petak terlebih dahulu.")
  else:
    df["Combo_Key"] = (
        "ID: "
        + df["ID Petak"].astype(str)
        + " | Kegiatan: "
        + df["Jenis Kegiatan"].astype(str)
    )
    list_combo = df["Combo_Key"].dropna().unique().tolist()

    sub_tab_rencana, sub_tab_realisasi = st.tabs(
        ["Buat Rencana", "Update Realisasi"]
    )

    with sub_tab_rencana:
      with st.form("form_buat_rencana"):
        selected_combo_r = st.selectbox(
            "🔍 Pilih Petak & Jenis Kegiatan (Rencana)", list_combo
        )

        col_rk1, col_rk2 = st.columns(2)
        with col_rk1:
          tgl_rencana = st.date_input("Tanggal Rencana Kerja", value=datetime.date.today())
          tgl_mulai = st.date_input("Tanggal Mulai Bekerja", value=datetime.date.today())
          rencana_tk = st.number_input("Rencana Tenaga Kerja (Orang)", min_value=0, step=1)
        with col_rk2:
          rencana_alat = st.text_input("Rencana Jenis Alat Berat", placeholder="Contoh: Excavator / -")
          rencana_operator = st.text_input("Rencana Operator", placeholder="Nama Operator / -")
          rencana_prod = st.number_input("Rencana Produktivitas (Ha)", min_value=0.0, step=0.1)

        submit_rencana_btn = st.form_submit_button(
            "Simpan Rencana Kerja", use_container_width=True
        )

        if submit_rencana_btn:
          matched_idx = df[df["Combo_Key"] == selected_combo_r].index
          if not matched_idx.empty:
            idx = matched_idx[0]
            df.loc[idx, "Tanggal Rencana Kerja"] = tgl_rencana.strftime("%Y-%m-%d")
            df.loc[idx, "Tanggal Mulai Bekerja"] = tgl_mulai.strftime("%Y-%m-%d")
            df.loc[idx, "Rencana Tenaga Kerja"] = rencana_tk
            df.loc[idx, "Rencana Alat Berat"] = (
                rencana_alat.strip() if rencana_alat.strip() else "-"
            )
            df.loc[idx, "Rencana Operator"] = (
                rencana_operator.strip() if rencana_operator.strip() else "-"
            )
            df.loc[idx, "Rencana Produktivitas"] = rencana_prod

            clean_df = df.drop(columns=["Combo_Key"], errors="ignore")
            if safe_gsheets_update("Sheet1", clean_df):
              st.success("Rencana kerja berhasil disimpan ke server.")
              st.rerun()
            else:
              st.session_state["offline_queue"].append(
                  {"type": "sheet1_update", "data": clean_df.to_dict()}
              )
              st.warning(
                  "📴 Mode Offline: Rencana kerja disimpan ke antrean lokal."
              )

    with sub_tab_realisasi:
      with st.form("form_update_realisasi"):
        selected_combo_u = st.selectbox(
            "🔍 Pilih Petak & Jenis Kegiatan (Realisasi)", list_combo
        )

        col_rl1, col_rl2 = st.columns(2)
        with col_rl1:
          actual_tk = st.number_input("Aktual Tenaga Kerja (Orang)", min_value=0, step=1)
          actual_alat = st.text_input("Aktual Jenis Alat Berat", placeholder="Contoh: Excavator / -")
          actual_operator = st.text_input("Aktual Operator", placeholder="Nama Operator / -")
        with col_rl2:
          actual_prod = st.number_input("Aktual Produktivitas (Ha)", min_value=0.0, step=0.1)
          rincian_input = st.text_area("Catatan Operasional / Rincian", height=95)

        submit_realisasi_btn = st.form_submit_button(
            "Simpan Update Realisasi", use_container_width=True
        )

        if submit_realisasi_btn:
          matched_idx = df[df["Combo_Key"] == selected_combo_u].index
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

            df.loc[idx, "Actual Tenaga Kerja"] = actual_tk
            df.loc[idx, "Actual Alat Berat"] = (
                actual_alat.strip() if actual_alat.strip() else "-"
            )
            df.loc[idx, "Actual Operator"] = (
                actual_operator.strip() if actual_operator.strip() else "-"
            )
            df.loc[idx, "Actual Produktivitas"] = actual_prod
            df.loc[idx, "Produktivitas Sampai Hari ini"] = prod_kumulatif
            df.loc[idx, "Sisa luas belum dikerjakan"] = sisa_luas
            df.loc[idx, "Rincian"] = final_rincian

            if sisa_luas <= 0:
              df.loc[idx, "Tanggal Selesai Kerja"] = str(datetime.date.today())
            else:
              df.loc[idx, "Tanggal Selesai Kerja"] = "-"

            clean_df = df.drop(columns=["Combo_Key"], errors="ignore")
            if safe_gsheets_update("Sheet1", clean_df):
              st.success("Realisasi kerja berhasil diperbarui ke server.")
              st.rerun()
            else:
              st.session_state["offline_queue"].append(
                  {"type": "sheet1_update", "data": clean_df.to_dict()}
              )
              st.warning(
                  "📴 Mode Offline: Realisasi kerja disimpan ke antrean lokal."
              )

    st.markdown("### Rekapitulasi Rencana & Realisasi Kerja")
    if not df.empty:
      df_display = df.copy()
      st.dataframe(
          df_display[[
              "ID Petak",
              "SPK",
              "Jenis Kegiatan",
              "Tanggal Rencana Kerja",
              "Tanggal Mulai Bekerja",
              "Tanggal Selesai Kerja",
              "Rencana Tenaga Kerja",
              "Rencana Produktivitas",
              "Rencana Alat Berat",
              "Actual Operator",
              "Actual Tenaga Kerja",
              "Actual Produktivitas",
              "Produktivitas Sampai Hari ini",
              "Sisa luas belum dikerjakan",
              "Rincian",
          ]],
          use_container_width=True,
          hide_index=True,
      )

elif active_menu == "Monitoring":
  st.subheader("Monitoring")
  st.write("Pemantauan kegiatan, nomor SPK terdaftar, serta kalkulasi pengingat (reminder) kegiatan selanjutnya secara real-time.")

  if df.empty:
    st.info("Belum terdapat data kegiatan.")
  else:
    user_mask = (
        df["Username"].astype(str).str.strip().str.upper()
        == st.session_state["user_pj"].strip().upper()
    )
    user_df = df[user_mask]

    if user_df.empty:
      st.info("Belum ada data kegiatan untuk akun Anda.")
    else:
      st.markdown("### 📋 Daftar Kegiatan Terdaftar")
      st.dataframe(
          user_df[[
              "ID Petak",
              "SPK",
              "Jenis Kegiatan",
              "Lokasi",
              "Tanggal Selesai Kerja",
              "Sisa luas belum dikerjakan",
              "Rincian",
          ]],
          use_container_width=True,
          hide_index=True,
      )

      st.markdown("---")
      st.markdown("### 🔔 Kalkulator Reminder Kegiatan Selanjutnya")
      st.write("Dihitung secara real-time berdasarkan tanggal selesai kegiatan Tanam / Tanam & Aquasorb yang telah selesai (`Sisa Luas = 0`).")

      unique_petaks = user_df["ID Petak"].dropna().unique()
      reminder_list = []

      today = datetime.date.today()

      for petak in unique_petaks:
        petak_rows = df[df["ID Petak"].astype(str).str.strip().str.upper() == str(petak).strip().upper()]

        tanam_completed = petak_rows[
            petak_rows["Jenis Kegiatan"].isin(["Established - Tanam", "Established - Tanam & Aquasorb"]) &
            ((petak_rows["Sisa luas belum dikerjakan"] <= 0) | (petak_rows["Rincian"].str.contains("Complete", case=False, na=False)))
        ]

        if tanam_completed.empty:
          continue

        t_selesai_str = str(tanam_completed.iloc[0]["Tanggal Selesai Kerja"])
        try:
          t_selesai_date = datetime.datetime.strptime(t_selesai_str, "%Y-%m-%d").date()
        except ValueError:
          continue

        plant_age_days = (today - t_selesai_date).days
        plant_age_months = plant_age_days / 30.44

        completed_activities = petak_rows[
            (petak_rows["Sisa luas belum dikerjakan"] <= 0) |
            (petak_rows["Rincian"].str.contains("Complete", case=False, na=False))
        ]["Jenis Kegiatan"].tolist()

        next_activity_info = None
        for rule in SCHEDULE_RULES:
          act_name = rule["activity"]
          if act_name not in completed_activities:
            target_date = t_selesai_date + datetime.timedelta(days=rule["days_offset"])
            next_activity_info = {
                "ID Petak": petak,
                "Tanggal Selesai Tanam": t_selesai_str,
                "Umur Tanaman": f"{plant_age_days} Hari (~{round(plant_age_months, 1)} Bulan)",
                "Kegiatan Selanjutnya": act_name,
                "Kategori Umur": rule["label"],
                "Estimasi Tanggal": target_date.strftime("%Y-%m-%d"),
                "Status Waktu": "Jadwal Tiba" if today >= target_date else "Akan Datang"
            }
            break

        if next_activity_info:
          reminder_list.append(next_activity_info)
        else:
          reminder_list.append({
              "ID Petak": petak,
              "Tanggal Selesai Tanam": t_selesai_str,
              "Umur Tanaman": f"{plant_age_days} Hari (~{round(plant_age_months, 1)} Bulan)",
              "Kegiatan Selanjutnya": "Semua Kegiatan Selesai / Siklus Terpenuhi",
              "Kategori Umur": "-",
              "Estimasi Tanggal": "-",
              "Status Waktu": "Selesai"
          })

      if reminder_list:
        df_reminder = pd.DataFrame(reminder_list)
        st.dataframe(df_reminder, use_container_width=True, hide_index=True)
      else:
        st.info("Belum ada petak dengan kegiatan Tanam yang berstatus selesai (`Sisa Luas = 0`). Selesaikan kegiatan Tanam terlebih dahulu untuk melihat reminder kegiatan berikutnya.")
