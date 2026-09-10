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
    box
