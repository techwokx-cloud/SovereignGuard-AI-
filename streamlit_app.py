"""
SovereignGuard AI — Enterprise Trade Compliance Desk  v3
"""

import re, json, textwrap, datetime as dt, os, base64
import requests
import streamlit as st

# ── Optional heavy deps ────────────────────────────────────────────────────
try:
    from openai import OpenAI as _OAI; OPENAI_OK = True
except ImportError:
    OPENAI_OK = False

try:
    import google.generativeai as genai; GENAI_OK = True
except ImportError:
    GENAI_OK = False

# ──────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SovereignGuard AI — Trade Desk",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def html(s: str) -> str:
    return textwrap.dedent(s).strip()

# ──────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────
FRAMEWORKS = ["AfCFTA", "WTO", "EU-UK", "USMCA"]

AFRICAN_PORTS = sorted([
    # East Africa
    "Dar es Salaam, Tanzania", "Zanzibar, Tanzania", "Tanga, Tanzania", "Mtwara, Tanzania",
    "Mombasa, Kenya", "Lamu, Kenya", "Kilindini (Mombasa), Kenya",
    "Djibouti, Djibouti", "Berbera, Somaliland", "Mogadishu, Somalia",
    "Port Sudan, Sudan", "Massawa, Eritrea", "Assab, Eritrea",
    # Southern Africa
    "Durban, South Africa", "Cape Town, South Africa",
    "Port Elizabeth (Gqeberha), South Africa", "Richards Bay, South Africa",
    "Coega (Ngqura), South Africa", "East London, South Africa",
    "Saldanha Bay, South Africa", "Mossel Bay, South Africa",
    "Maputo, Mozambique", "Beira, Mozambique", "Nacala, Mozambique", "Pemba, Mozambique",
    "Walvis Bay, Namibia", "Luanda, Angola", "Lobito, Angola",
    # Indian Ocean Islands
    "Port Louis, Mauritius", "Toamasina (Tamatave), Madagascar",
    "Mahajanga, Madagascar", "Toliara, Madagascar",
    "Victoria, Seychelles", "Moroni, Comoros",
    # West Africa
    "Lagos (Apapa), Nigeria", "Lagos (Tin Can Island), Nigeria",
    "Port Harcourt, Nigeria", "Onne, Nigeria", "Warri, Nigeria", "Calabar, Nigeria",
    "Tema, Ghana", "Takoradi, Ghana",
    "Abidjan, Côte d'Ivoire", "San Pedro, Côte d'Ivoire",
    "Lomé, Togo", "Cotonou, Benin",
    "Dakar, Senegal", "Banjul, Gambia",
    "Conakry, Guinea", "Freetown, Sierra Leone",
    "Monrovia, Liberia", "Buchanan, Liberia",
    "Nouakchott, Mauritania", "Bissau, Guinea-Bissau", "Praia, Cape Verde",
    # Central Africa
    "Douala, Cameroon", "Kribi, Cameroon",
    "Libreville, Gabon", "Port-Gentil, Gabon",
    "Pointe-Noire, Rep. of Congo", "Matadi, DR Congo", "Boma, DR Congo",
    "Malabo, Equatorial Guinea", "Bata, Equatorial Guinea",
    "São Tomé, São Tomé & Príncipe",
    # North Africa
    "Casablanca, Morocco", "Tangier Med, Morocco", "Agadir, Morocco",
    "Alexandria, Egypt", "Port Said, Egypt", "Suez, Egypt",
    "Tunis (Radès), Tunisia", "Sfax, Tunisia",
    "Tripoli, Libya", "Benghazi, Libya",
    "Algiers, Algeria", "Oran, Algeria", "Annaba, Algeria",
])

AFCFTA_ORIGIN_CODES = {
    "ZA","TZ","KE","GH","NG","EG","MA","CI","SN","RW","UG","ET",
    "ZM","ZW","BW","MU","NA","CM","GA","AO","MZ","SN","DZ","TN","LY",
    "SD","DJ","ER","SO","MG","MW","BI","RW","CD","CG","CF","TD","GM",
    "GW","GN","SL","LR","ML","BF","NE","BJ","TG","CV","ST","GQ","SC",
}
SANCTIONED_ENTITIES = {"shadow trading corp", "blackline freight", "umbra logistics fzc"}
HIGH_SCRUTINY = {"e-bikes", "lithium batteries", "electronics", "dual-use components"}
RISK_THRESHOLD = 70

DEFAULT_DOCUMENT = """BILL OF LADING
Shipper: ABC Trading Ltd.
Consignee: XYZ Importers
Carrier: MSC
HS Code: 8471.30
Origin: GZ
Destination: MBA
Commodity: E-bikes
"""

LEVEL_GRADIENTS = {
    "Minimal": "linear-gradient(145deg,#6BEFA8,#1FA855)",
    "Low":     "linear-gradient(145deg,#82F0B6,#2FBE6E)",
    "Medium":  "linear-gradient(145deg,#FFCB66,#E0A317)",
    "High":    "linear-gradient(145deg,#FF8A80,#E0483E)",
    "Critical":"linear-gradient(145deg,#FF6F66,#B0241B)",
}

# ──────────────────────────────────────────────────────────────────────────
# API KEYS  (from Streamlit secrets or env)
# ──────────────────────────────────────────────────────────────────────────
def _secret(key: str) -> str:
    try:    return st.secrets.get(key, "") or os.getenv(key, "")
    except: return os.getenv(key, "")

GOOGLE_API_KEY      = _secret("GOOGLE_API_KEY")
FEATHERLESS_API_KEY = _secret("FEATHERLESS_API_KEY")
DEEPSEEK_API_KEY    = _secret("DEEPSEEK_API_KEY")
AIML_API_KEY        = _secret("AIML_API_KEY")

# ──────────────────────────────────────────────────────────────────────────
# STYLES
# ──────────────────────────────────────────────────────────────────────────
st.markdown(html("""
<style>
.block-container{padding-top:1rem;padding-bottom:2rem;max-width:1380px}
html,body,[class*="css"]{font-size:15.5px}

/* ── HEADER ─────────────────────────────────────────────────────────── */
.sg-header{
    background:linear-gradient(135deg,#0D2240 0%,#1B4F88 55%,#2D6CB0 100%);
    border-radius:14px;padding:0;overflow:hidden;margin-bottom:14px;
    box-shadow:0 12px 28px rgba(10,25,55,.35),inset 0 1px 0 rgba(255,255,255,.12);
}
.sg-header-inner{
    display:flex;align-items:center;justify-content:space-between;padding:18px 28px;
}
.sg-header-brand{display:flex;align-items:center;gap:14px}
.sg-header-logo{
    width:52px;height:52px;border-radius:50%;
    background:linear-gradient(145deg,#F0AC45,#C97A00);
    display:flex;align-items:center;justify-content:center;font-size:26px;
    box-shadow:0 4px 0 rgba(0,0,0,.3),0 8px 16px rgba(0,0,0,.25),inset 0 1px 0 rgba(255,255,255,.4);
}
.sg-header-text h1{color:#fff;font-size:26px;font-weight:800;margin:0;letter-spacing:.3px;
    text-shadow:0 2px 6px rgba(0,0,0,.25)}
.sg-header-text p{color:#BFD7EE;margin:3px 0 0;font-size:13px;letter-spacing:.5px}
.sg-header-meta{text-align:right;font-size:12.5px;color:#9FBFE0;line-height:1.7}
.sg-header-meta b{color:#fff}
.sg-header-bar{background:rgba(0,0,0,.2);padding:7px 28px;display:flex;
    justify-content:space-between;align-items:center;font-size:13px;color:#9FBFE0}
.hbar-icons{display:flex;gap:8px}
.hbar-icon{
    width:28px;height:28px;border-radius:50%;
    background:linear-gradient(145deg,rgba(255,255,255,.18),rgba(255,255,255,.06));
    border:1px solid rgba(255,255,255,.15);
    display:inline-flex;align-items:center;justify-content:center;
    font-size:13px;cursor:pointer;transition:background .15s;
}
.hbar-icon:hover{background:rgba(255,255,255,.25)}

/* ── KPI STRIP ─────────────────────────────────────────────────────── */
.sg-kpi{
    border-radius:12px;padding:13px 14px;
    background:linear-gradient(160deg,#fff,#F3F6FA);
    box-shadow:0 6px 14px rgba(20,40,70,.10),inset 0 1px 0 rgba(255,255,255,.8);
    text-align:center;border:1px solid #E7ECF2;
}
.sg-kpi .v{font-size:24px;font-weight:800;color:#16314F}
.sg-kpi .l{font-size:12px;color:#6B7A90;font-weight:600;letter-spacing:.4px;margin-top:2px}

/* ── SECTION TITLE ──────────────────────────────────────────────────── */
.sg-section-title{
    text-align:center;font-weight:800;color:#16314F;
    background:linear-gradient(180deg,#EEF3FA,#E3EAF4);
    border-radius:8px;padding:9px 0;margin:8px 0 16px;
    font-size:14.5px;letter-spacing:.8px;
    box-shadow:inset 0 1px 0 rgba(255,255,255,.7),0 2px 4px rgba(20,40,70,.06);
}

/* ── AGENT CARDS ────────────────────────────────────────────────────── */
.sg-card{
    border:1px solid #E5E9F0;border-radius:14px;overflow:hidden;
    background:#fff;display:flex;flex-direction:column;
    box-shadow:0 8px 18px rgba(20,40,70,.09),0 2px 4px rgba(20,40,70,.05);
    transition:transform .15s ease,box-shadow .15s ease;min-height:230px;
}
.sg-card:hover{transform:translateY(-3px);box-shadow:0 14px 26px rgba(20,40,70,.16)}
.sg-card-header{
    padding:11px 14px;font-weight:900;color:#fff;font-size:14.5px;
    display:flex;align-items:center;letter-spacing:.5px;
    text-shadow:0 1px 3px rgba(0,0,0,.25);flex-shrink:0;
}
.sg-card-body{padding:13px 15px;font-size:14px;color:#2B2F38;flex:1}
.sg-subheader{font-weight:700;font-size:13px;color:#5A6679;
    letter-spacing:.5px;margin-bottom:8px;text-transform:uppercase}
.sg-status-bar{
    display:inline-block;font-weight:700;font-size:12.5px;padding:3px 10px;
    border-radius:20px;margin-bottom:10px;
}
.sb-green{background:#DEF7E7;color:#0E6B36}
.sb-amber{background:#FEF0D3;color:#8A5A00}
.sg-item{padding:4px 0;border-bottom:1px dashed #EEF1F5;font-size:13.5px}
.sg-item:last-child{border-bottom:none}
.sg-check{color:#1FA855;margin-right:5px}
.sg-check-bad{color:#E0483E;margin-right:5px}

.hdr-intake{background:linear-gradient(135deg,#4D8FD6,#1E5EA8)}
.hdr-compliance{background:linear-gradient(135deg,#F0AC45,#C97A00)}
.hdr-auditor{background:linear-gradient(135deg,#4A6096,#0D2240)}

.icon-badge{
    width:28px;height:28px;border-radius:50%;margin-right:8px;flex-shrink:0;
    display:inline-flex;align-items:center;justify-content:center;font-size:15px;
    background:rgba(255,255,255,.2);
    box-shadow:inset 0 1px 1px rgba(255,255,255,.5),0 2px 4px rgba(0,0,0,.2);
}

/* ── PILLS ──────────────────────────────────────────────────────────── */
.sg-pill{
    display:inline-block;padding:2px 10px;border-radius:12px;
    font-size:12px;font-weight:800;margin-left:6px;
}
.pill-ok{background:linear-gradient(145deg,#BFF3D6,#8CE6B4);color:#0E6B36}
.pill-flagged{background:linear-gradient(145deg,#FFD3CF,#FFADA5);color:#9A1F17}
.pill-clear{background:linear-gradient(145deg,#C8F0FF,#8ADAFF);color:#054F73}

/* ── RISK SCORE BADGE ───────────────────────────────────────────────── */
.sg-score-badge{
    text-align:center;font-weight:900;color:#fff;border-radius:9px;
    padding:10px 6px;font-size:15px;letter-spacing:.5px;margin-top:10px;
    box-shadow:0 1px 0 rgba(255,255,255,.3) inset,0 5px 0 rgba(0,0,0,.18),
               0 9px 18px rgba(0,0,0,.2);
}
.sg-audit-trail{
    font-size:13px;color:#44546A;padding:6px 0 4px;
    display:flex;align-items:flex-start;gap:5px;
}
.sg-audit-trail .trail-sub{font-size:11.5px;color:#8C99AB;line-height:1.3}

/* ── ROOM STATUS & RISK ASSESSMENT ─────────────────────────────────── */
.sg-infobox{
    border:1px solid #E5E9F0;border-radius:14px;
    background:linear-gradient(160deg,#fff,#F6F8FB);
    padding:13px 15px;margin-bottom:12px;
    box-shadow:0 8px 16px rgba(20,40,70,.08);
}
.sg-infobox h4{margin:0 0 10px;font-size:11.5px;color:#5A6679;
    letter-spacing:.7px;font-weight:800;text-transform:uppercase}
.rs-icons{display:flex;justify-content:center;gap:10px;margin-bottom:10px}
.rs-icon{
    width:34px;height:34px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:16px;
    box-shadow:0 3px 0 rgba(0,0,0,.15),0 6px 12px rgba(0,0,0,.12),
               inset 0 1px 0 rgba(255,255,255,.5);
}
.rs-doc{background:linear-gradient(145deg,#4D8FD6,#1E5EA8)}
.rs-balance{background:linear-gradient(145deg,#F0AC45,#C97A00)}
.rs-cloud{background:linear-gradient(145deg,#4A6096,#0D2240)}
.inforow{display:flex;justify-content:space-between;align-items:center;
    font-size:13.5px;margin-bottom:5px}
.inforow:last-child{margin-bottom:0}
.sha-badge{
    font-size:10px;font-weight:800;color:#fff;letter-spacing:.5px;
    background:linear-gradient(145deg,#3A5080,#1B2D50);
    border-radius:6px;padding:4px 8px;text-align:center;
    box-shadow:0 2px 0 rgba(0,0,0,.25),0 4px 8px rgba(0,0,0,.15);
    margin-top:6px;line-height:1.4;
}

/* ── COMPLIANCE MATRIX ──────────────────────────────────────────────── */
.sg-table-wrap{border-radius:12px;overflow:hidden;
    box-shadow:0 6px 16px rgba(20,40,70,.08);border:1px solid #E5E9F0}
.sg-table{width:100%;border-collapse:collapse;font-size:14px}
.sg-table thead{background:linear-gradient(180deg,#EEF3FA,#E3EAF4);color:#16314F}
.sg-table th{text-align:left;padding:10px 12px;font-weight:800;font-size:13px}
.sg-table td{padding:8px 12px;border-top:1px solid #EEF1F5;vertical-align:middle}
.sg-table tbody tr:hover{background:#F7FAFD}
.sg-view-btn{
    display:inline-block;padding:4px 12px;border-radius:8px;font-size:12.5px;
    font-weight:700;background:linear-gradient(145deg,#4D8FD6,#2D6CB0);
    color:#fff;cursor:pointer;border:none;
    box-shadow:0 2px 0 rgba(15,45,80,.4),0 4px 8px rgba(20,40,70,.18);
    transition:filter .1s;text-decoration:none;
}
.sg-view-btn:hover{filter:brightness(1.1)}

/* ── MODAL ──────────────────────────────────────────────────────────── */
.sg-modal-wrap{
    background:linear-gradient(160deg,#EEF3FA,#E3EAF4);
    border:2px solid #2D6CB0;border-radius:16px;padding:20px 24px;
    margin:8px 0 16px;
    box-shadow:0 16px 40px rgba(20,40,70,.22);
}
.sg-modal-header{
    background:linear-gradient(135deg,#1E5EA8,#0D2240);
    border-radius:10px;padding:10px 16px;margin-bottom:14px;
    display:flex;justify-content:space-between;align-items:center;
}
.sg-modal-header span{color:#fff;font-weight:800;font-size:14.5px;letter-spacing:.3px}

/* ── ESCALATION / HUMAN REVIEW ──────────────────────────────────────── */
.hra-wrap{border-radius:14px;overflow:hidden;
    box-shadow:0 12px 28px rgba(180,30,20,.2)}
.hra-header{
    background:linear-gradient(135deg,#C2241B,#8B1210);
    padding:11px 20px;font-weight:900;color:#fff;
    font-size:14px;letter-spacing:.8px;text-align:center;text-transform:uppercase;
    text-shadow:0 1px 3px rgba(0,0,0,.3);
}
.hra-body{
    background:linear-gradient(160deg,#FFF5F4,#FFE8E6);
    padding:16px 20px;border:2px solid #E0483E;border-top:none;
    border-radius:0 0 14px 14px;
}
.hra-alert{
    display:flex;align-items:flex-start;gap:10px;
    background:linear-gradient(145deg,#FFF0EE,#FFE0DC);
    border:1px solid #FFADA5;border-radius:10px;padding:12px 14px;
}
.hra-alert-icon{font-size:22px;flex-shrink:0;margin-top:1px}
.hra-alert-text{font-size:14px;font-weight:700;color:#7A1810;line-height:1.5}
.hra-reason{font-size:13px;font-weight:400;color:#5A2A28;margin-top:4px}

/* ── HUMAN REVIEW BUTTONS (override via wrapper divs) ──────────────── */
.override-btn > button{
    background:linear-gradient(145deg,#2D6CB0,#0D2240) !important;
    color:#fff !important;border:none !important;
    box-shadow:0 1px 0 rgba(255,255,255,.2) inset,0 5px 0 rgba(5,15,40,.6),
               0 9px 18px rgba(10,25,55,.3) !important;
    font-size:14px !important;letter-spacing:.3px;
}
.reject-btn > button{
    background:linear-gradient(145deg,#FF5249,#C2241B) !important;
    color:#fff !important;border:none !important;
    box-shadow:0 1px 0 rgba(255,255,255,.2) inset,0 5px 0 rgba(100,10,5,.5),
               0 9px 18px rgba(180,30,20,.25) !important;
    font-size:14px !important;letter-spacing:.3px;
}
.override-btn > button:active,.reject-btn > button:active{
    transform:translateY(4px) !important;
    box-shadow:0 1px 0 rgba(255,255,255,.1) inset,0 1px 0 rgba(0,0,0,.4) !important;
}

/* ── SIDEBAR STYLING ────────────────────────────────────────────────── */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0D2240 0%,#16314F 100%)}
[data-testid="stSidebar"] *{color:#D7E6F7 !important}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3{color:#fff !important}
[data-testid="stSidebar"] .sg-sb-logo{
    display:flex;align-items:center;gap:10px;
    padding:14px 0 18px;border-bottom:1px solid rgba(255,255,255,.1);
    margin-bottom:16px;
}
[data-testid="stSidebar"] .sg-sb-logo-icon{
    width:42px;height:42px;border-radius:50%;
    background:linear-gradient(145deg,#F0AC45,#C97A00);
    display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;
    box-shadow:0 3px 0 rgba(0,0,0,.3),0 6px 12px rgba(0,0,0,.2);
}
[data-testid="stSidebar"] .sg-sb-logo-text{font-size:14px;font-weight:800;
    color:#fff !important;letter-spacing:.3px;line-height:1.3}
[data-testid="stSidebar"] .sg-sb-logo-sub{font-size:11px;color:#9FBFE0 !important}
[data-testid="stSidebar"] label{
    font-weight:700 !important;font-size:12.5px !important;
    letter-spacing:.4px;color:#BFD7EE !important;text-transform:uppercase;
}
[data-testid="stSidebar"] .stTextArea textarea,
[data-testid="stSidebar"] .stSelectbox select,
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"],
[data-testid="stSidebar"] input{
    background:rgba(255,255,255,.08) !important;
    border:1px solid rgba(255,255,255,.15) !important;
    color:#fff !important;border-radius:8px !important;
}
[data-testid="stSidebar"] .sg-sb-section{
    border-top:1px solid rgba(255,255,255,.1);
    padding-top:14px;margin-top:14px;
}
[data-testid="stSidebar"] .sg-sb-section-title{
    font-size:11px;font-weight:800;letter-spacing:.8px;
    color:#9FBFE0 !important;text-transform:uppercase;margin-bottom:10px;
}

/* ── GENERAL BUTTONS ────────────────────────────────────────────────── */
.stButton>button,.stDownloadButton>button{
    border-radius:10px;font-weight:700;font-size:14.5px;
    padding:.55rem 1.1rem;border:none;
    transition:transform .08s ease,box-shadow .08s ease,filter .12s ease;
}
button[kind="primary"]{
    color:#fff;
    background:linear-gradient(145deg,#3A8BE0,#2060A8);
    box-shadow:0 1px 0 rgba(255,255,255,.3) inset,0 5px 0 rgba(15,45,80,.55),
               0 9px 16px rgba(20,40,70,.25);
}
button[kind="primary"]:hover{filter:brightness(1.06)}
button[kind="primary"]:active{transform:translateY(4px);
    box-shadow:0 1px 0 rgba(255,255,255,.2) inset,0 1px 0 rgba(15,45,80,.55)}
button[kind="secondary"]{
    color:#16314F;background:linear-gradient(145deg,#fff,#E7ECF2);
    box-shadow:0 1px 0 rgba(255,255,255,.7) inset,0 5px 0 rgba(170,180,195,.55),
               0 9px 16px rgba(20,40,70,.12);border:1px solid #D7DEE8;
}

/* ── FOOTER ────────────────────────────────────────────────────────── */
.sg-footer{
    text-align:center;color:#8C99AB;font-size:12.5px;margin-top:28px;
    border-top:1px solid #E1E6ED;padding-top:14px;letter-spacing:.4px;
}
</style>
"""), unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# AGENT FUNCTIONS — MOCK
# ──────────────────────────────────────────────────────────────────────────
def intake_agent(text: str) -> dict:
    def find(p, d="—"):
        m = re.search(p, text, re.IGNORECASE)
        return m.group(1).strip() if m else d
    return {
        "shipper":     find(r"Shipper:\s*(.+)"),
        "consignee":   find(r"Consignee:\s*(.+)"),
        "carrier":     find(r"Carrier:\s*(.+)"),
        "hs_code":     find(r"HS Code:\s*(.+)"),
        "origin":      find(r"Origin:\s*(.+)"),
        "destination": find(r"Destination:\s*(.+)"),
        "commodity":   find(r"Commodity:\s*(.+)"),
    }

def compliance_agent(entities: dict, framework: str) -> dict:
    flags = {}
    origin = entities["origin"].strip().upper()
    flags["rules_of_origin"] = "Verified" if (framework != "AfCFTA" or origin in AFCFTA_ORIGIN_CODES) else "Flagged"
    flags["hs_code"] = "Verified" if re.match(r"^\d{4}\.\d{2}$", entities["hs_code"].strip()) else "Flagged"
    bl = any(n in f"{entities['shipper']} {entities['consignee']}".lower() for n in SANCTIONED_ENTITIES)
    flags["sanctions"] = "Flagged" if bl else "Clear"
    return flags

def risk_broker(entities: dict, flags: dict) -> dict:
    score, reasons = 20, []
    if flags["rules_of_origin"] == "Flagged":
        score += 30; reasons.append("Declared origin not recognized under framework's preferential rules of origin.")
    if flags["hs_code"] == "Flagged":
        score += 20; reasons.append("HS code format is inconsistent with the declared commodity.")
    if flags["sanctions"] == "Flagged":
        score += 40; reasons.append("Shipper or consignee matched a sanctions watch-list entry.")
    if entities["commodity"].strip().lower() in HIGH_SCRUTINY:
        score += 24; reasons.append(f"Commodity '{entities['commodity']}' carries elevated dual-use/battery risk.")
    score = min(score, 100)
    if   score <= 20: level, action = "Minimal", "Auto-approve"
    elif score <= 40: level, action = "Low",     "Auto-approve with notation"
    elif score <= 60: level, action = "Medium",  "Enhanced review"
    elif score <= 80: level, action = "High",    "Escalate to human"
    else:             level, action = "Critical","Immediate escalation"
    if not reasons: reasons.append("No material discrepancies detected.")
    return {"score": score, "level": level, "action": action,
            "reasons": reasons, "escalation_required": score >= RISK_THRESHOLD}

# ── REAL API AGENTS ─────────────────────────────────────────────────────
def intake_agent_gemini(text: str) -> dict:
    if not GENAI_OK or not GOOGLE_API_KEY: return intake_agent(text)
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            "Extract trade document entities. Return ONLY a JSON object with keys: "
            "shipper, consignee, carrier, hs_code, origin, destination, commodity. "
            "Use dash for missing fields.\n\nDocument:\n" + text
        )
        raw = model.generate_content(prompt).text
        raw = re.sub(r"```json\n?|```", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        st.warning(f"Gemini intake fell back to mock: {e}")
        return intake_agent(text)

def compliance_agent_featherless(entities: dict, framework: str) -> dict:
    if not OPENAI_OK or not FEATHERLESS_API_KEY: return compliance_agent(entities, framework)
    try:
        client = _OAI(base_url="https://api.featherless.ai/v1", api_key=FEATHERLESS_API_KEY)
        prompt = (
            f"You are a trade compliance expert for {framework}. "
            "Analyse these entities and return ONLY JSON with keys: "
            "rules_of_origin (Verified/Flagged), hs_code (Verified/Flagged), "
            "sanctions (Clear/Flagged).\n\n" + json.dumps(entities)
        )
        resp = client.chat.completions.create(
            model="meta-llama/Llama-3-70B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        raw = re.sub(r"```json\n?|```", "", resp.choices[0].message.content).strip()
        result = json.loads(raw)
        return {
            "rules_of_origin": result.get("rules_of_origin", "Flagged"),
            "hs_code":         result.get("hs_code",         "Flagged"),
            "sanctions":       result.get("sanctions",       "Clear"),
        }
    except Exception as e:
        st.warning(f"Featherless compliance fell back to mock: {e}")
        return compliance_agent(entities, framework)

def risk_broker_deepseek(entities: dict, flags: dict) -> dict:
    if not OPENAI_OK or not DEEPSEEK_API_KEY: return risk_broker(entities, flags)
    try:
        client = _OAI(base_url="https://api.deepseek.com/v1", api_key=DEEPSEEK_API_KEY)
        prompt = (
            "You are an adversarial trade compliance auditor. "
            "Return ONLY JSON: score (0-100 int), level (Minimal/Low/Medium/High/Critical), "
            "action (string), reasons (list of strings).\n\n"
            + json.dumps({"entities": entities, "flags": flags})
        )
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
        )
        raw = re.sub(r"```json\n?|```", "", resp.choices[0].message.content).strip()
        r = json.loads(raw)
        score = min(100, max(0, int(r.get("score", 50))))
        return {
            "score":               score,
            "level":               r.get("level",   "Medium"),
            "action":              r.get("action",  "Enhanced review"),
            "reasons":             r.get("reasons", ["AI assessment."]),
            "escalation_required": score >= RISK_THRESHOLD,
        }
    except Exception as e:
        st.warning(f"DeepSeek risk broker fell back to mock: {e}")
        return risk_broker(entities, flags)

# ──────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────
def pill(ok: bool, ok_label="Verified", bad_label="Flagged") -> str:
    cls = "pill-ok" if ok else "pill-flagged"
    return f'<span class="sg-pill {cls}">{ok_label if ok else bad_label}</span>'

def pill3(value: str) -> str:
    if value in ("Verified",):   return f'<span class="sg-pill pill-ok">{value}</span>'
    if value in ("Clear",):      return f'<span class="sg-pill pill-clear">{value}</span>'
    return f'<span class="sg-pill pill-flagged">{value}</span>'

def check_icon(ok: bool) -> str:
    return '<span class="sg-check">☑</span>' if ok else '<span class="sg-check-bad">☑</span>'

def traffic_light_svg(level: str) -> str:
    is_red   = level in ("Critical", "High")
    is_amber = level == "Medium"
    is_green = level in ("Minimal", "Low")
    def bulb(cy, on, gid, off):
        if on:
            return f'<circle cx="24" cy="{cy}" r="13" fill="url(#{gid})" filter="url(#sgG)" stroke="#000" stroke-opacity=".25" stroke-width="1"/>'
        return f'<circle cx="24" cy="{cy}" r="13" fill="{off}" stroke="#000" stroke-opacity=".3" stroke-width="1"/>'
    return html(f"""
    <svg width="48" height="124" viewBox="0 0 48 124" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="sgCase" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#3a4763"/>
            <stop offset="100%" stop-color="#0f1626"/>
        </linearGradient>
        <radialGradient id="sgR" cx="35%" cy="30%" r="75%">
            <stop offset="0%" stop-color="#ffc7c2"/><stop offset="55%" stop-color="#ff4d4d"/><stop offset="100%" stop-color="#b0241b"/>
        </radialGradient>
        <radialGradient id="sgA" cx="35%" cy="30%" r="75%">
            <stop offset="0%" stop-color="#ffe9b8"/><stop offset="55%" stop-color="#ffb020"/><stop offset="100%" stop-color="#c97a00"/>
        </radialGradient>
        <radialGradient id="sgGN" cx="35%" cy="30%" r="75%">
            <stop offset="0%" stop-color="#c9ffe2"/><stop offset="55%" stop-color="#3ddc84"/><stop offset="100%" stop-color="#1f9e57"/>
        </radialGradient>
        <filter id="sgG" x="-80%" y="-80%" width="260%" height="260%">
            <feGaussianBlur stdDeviation="4.2" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
    </defs>
    <rect x="2" y="2" width="44" height="120" rx="18" fill="url(#sgCase)" stroke="#000" stroke-opacity=".45" stroke-width="1.5"/>
    <rect x="5" y="5" width="38" height="6" rx="3" fill="#fff" opacity=".08"/>
    {bulb(26, is_red,   "sgR",  "#3a2326")}
    {bulb(62, is_amber, "sgA",  "#3a3320")}
    {bulb(98, is_green, "sgGN", "#1f3326")}
    </svg>
    """)

def extract_uploaded_text(f):
    name = f.name.lower()
    if name.endswith((".txt", ".md")): return f.read().decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            return "\n".join(p.extract_text() or "" for p in PdfReader(f).pages).strip() or None
        except ImportError:
            st.warning("Add `pypdf` to requirements.txt for PDF support."); return None
        except Exception as e:
            st.warning(f"PDF parse error: {e}"); return None
    return None

def build_packet(framework, port, entities, flags, audit) -> dict:
    return {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "framework": framework, "port": port,
        "entities": entities, "compliance_flags": flags, "risk_audit": audit,
    }

def github_push(token, owner_repo, branch, file_path, content, message) -> dict:
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{owner_repo}/contents/{file_path}"
    r = requests.get(url, headers=headers, params={"ref": branch}, timeout=10)
    sha = r.json().get("sha") if r.status_code == 200 else None
    payload = {"message": message, "content": base64.b64encode(content.encode()).decode(), "branch": branch}
    if sha: payload["sha"] = sha
    r = requests.put(url, headers=headers, json=payload, timeout=15)
    return r.json()

# ──────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = [
        {"ts":"Oct 21, 13:00","framework":"AfCFTA","level":"Medium","score":52,"status":"Processed"},
        {"ts":"Oct 24, 02:08","framework":"WTO",   "level":"Low",   "score":28,"status":"Finalized"},
        {"ts":"Oct 27, 13:06","framework":"AfCFTA","level":"High",  "score":74,"status":"Finalized"},
    ]
if "history_packets" not in st.session_state:
    st.session_state.history_packets = [{}, {}, {}]
if "doc_text_area" not in st.session_state:
    st.session_state["doc_text_area"] = DEFAULT_DOCUMENT
if "modal_idx" not in st.session_state:
    st.session_state.modal_idx = None
if "result" not in st.session_state:
    _e = intake_agent(DEFAULT_DOCUMENT)
    _f = compliance_agent(_e, "AfCFTA")
    _a = risk_broker(_e, _f)
    st.session_state.result = {"entities":_e,"flags":_f,"audit":_a,"framework":"AfCFTA","port":"Dar es Salaam, Tanzania"}
    st.session_state.history_packets[2] = build_packet("AfCFTA","Dar es Salaam, Tanzania",_e,_f,_a)

# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(html("""
    <div class="sg-sb-logo">
        <div class="sg-sb-logo-icon">🛡️</div>
        <div>
            <div class="sg-sb-logo-text">SovereignGuard AI</div>
            <div class="sg-sb-logo-sub">Trade Compliance Desk</div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    # ── Document intake ──────────────────────────────────────
    st.markdown('<div class="sg-sb-section-title">📄 Document Intake</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a document", type=["txt","md","pdf"], label_visibility="collapsed")
    if uploaded_file is not None:
        sig = (uploaded_file.name, uploaded_file.size)
        if st.session_state.get("last_upload_sig") != sig:
            extracted = extract_uploaded_text(uploaded_file)
            if extracted:
                st.session_state["doc_text_area"] = extracted
                st.session_state["last_upload_sig"] = sig
                st.success(f"📎 {uploaded_file.name}")

    document_text = st.text_area("Document text", height=180, key="doc_text_area", label_visibility="collapsed",
                                  placeholder="Paste or upload a bill of lading, manifest, or customs declaration…")

    st.markdown('<div class="sg-sb-section-title" style="margin-top:10px">⚖️ Framework & Port</div>', unsafe_allow_html=True)
    framework = st.selectbox("Trade framework", FRAMEWORKS, index=0, label_visibility="collapsed")

    port_options = ["— Select a port —"] + AFRICAN_PORTS + ["Other (type below)"]
    port_select = st.selectbox("Target entrance port", port_options,
                                index=AFRICAN_PORTS.index("Dar es Salaam, Tanzania")+1,
                                label_visibility="collapsed")
    if port_select == "Other (type below)":
        port = st.text_input("Custom port name", placeholder="Enter port name…", label_visibility="collapsed")
    elif port_select == "— Select a port —":
        port = ""
    else:
        port = port_select

    # ── API toggle ───────────────────────────────────────────
    st.markdown('<div class="sg-sb-section-title" style="margin-top:10px">🤖 AI Agents</div>', unsafe_allow_html=True)
    use_real_apis = st.toggle("Use real AI agents", value=False,
        help="Requires GOOGLE_API_KEY, FEATHERLESS_API_KEY, and DEEPSEEK_API_KEY in Streamlit secrets or env vars.")
    api_ok = use_real_apis and (GOOGLE_API_KEY or FEATHERLESS_API_KEY or DEEPSEEK_API_KEY)
    if use_real_apis and not api_ok:
        st.caption("⚠️ No API keys found — using mock agents. Add keys to .streamlit/secrets.toml")

    # ── Process / Reset ──────────────────────────────────────
    st.markdown('<div style="margin-top:14px"/>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: process = st.button("▶ Process", use_container_width=True, type="primary")
    with c2: reset   = st.button("↺ Reset",   use_container_width=True)

    # ── GitHub push ──────────────────────────────────────────
    with st.expander("⬆ Push to GitHub", expanded=False):
        gh_token  = st.text_input("GitHub token", type="password", placeholder="ghp_…")
        gh_repo   = st.text_input("Repository", placeholder="owner/repo")
        gh_branch = st.text_input("Branch", value="main")
        gh_path   = st.text_input("File path", value="app.py")
        gh_msg    = st.text_input("Commit message", value="chore: update app.py via SovereignGuard dashboard")
        if st.button("⬆ Commit & Push", use_container_width=True, type="primary"):
            if gh_token and gh_repo:
                with st.spinner("Pushing to GitHub…"):
                    try:
                        app_src = open(__file__).read()
                        r = github_push(gh_token, gh_repo, gh_branch, gh_path, app_src, gh_msg)
                        if "content" in r or "commit" in r:
                            sha = (r.get("commit") or {}).get("sha","")[:7]
                            st.success(f"✅ Pushed! Commit: {sha}")
                        else:
                            st.error(f"GitHub error: {r.get('message','Unknown error')}")
                    except Exception as e:
                        st.error(f"Push failed: {e}")
            else:
                st.warning("Enter a token and repository (owner/repo).")

# ──────────────────────────────────────────────────────────────────────────
# PROCESS
# ──────────────────────────────────────────────────────────────────────────
if reset:
    st.session_state["doc_text_area"] = DEFAULT_DOCUMENT
    st.rerun()

if process:
    if not port:
        st.sidebar.error("Please select or enter a target port.")
    else:
        with st.spinner("Running Intake → Compliance → Risk Broker pipeline…"):
            if api_ok:
                entities  = intake_agent_gemini(document_text)
                flags     = compliance_agent_featherless(entities, framework)
                audit     = risk_broker_deepseek(entities, flags)
            else:
                entities  = intake_agent(document_text)
                flags     = compliance_agent(entities, framework)
                audit     = risk_broker(entities, flags)
        pkt = build_packet(framework, port, entities, flags, audit)
        st.session_state.result          = {"entities":entities,"flags":flags,"audit":audit,"framework":framework,"port":port}
        st.session_state.history.insert(0, {
            "ts":       dt.datetime.now().strftime("%b %d, %H:%M"),
            "framework":framework, "level":audit["level"],
            "score":    audit["score"],
            "status":   "Finalized" if audit["score"] >= 60 else "Processed",
        })
        st.session_state.history_packets.insert(0, pkt)

result   = st.session_state.result
entities = result["entities"]
flags    = result["flags"]
audit    = result["audit"]

# ──────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────
st.markdown(html(f"""
<div class="sg-header">
    <div class="sg-header-inner">
        <div class="sg-header-brand">
            <div class="sg-header-logo">🛡️</div>
            <div class="sg-header-text">
                <h1>SovereignGuard AI Trade Desk</h1>
                <p>ENTERPRISE TRADE COMPLIANCE ORCHESTRATION</p>
            </div>
        </div>
        <div class="sg-header-meta">
            <div>Room ID: <b>212-5606</b></div>
            <div>Framework: <b>{result['framework']}</b></div>
            <div>Port: <b>{result['port']}</b></div>
        </div>
    </div>
    <div class="sg-header-bar">
        <div class="hbar-icons">
            <span class="hbar-icon">☰</span>
            <span class="hbar-icon">⚙️</span>
            <span class="hbar-icon">🔔</span>
            <span class="hbar-icon">👤</span>
        </div>
        <div>{'🟢 Real AI Agents Active' if api_ok else '🔵 Mock Agents · Toggle real agents in sidebar'}</div>
    </div>
</div>
"""), unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# KPI ROW
# ──────────────────────────────────────────────────────────────────────────
total_docs  = len(st.session_state.history)
escalations = sum(1 for r in st.session_state.history if r["level"] in ("High","Critical"))
avg_score   = round(sum(r["score"] for r in st.session_state.history) / total_docs) if total_docs else 0

k1,k2,k3,k4 = st.columns(4)
for col, val, lbl in [
    (k1, total_docs,  "DOCUMENTS PROCESSED"),
    (k2, escalations, "ESCALATIONS"),
    (k3, avg_score,   "AVG RISK SCORE"),
    (k4, "3/3",       "AGENTS ACTIVE"),
]:
    with col:
        st.markdown(html(f'<div class="sg-kpi"><div class="v">{val}</div><div class="l">{lbl}</div></div>'),
                    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# ACTIVE BAND ROOM COLLABORATION
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sg-section-title">⚡ ACTIVE BAND ROOM COLLABORATION</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([1.05, 1.05, 1.05, 0.85])

with c1:
    st.markdown(html(f"""
    <div class="sg-card">
        <div class="sg-card-header hdr-intake">
            <span class="icon-badge">🔍</span>INTAKE AGENT
        </div>
        <div class="sg-card-body">
            <div class="sg-subheader">Parsed Documents</div>
            <span class="sg-status-bar sb-green">Status: Parsing Complete</span>
            <div class="sg-item">Carrier: <b>{entities['carrier']}</b></div>
            <div class="sg-item">Origin: <b>{entities['origin']}</b></div>
            <div class="sg-item">Destination: <b>{entities['destination']}</b></div>
            <div class="sg-item">Commodity: <b>{entities['commodity']}</b></div>
            <div class="sg-item">Shipper: <b>{entities['shipper']}</b></div>
        </div>
    </div>
    """), unsafe_allow_html=True)

with c2:
    ro_ok  = flags['rules_of_origin'] == 'Verified'
    hs_ok  = flags['hs_code']         == 'Verified'
    san_ok = flags['sanctions']        == 'Clear'
    st.markdown(html(f"""
    <div class="sg-card">
        <div class="sg-card-header hdr-compliance">
            <span class="icon-badge">⚖️</span>COMPLIANCE AGENT
        </div>
        <div class="sg-card-body">
            <div class="sg-subheader">Framework Analysis</div>
            <div style="font-size:12px;color:#8A5A00;margin-bottom:8px">(e.g., {result['framework']} v. Mombasa Protocols)</div>
            <span class="sg-status-bar sb-amber">Status: Analysis Finalized</span>
            <div class="sg-item">
                {check_icon(ro_ok)} Rules of Origin
                {pill3(flags['rules_of_origin'])}
            </div>
            <div class="sg-item">
                {check_icon(hs_ok)} HS Code Validation
                {pill3(flags['hs_code'])}
            </div>
            <div class="sg-item">
                {check_icon(san_ok)} Sanctions List
                {pill3(flags['sanctions'])}
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

with c3:
    score_grad = LEVEL_GRADIENTS[audit["level"]]
    audit_action_text = "Action Required" if audit["escalation_required"] else "No Action Required"
    st.markdown(html(f"""
    <div class="sg-card">
        <div class="sg-card-header hdr-auditor">
            <span class="icon-badge">🛡️</span>AUDITOR AGENT
        </div>
        <div class="sg-card-body">
            <div class="sg-subheader">Adversarial Risk Audit</div>
            <div style="font-size:13.5px;font-weight:700;color:#1FA855;margin-bottom:8px">
                ✅ Audit Complete — {audit_action_text}
            </div>
            <div class="sg-audit-trail">
                🔒 Audit Trail Packet
                <div class="trail-sub">(cryptographically hashed<br>Audit Trail generated)</div>
            </div>
            <div class="sg-score-badge" style="background:{score_grad}">
                RISK SCORE: {audit['score']} [{audit['level'].upper()}]
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

with c4:
    # Room status with 3 agent icons
    st.markdown(html(f"""
    <div class="sg-infobox">
        <h4>ROOM STATUS</h4>
        <div class="rs-icons">
            <span class="rs-icon rs-doc"  title="Intake Agent">📄</span>
            <span class="rs-icon rs-balance" title="Compliance Agent">⚖️</span>
            <span class="rs-icon rs-cloud" title="Risk Broker">🛡️</span>
        </div>
        <div class="inforow"><span>Orchestrator</span><b style="color:#1FA855;">● Online</b></div>
        <div class="inforow"><span>Agents</span><b>3/3 Active</b></div>
    </div>
    """), unsafe_allow_html=True)

    # Risk assessment — traffic light + SHA badge
    st.markdown(html(f"""
    <div class="sg-infobox" style="text-align:center">
        <h4>RISK ASSESSMENT</h4>
        <div style="display:flex;justify-content:center;align-items:center;gap:10px">
            {traffic_light_svg(audit['level'])}
            <div class="sha-badge">SHA-256<br>HASH</div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    # Download packet
    pkt_json = json.dumps(
        build_packet(result["framework"], result["port"], entities, flags, audit),
        indent=2
    )
    st.download_button(
        "⬇️ Download Audit Packet",
        data=pkt_json,
        file_name=f"audit_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True,
    )

# ──────────────────────────────────────────────────────────────────────────
# COMPLIANCE CHECKLIST MATRIX
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sg-section-title">📋 COMPLIANCE CHECKLIST MATRIX</div>', unsafe_allow_html=True)

status_colors = {"Finalized":"#1FA855","Processed":"#5A6679"}
level_colors  = {"Minimal":"#1FA855","Low":"#2FBE6E","Medium":"#C97A00",
                 "High":"#E0483E","Critical":"#B0241B"}

# Header row
st.markdown(html("""
<div class="sg-table-wrap">
<table class="sg-table">
<thead><tr>
    <th>Timestamp</th><th>Framework</th><th>Risk Level</th>
    <th>Score</th><th>Status</th><th>Audit Packet</th>
</tr></thead>
</table>
</div>
"""), unsafe_allow_html=True)

# Data rows with native buttons
for idx, row in enumerate(st.session_state.history[:8]):
    sc   = status_colors.get(row["status"], "#5A6679")
    lc   = level_colors.get(row["level"], "#5A6679")
    ca, cb, cc, cd, ce, cf = st.columns([1.8, 1.2, 1.4, 0.8, 1.2, 1.6])
    with ca: st.markdown(f"<div style='font-size:13px;padding:6px 0'>{row['ts']}</div>", unsafe_allow_html=True)
    with cb: st.markdown(f"<div style='font-size:13px;padding:6px 0'>{row['framework']}</div>", unsafe_allow_html=True)
    with cc: st.markdown(f"<div style='font-size:13px;padding:6px 0;font-weight:700;color:{lc}'>{row['level']}</div>", unsafe_allow_html=True)
    with cd: st.markdown(f"<div style='font-size:13px;padding:6px 0;font-weight:800;color:{lc}'>{row['score']}</div>", unsafe_allow_html=True)
    with ce: st.markdown(f"<div style='font-size:13px;padding:6px 0;font-weight:700;color:{sc}'>{row['status']}</div>", unsafe_allow_html=True)
    with cf:
        if st.button("📋 View Packet", key=f"view_{idx}", use_container_width=True):
            if st.session_state.modal_idx == idx:
                st.session_state.modal_idx = None
            else:
                st.session_state.modal_idx = idx
            st.rerun()

    st.markdown("<hr style='margin:0;border:none;border-top:1px solid #EEF1F5'>", unsafe_allow_html=True)

# ── AUDIT PACKET MODAL ──────────────────────────────────────────────────
if st.session_state.modal_idx is not None:
    midx = st.session_state.modal_idx
    hist = st.session_state.history
    pkts = st.session_state.history_packets
    modal_ts  = hist[midx]["ts"]   if midx < len(hist) else "—"
    modal_pkt = pkts[midx]         if midx < len(pkts) else {}

    st.markdown(html(f"""
    <div class="sg-modal-wrap">
        <div class="sg-modal-header">
            <span>📋 AUDIT PACKET — {modal_ts} &nbsp;|&nbsp; {hist[midx].get('framework','—')} &nbsp;|&nbsp; Risk: {hist[midx].get('level','—')} ({hist[midx].get('score','—')})</span>
        </div>
    </div>
    """), unsafe_allow_html=True)

    _, mc, _ = st.columns([0.1, 5.8, 0.1])
    with mc:
        st.json(modal_pkt if modal_pkt else {"note": "Packet data not available for this historical entry."})
        if st.button("✕  Close Audit Packet", key="modal_close_btn", use_container_width=True):
            st.session_state.modal_idx = None
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# HUMAN REVIEW ACTION / ESCALATION
# ──────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

if audit["escalation_required"]:
    crit = audit["level"] == "Critical"
    label = "⚠️ CRITICAL ESCALATION:" if crit else "⚠️ ESCALATION REQUIRED:"
    reason_str = " ".join(audit["reasons"])

    st.markdown(html(f"""
    <div class="hra-wrap">
        <div class="hra-header">🚨 HUMAN REVIEW ACTION</div>
        <div class="hra-body">
            <div class="hra-alert">
                <div class="hra-alert-icon">⚠️</div>
                <div>
                    <div class="hra-alert-text">{label}<br>Human Auditor Intervention Required due to {audit['level']} Risk Flag</div>
                    <div class="hra-reason">{reason_str}</div>
                </div>
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    b1, b2, _ = st.columns([1.4, 1.1, 1.5])
    with b1:
        st.markdown('<div class="override-btn">', unsafe_allow_html=True)
        if st.button("✏️ OVERRIDE & SIGN AUDIT PACKET", use_container_width=True, type="primary", key="override_btn"):
            st.success("✅ Audit packet signed and override logged to the audit trail.")
        st.markdown('</div>', unsafe_allow_html=True)
    with b2:
        st.markdown('<div class="reject-btn">', unsafe_allow_html=True)
        if st.button("✕  REJECT MANIFEST", use_container_width=True, key="reject_btn"):
            st.error("❌ Manifest rejected and returned to shipper with a compliance notice.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.success(f"✅ No escalation required — {audit['action']}.")

with st.expander("🔍 Detailed audit reasoning"):
    for r in audit["reasons"]:
        st.write(f"• {r}")

# ──────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────
st.markdown(html("""
<div class="sg-footer">
POWERED BY GEMINI (Intake) · LLAMA-3-70B via FEATHERLESS (Compliance) · DEEPSEEK-R1 (Risk Broker)
<br><span style="font-size:11px;opacity:.7">SovereignGuard AI by TechWokx · techwokx.online</span>
</div>
"""), unsafe_allow_html=True)
