"""
SovereignGuard AI — Enterprise Trade Compliance Desk
Streamlit UI rebuilt from the product mockup, v2 — polished pass.

Run with:  streamlit run app.py
"""

import re
import json
import textwrap
import datetime as dt

import streamlit as st

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
    """Dedent + strip multi-line HTML literals.

    Streamlit's markdown renderer follows CommonMark rules: any block
    indented 4+ spaces is treated as a *code block* rather than raw HTML.
    Writing HTML inside normally-indented Python triple-quoted strings
    triggers exactly that, which is what caused stray tags like `</div>`
    to leak onto the page as literal text. Dedenting before it ever
    reaches st.markdown fixes it for every call site.
    """
    return textwrap.dedent(s).strip()


# ──────────────────────────────────────────────────────────────────────────
# STYLES
# ──────────────────────────────────────────────────────────────────────────
st.markdown(
    html(
        """
        <style>
        .block-container { padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1340px; }
        html, body, [class*="css"] { font-size: 15.5px; }

        .sg-header {
            background: linear-gradient(135deg, #16314F 0%, #2A6098 60%, #3A7BD5 100%);
            border-radius: 14px;
            padding: 22px 28px;
            text-align: center;
            margin-bottom: 16px;
            box-shadow: 0 10px 24px rgba(20,40,70,.25), inset 0 1px 0 rgba(255,255,255,.15);
        }
        .sg-header h1 {
            color: #ffffff; font-size: 31px; margin: 0; font-weight: 800;
            letter-spacing: 0.3px; text-shadow: 0 2px 6px rgba(0,0,0,.25);
        }
        .sg-header p { color: #D7E6F7; margin: 6px 0 0 0; font-size: 14.5px; }

        .sg-topbar {
            display: flex; justify-content: space-between; align-items: center;
            background: #F4F6F9; border: 1px solid #E1E6ED; border-radius: 10px;
            padding: 10px 18px; margin-bottom: 18px; font-size: 14.5px; color: #44546A;
            box-shadow: 0 2px 6px rgba(20,40,70,.05);
        }
        .icon-chip {
            display: inline-flex; align-items: center; justify-content: center;
            width: 30px; height: 30px; border-radius: 50%; margin-right: 5px;
            background: linear-gradient(145deg, #ffffff, #E4E9F0);
            box-shadow: 0 2px 0 rgba(255,255,255,.6) inset, 0 2px 5px rgba(20,40,70,.18);
            font-size: 14.5px; cursor: pointer;
        }

        .sg-section-title {
            text-align: center; font-weight: 800; color: #16314F;
            background: linear-gradient(180deg, #EEF3FA, #E3EAF4);
            border-radius: 8px; padding: 9px 0; margin: 8px 0 16px 0;
            font-size: 15px; letter-spacing: 0.6px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.7), 0 2px 4px rgba(20,40,70,.06);
        }

        .sg-kpi {
            border-radius: 12px; padding: 14px 16px; background: linear-gradient(160deg, #ffffff, #F3F6FA);
            box-shadow: 0 6px 14px rgba(20,40,70,.10), inset 0 1px 0 rgba(255,255,255,.8);
            text-align: center; border: 1px solid #E7ECF2;
        }
        .sg-kpi .v { font-size: 25px; font-weight: 800; color: #16314F; }
        .sg-kpi .l { font-size: 12.5px; color: #6B7A90; font-weight: 600; letter-spacing: .4px; margin-top: 2px;}

        .sg-card {
            border: 1px solid #E5E9F0; border-radius: 14px; overflow: hidden;
            background: #fff; height: 100%;
            box-shadow: 0 8px 18px rgba(20,40,70,.09), 0 2px 4px rgba(20,40,70,.05);
            transition: transform .15s ease, box-shadow .15s ease;
        }
        .sg-card:hover { transform: translateY(-3px); box-shadow: 0 14px 26px rgba(20,40,70,.16); }
        .sg-card-header {
            padding: 12px 14px; font-weight: 800; color: #fff; font-size: 15px;
            display: flex; align-items: center;
            text-shadow: 0 1px 2px rgba(0,0,0,.2);
        }
        .sg-card-body { padding: 14px 16px; font-size: 14.5px; color: #2B2F38; }
        .sg-card-body .sg-status { font-weight: 700; margin-bottom: 10px; color: #16314F; }
        .sg-item { padding: 5px 0; border-bottom: 1px dashed #EEF1F5; }
        .sg-item:last-child { border-bottom: none; }

        .hdr-intake     { background: linear-gradient(135deg, #4D8FD6, #2D6CB0); }
        .hdr-compliance { background: linear-gradient(135deg, #F0AC45, #D98F1E); }
        .hdr-auditor    { background: linear-gradient(135deg, #34466e, #161F33); }

        .icon-badge {
            display: inline-flex; align-items: center; justify-content: center;
            width: 30px; height: 30px; border-radius: 50%;
            font-size: 16px; margin-right: 9px; flex-shrink: 0;
            box-shadow: inset 0 1px 1px rgba(255,255,255,.5), inset 0 -2px 3px rgba(0,0,0,.25), 0 3px 6px rgba(0,0,0,.25);
        }
        .icon-light  { background: rgba(255,255,255,.22); }

        .sg-pill {
            display: inline-block; padding: 2px 11px; border-radius: 12px;
            font-size: 12px; font-weight: 800; margin-left: 6px;
            box-shadow: 0 1px 2px rgba(0,0,0,.12);
        }
        .pill-ok      { background: linear-gradient(145deg, #BFF3D6, #8CE6B4); color: #0E6B36; }
        .pill-flagged { background: linear-gradient(145deg, #FFD3CF, #FFADA5); color: #9A1F17; }

        .sg-infobox {
            border: 1px solid #E5E9F0; border-radius: 14px; background: linear-gradient(160deg, #ffffff, #F6F8FB);
            padding: 14px 16px; margin-bottom: 14px;
            box-shadow: 0 8px 16px rgba(20,40,70,.08);
        }
        .sg-infobox h4 { margin: 0 0 10px 0; font-size: 12.5px; color: #5A6679; letter-spacing: .6px; }
        .sg-infobox .row { display:flex; justify-content: space-between; font-size: 14.5px; margin-bottom: 5px;}

        .sg-score-badge {
            text-align: center; font-weight: 800; color: #fff; border-radius: 9px;
            padding: 10px 4px; font-size: 15px; letter-spacing: .5px; margin-top: 10px;
            box-shadow: 0 1px 0 rgba(255,255,255,.3) inset, 0 5px 0 rgba(0,0,0,.15), 0 9px 16px rgba(0,0,0,.18);
        }

        .sg-table-wrap { border-radius: 12px; overflow: hidden; box-shadow: 0 6px 16px rgba(20,40,70,.08); border: 1px solid #E5E9F0;}
        .sg-table { width: 100%; border-collapse: collapse; font-size: 14.5px; }
        .sg-table thead { background: linear-gradient(180deg, #EEF3FA, #E3EAF4); color: #16314F; }
        .sg-table th { text-align: left; padding: 10px 12px; font-weight: 800; font-size: 13.5px; }
        .sg-table td { padding: 9px 12px; border-top: 1px solid #EEF1F5; }
        .sg-table tbody tr:hover { background: #F7FAFD; }

        .sg-escalation {
            border: 2px solid #E0483E; border-radius: 14px; padding: 18px 22px;
            background: linear-gradient(160deg, #FFF8F7, #FFEDEC);
            box-shadow: 0 10px 22px rgba(224,72,62,.15);
        }
        .sg-escalation h3 { color: #C2241B; margin: 0 0 8px 0; font-size: 16.5px; }
        .sg-escalation p { margin: 0; font-size: 14.5px; color: #44303B; }

        .sg-footer {
            text-align: center; color: #8C99AB; font-size: 13px; margin-top: 30px;
            border-top: 1px solid #E1E6ED; padding-top: 16px; letter-spacing: .3px;
        }

        /* 3D buttons */
        .stButton > button, .stDownloadButton > button {
            border-radius: 11px; font-weight: 700; font-size: 15px;
            padding: 0.6rem 1.2rem; border: none;
            transition: transform .08s ease, box-shadow .08s ease, filter .15s ease;
        }
        button[kind="primary"] {
            color: #fff;
            background: linear-gradient(145deg, #3A8BE0, #2660A8);
            box-shadow: 0 1px 0 rgba(255,255,255,.3) inset, 0 5px 0 rgba(15,45,80,.55), 0 9px 16px rgba(20,40,70,.25);
        }
        button[kind="primary"]:hover { filter: brightness(1.06); }
        button[kind="primary"]:active {
            transform: translateY(4px);
            box-shadow: 0 1px 0 rgba(255,255,255,.2) inset, 0 1px 0 rgba(15,45,80,.55), 0 3px 6px rgba(20,40,70,.2);
        }
        button[kind="secondary"] {
            color: #16314F; background: linear-gradient(145deg, #ffffff, #E7ECF2);
            box-shadow: 0 1px 0 rgba(255,255,255,.7) inset, 0 5px 0 rgba(170,180,195,.55), 0 9px 16px rgba(20,40,70,.12);
            border: 1px solid #D7DEE8;
        }
        button[kind="secondary"]:hover { filter: brightness(0.98); }
        button[kind="secondary"]:active {
            transform: translateY(4px);
            box-shadow: 0 1px 0 rgba(255,255,255,.5) inset, 0 1px 0 rgba(170,180,195,.55), 0 3px 6px rgba(20,40,70,.1);
        }
        </style>
        """
    ),
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# MOCK DATA / CONSTANTS
# (Standing in for the real Intake / Compliance / Risk Broker agents,
#  which in production call GPT-4o-mini, Llama-3-70B and Gemini/DeepSeek-R1
#  per the README's architecture.)
# ──────────────────────────────────────────────────────────────────────────
FRAMEWORKS = ["AfCFTA", "WTO", "EU-UK", "USMCA"]

AFCFTA_ORIGIN_CODES = {
    "ZA", "TZ", "KE", "GH", "NG", "EG", "MA", "CI", "SN",
    "RW", "UG", "ET", "ZM", "ZW", "BW", "MU", "NA",
}

SANCTIONED_ENTITIES = {"shadow trading corp", "blackline freight", "umbra logistics fzc"}
HIGH_SCRUTINY_COMMODITIES = {"e-bikes", "lithium batteries", "electronics", "dual-use components"}
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
    "Minimal": "linear-gradient(145deg, #6BEFA8, #1FA855)",
    "Low": "linear-gradient(145deg, #82F0B6, #2FBE6E)",
    "Medium": "linear-gradient(145deg, #FFCB66, #E0A317)",
    "High": "linear-gradient(145deg, #FF8A80, #E0483E)",
    "Critical": "linear-gradient(145deg, #FF6F66, #B0241B)",
}


# ──────────────────────────────────────────────────────────────────────────
# MOCK AGENT PIPELINE
# ──────────────────────────────────────────────────────────────────────────
def intake_agent(text: str) -> dict:
    """Stand-in for the GPT-4o-mini entity extractor."""
    def find(pattern, default="—"):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else default

    return {
        "shipper": find(r"Shipper:\s*(.+)"),
        "consignee": find(r"Consignee:\s*(.+)"),
        "carrier": find(r"Carrier:\s*(.+)"),
        "hs_code": find(r"HS Code:\s*(.+)"),
        "origin": find(r"Origin:\s*(.+)"),
        "destination": find(r"Destination:\s*(.+)"),
        "commodity": find(r"Commodity:\s*(.+)"),
    }


def compliance_agent(entities: dict, framework: str) -> dict:
    """Stand-in for the Llama-3-70B compliance checker."""
    flags = {}

    origin = entities["origin"].strip().upper()
    if framework == "AfCFTA":
        flags["rules_of_origin"] = "Verified" if origin in AFCFTA_ORIGIN_CODES else "Flagged"
    else:
        flags["rules_of_origin"] = "Verified"

    hs = entities["hs_code"].strip()
    flags["hs_code"] = "Verified" if re.match(r"^\d{4}\.\d{2}$", hs) else "Flagged"

    blacklist_hit = any(
        name in f"{entities['shipper']} {entities['consignee']}".lower()
        for name in SANCTIONED_ENTITIES
    )
    flags["sanctions"] = "Flagged" if blacklist_hit else "Clear"

    return flags


def risk_broker(entities: dict, flags: dict) -> dict:
    """Stand-in for the Gemini / DeepSeek-R1 adversarial risk audit."""
    score = 20
    reasons = []

    if flags["rules_of_origin"] == "Flagged":
        score += 30
        reasons.append("Declared origin is not recognized under the framework's preferential rules of origin.")
    if flags["hs_code"] == "Flagged":
        score += 20
        reasons.append("HS code format is inconsistent with the declared commodity.")
    if flags["sanctions"] == "Flagged":
        score += 40
        reasons.append("Shipper or consignee name matched a sanctions watch-list entry.")
    if entities["commodity"].strip().lower() in HIGH_SCRUTINY_COMMODITIES:
        score += 24
        reasons.append(f"Commodity class '{entities['commodity']}' carries elevated scrutiny (e.g. battery/dual-use risk).")

    score = min(score, 100)

    if score <= 20:
        level, action = "Minimal", "Auto-approve"
    elif score <= 40:
        level, action = "Low", "Auto-approve with notation"
    elif score <= 60:
        level, action = "Medium", "Enhanced review"
    elif score <= 80:
        level, action = "High", "Escalate to human"
    else:
        level, action = "Critical", "Immediate escalation"

    if not reasons:
        reasons.append("No material discrepancies detected across origin, classification or watch-lists.")

    return {
        "score": score,
        "level": level,
        "action": action,
        "reasons": reasons,
        "escalation_required": score >= RISK_THRESHOLD,
    }


def pill(ok: bool, ok_label: str, bad_label: str) -> str:
    cls = "pill-ok" if ok else "pill-flagged"
    text = ok_label if ok else bad_label
    return f'<span class="sg-pill {cls}">{text}</span>'


def traffic_light_svg(level: str) -> str:
    is_red = level in ("Critical", "High")
    is_amber = level == "Medium"
    is_green = level in ("Minimal", "Low")

    def light(cy, on, grad_id, off_color):
        if on:
            return f'<circle cx="24" cy="{cy}" r="13" fill="url(#{grad_id})" filter="url(#sgGlow)" stroke="#000" stroke-opacity="0.25" stroke-width="1"/>'
        return f'<circle cx="24" cy="{cy}" r="13" fill="{off_color}" stroke="#000" stroke-opacity="0.3" stroke-width="1"/>'

    return html(
        f"""
        <svg width="48" height="124" viewBox="0 0 48 124" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="sgCase" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#3a4763"/>
                    <stop offset="100%" stop-color="#0f1626"/>
                </linearGradient>
                <radialGradient id="sgRedOn" cx="35%" cy="30%" r="75%">
                    <stop offset="0%" stop-color="#ffc7c2"/>
                    <stop offset="55%" stop-color="#ff4d4d"/>
                    <stop offset="100%" stop-color="#b0241b"/>
                </radialGradient>
                <radialGradient id="sgAmberOn" cx="35%" cy="30%" r="75%">
                    <stop offset="0%" stop-color="#ffe9b8"/>
                    <stop offset="55%" stop-color="#ffb020"/>
                    <stop offset="100%" stop-color="#c97a00"/>
                </radialGradient>
                <radialGradient id="sgGreenOn" cx="35%" cy="30%" r="75%">
                    <stop offset="0%" stop-color="#c9ffe2"/>
                    <stop offset="55%" stop-color="#3ddc84"/>
                    <stop offset="100%" stop-color="#1f9e57"/>
                </radialGradient>
                <filter id="sgGlow" x="-80%" y="-80%" width="260%" height="260%">
                    <feGaussianBlur stdDeviation="4.2" result="blur"/>
                    <feMerge>
                        <feMergeNode in="blur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <rect x="2" y="2" width="44" height="120" rx="18" fill="url(#sgCase)" stroke="#000" stroke-opacity="0.45" stroke-width="1.5"/>
            <rect x="5" y="5" width="38" height="6" rx="3" fill="#ffffff" opacity="0.08"/>
            {light(26, is_red, "sgRedOn", "#3a2326")}
            {light(62, is_amber, "sgAmberOn", "#3a3320")}
            {light(98, is_green, "sgGreenOn", "#1f3326")}
        </svg>
        """
    )


def extract_uploaded_text(uploaded_file):
    """Best-effort text extraction for .txt/.md/.pdf uploads."""
    name = uploaded_file.name.lower()
    if name.endswith((".txt", ".md")):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader  # optional dependency
            reader = PdfReader(uploaded_file)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip() or None
        except ImportError:
            st.warning("PDF parsing needs the `pypdf` package — add it to requirements.txt to enable this on deploy.")
            return None
        except Exception as e:
            st.warning(f"Couldn't parse that PDF: {e}")
            return None
    return None


# ──────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = [
        {"ts": "Oct 21, 13:00:33", "framework": "AfCFTA", "level": "Medium", "score": 52, "status": "Processed"},
        {"ts": "Oct 24, 02:08:18", "framework": "WTO", "level": "Low", "score": 28, "status": "Finalized"},
        {"ts": "Oct 27, 13:06:30", "framework": "AfCFTA", "level": "High", "score": 74, "status": "Finalized"},
    ]

if "doc_text_area" not in st.session_state:
    st.session_state["doc_text_area"] = DEFAULT_DOCUMENT

if "result" not in st.session_state:
    _entities = intake_agent(DEFAULT_DOCUMENT)
    _flags = compliance_agent(_entities, "AfCFTA")
    _audit = risk_broker(_entities, _flags)
    st.session_state.result = {"entities": _entities, "flags": _flags, "audit": _audit, "framework": "AfCFTA", "port": "Dar es Salaam"}

# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR — DOCUMENT INTAKE
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📄 Submit Trade Document")

    uploaded_file = st.file_uploader("Upload a document", type=["txt", "md", "pdf"])
    if uploaded_file is not None:
        sig = (uploaded_file.name, uploaded_file.size)
        if st.session_state.get("last_upload_sig") != sig:
            extracted = extract_uploaded_text(uploaded_file)
            if extracted:
                st.session_state["doc_text_area"] = extracted
                st.session_state["last_upload_sig"] = sig
                st.success(f"📎 Loaded {uploaded_file.name}")

    document_text = st.text_area("Document text", height=220, key="doc_text_area")
    framework = st.selectbox("Trade framework", FRAMEWORKS, index=0)
    port = st.text_input("Target entrance port", value="Dar es Salaam")

    c1, c2 = st.columns(2)
    with c1:
        process = st.button("▶ Process", use_container_width=True, type="primary")
    with c2:
        reset = st.button("↺ Reset", use_container_width=True)

    st.caption("Intake → Compliance → Risk Broker pipeline runs on submit.")

if reset:
    st.session_state["doc_text_area"] = DEFAULT_DOCUMENT
    st.rerun()

if process:
    with st.spinner("Running Intake → Compliance → Risk Broker pipeline…"):
        entities = intake_agent(document_text)
        flags = compliance_agent(entities, framework)
        audit = risk_broker(entities, flags)
    st.session_state.result = {"entities": entities, "flags": flags, "audit": audit, "framework": framework, "port": port}
    st.session_state.history.insert(0, {
        "ts": dt.datetime.now().strftime("%b %d, %H:%M:%S"),
        "framework": framework,
        "level": audit["level"],
        "score": audit["score"],
        "status": "Finalized" if audit["score"] >= 60 else "Processed",
    })

result = st.session_state.result
entities, flags, audit = result["entities"], result["flags"], result["audit"]

# ──────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────
st.markdown(
    html(
        """
        <div class="sg-header">
            <h1>🛡️ SovereignGuard AI Trade Desk</h1>
            <p>Enterprise Trade Compliance Orchestration</p>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

st.markdown(
    html(
        f"""
        <div class="sg-topbar">
            <div><span class="icon-chip">☰</span><span class="icon-chip">⚙️</span><span class="icon-chip">🔔</span><span class="icon-chip">👤</span></div>
            <div>Room ID: <b>212-5606</b> &nbsp;|&nbsp; Framework: <b>{result['framework']}</b> &nbsp;|&nbsp; Port: <b>{result['port']}</b></div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# KPI ROW
# ──────────────────────────────────────────────────────────────────────────
total_docs = len(st.session_state.history)
escalations = sum(1 for r in st.session_state.history if r["level"] in ("High", "Critical"))
avg_score = round(sum(r["score"] for r in st.session_state.history) / total_docs) if total_docs else 0

k1, k2, k3, k4 = st.columns(4)
for col, value, label in (
    (k1, total_docs, "DOCUMENTS PROCESSED"),
    (k2, escalations, "ESCALATIONS"),
    (k3, f"{avg_score}", "AVG RISK SCORE"),
    (k4, "3/3", "AGENTS ACTIVE"),
):
    with col:
        st.markdown(
            html(f"""<div class="sg-kpi"><div class="v">{value}</div><div class="l">{label}</div></div>"""),
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# ACTIVE BAND ROOM COLLABORATION
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sg-section-title">ACTIVE BAND ROOM COLLABORATION</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 1, 1, 0.9])

with col1:
    st.markdown(
        html(
            f"""
            <div class="sg-card">
                <div class="sg-card-header hdr-intake"><span class="icon-badge icon-light">🔍</span>INTAKE AGENT</div>
                <div class="sg-card-body">
                    <div class="sg-status">Status: Parsing Complete</div>
                    <div class="sg-item">Carrier: {entities['carrier']}</div>
                    <div class="sg-item">Origin: {entities['origin']}</div>
                    <div class="sg-item">Destination: {entities['destination']}</div>
                    <div class="sg-item">Commodity: {entities['commodity']}</div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        html(
            f"""
            <div class="sg-card">
                <div class="sg-card-header hdr-compliance"><span class="icon-badge icon-light">⚖️</span>COMPLIANCE AGENT</div>
                <div class="sg-card-body">
                    <div class="sg-status">Framework: {result['framework']}<br>Status: Analysis Finalized</div>
                    <div class="sg-item">Rules-of-Origin {pill(flags['rules_of_origin']=='Verified', 'Verified', 'Flagged')}</div>
                    <div class="sg-item">HS Code Validation {pill(flags['hs_code']=='Verified', 'Verified', 'Flagged')}</div>
                    <div class="sg-item">Sanctions List {pill(flags['sanctions']=='Clear', 'Clear', 'Flagged')}</div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

with col3:
    score_grad = LEVEL_GRADIENTS[audit["level"]]
    st.markdown(
        html(
            f"""
            <div class="sg-card">
                <div class="sg-card-header hdr-auditor"><span class="icon-badge icon-light">🛡️</span>AUDITOR AGENT</div>
                <div class="sg-card-body">
                    <div class="sg-status">✅ Audit Complete — {audit['action']}</div>
                    <div class="sg-item">🔒 Audit Trail Packet (cryptographically hashed)</div>
                    <div class="sg-score-badge" style="background:{score_grad};">RISK SCORE: {audit['score']} [{audit['level'].upper()}]</div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        html(
            """
            <div class="sg-infobox">
                <h4>ROOM STATUS</h4>
                <div class="row"><span>Orchestrator</span><b style="color:#1FA855;">● Online</b></div>
                <div class="row"><span>Agents</span><b>3/3 Active</b></div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        html(
            f"""
            <div class="sg-infobox" style="text-align:center;">
                <h4>RISK ASSESSMENT</h4>
                {traffic_light_svg(audit['level'])}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    packet = json.dumps(
        {
            "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
            "framework": result["framework"],
            "port": result["port"],
            "entities": entities,
            "compliance_flags": flags,
            "risk_audit": audit,
        },
        indent=2,
    )
    st.download_button(
        "⬇️ Download Audit Packet",
        data=packet,
        file_name=f"audit_packet_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True,
    )

# ──────────────────────────────────────────────────────────────────────────
# COMPLIANCE CHECKLIST MATRIX
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sg-section-title">COMPLIANCE CHECKLIST MATRIX</div>', unsafe_allow_html=True)

status_colors = {"Finalized": "#1FA855", "Processed": "#5A6679", "Red": "#E0483E"}
rows_html = ""
for row in st.session_state.history[:8]:
    color = status_colors.get(row["status"], "#5A6679")
    rows_html += html(
        f"""
        <tr>
            <td>{row['ts']}</td>
            <td>{row['framework']}</td>
            <td>{row['level']} ({row['score']})</td>
            <td style="color:{color}; font-weight:800;">{row['status']}</td>
            <td><a href="#" style="color:#2D6CB0; font-weight:600;">View audit packet ↗</a></td>
        </tr>
        """
    )

st.markdown(
    html(
        f"""
        <div class="sg-table-wrap">
        <table class="sg-table">
            <thead>
                <tr>
                    <th>Recent Transaction</th>
                    <th>Framework</th>
                    <th>Risk Level</th>
                    <th>Status</th>
                    <th>Audit Packet</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# HUMAN REVIEW ACTION
# ──────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

if audit["escalation_required"]:
    st.markdown(
        html(
            f"""
            <div class="sg-escalation">
                <h3>⚠️ {"CRITICAL ESCALATION" if audit['level']=="Critical" else "ESCALATION REQUIRED"}</h3>
                <p>Human auditor intervention required due to a {audit['level'].lower()} risk flag.<br>{' '.join(audit['reasons'])}</p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2, _ = st.columns([1, 1, 2])
    with b1:
        if st.button("🔏 Override & Sign Audit Packet", type="primary", use_container_width=True):
            st.success("Audit packet signed and override logged.")
    with b2:
        if st.button("🛑 Reject Manifest", use_container_width=True):
            st.error("Manifest rejected and returned to shipper.")
else:
    st.success(f"No escalation required — {audit['action']}.")

with st.expander("🔍 Detailed audit reasoning"):
    for r in audit["reasons"]:
        st.write(f"- {r}")

# ──────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="sg-footer">POWERED BY GPT-4o-mini · LLAMA-3-70B · GEMINI / DEEPSEEK-R1</div>',
    unsafe_allow_html=True,
)
