"""
SovereignGuard AI — Enterprise Trade Compliance Desk
Streamlit UI rebuilt from the product mockup.

Run with:  streamlit run app.py
"""

import re
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

# ──────────────────────────────────────────────────────────────────────────
# STYLES
# ──────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1300px; }

    .sg-header {
        background: linear-gradient(135deg, #1B3A5C 0%, #25527E 100%);
        border-radius: 10px;
        padding: 18px 28px;
        text-align: center;
        margin-bottom: 14px;
    }
    .sg-header h1 {
        color: #ffffff; font-size: 28px; margin: 0; font-weight: 700;
        letter-spacing: 0.3px;
    }
    .sg-header p { color: #BFD7EE; margin: 4px 0 0 0; font-size: 13px; }

    .sg-topbar {
        display: flex; justify-content: space-between; align-items: center;
        background: #F4F6F9; border: 1px solid #E1E6ED; border-radius: 8px;
        padding: 8px 16px; margin-bottom: 16px; font-size: 13px; color: #44546A;
    }

    .sg-section-title {
        text-align: center; font-weight: 700; color: #1B3A5C;
        background: #EDF2F8; border-radius: 6px; padding: 6px 0; margin: 6px 0 14px 0;
        font-size: 14px; letter-spacing: 0.4px;
    }

    .sg-card {
        border: 1px solid #E1E6ED; border-radius: 10px; overflow: hidden;
        background: #fff; height: 100%;
    }
    .sg-card-header {
        padding: 10px 14px; font-weight: 700; color: #fff; font-size: 14px;
    }
    .sg-card-body { padding: 12px 14px; font-size: 13px; color: #2B2F38; }
    .sg-card-body .sg-status { font-weight: 600; margin-bottom: 8px; color: #1B3A5C; }
    .sg-item { padding: 3px 0; border-bottom: 1px dashed #EEF1F5; }
    .sg-item:last-child { border-bottom: none; }

    .hdr-intake     { background: #2D6CB0; }
    .hdr-compliance { background: #D98F1E; }
    .hdr-auditor    { background: #1F2A44; }

    .sg-pill {
        display: inline-block; padding: 1px 9px; border-radius: 10px;
        font-size: 11px; font-weight: 700; margin-left: 4px;
    }
    .pill-ok      { background: #DEF7E7; color: #1FA855; }
    .pill-flagged { background: #FBE3E1; color: #E0483E; }

    .sg-infobox {
        border: 1px solid #E1E6ED; border-radius: 10px; background: #F8FAFC;
        padding: 12px 14px; margin-bottom: 12px;
    }
    .sg-infobox h4 { margin: 0 0 8px 0; font-size: 12px; color: #5A6679; letter-spacing: .5px; }
    .sg-infobox .row { display:flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;}

    .sg-score-badge {
        text-align: center; font-weight: 800; color: #fff; border-radius: 6px;
        padding: 8px 4px; font-size: 14px; letter-spacing: .5px; margin-top: 8px;
    }

    .sg-escalation {
        border: 2px solid #E0483E; border-radius: 10px; padding: 16px 20px;
        background: #FFF6F5;
    }
    .sg-escalation h3 { color: #C2241B; margin: 0 0 6px 0; font-size: 15px; }
    .sg-escalation p { margin: 0 0 10px 0; font-size: 13px; color: #44303B; }

    .sg-footer {
        text-align: center; color: #8C99AB; font-size: 12px; margin-top: 28px;
        border-top: 1px solid #E1E6ED; padding-top: 14px;
    }

    .stButton>button { border-radius: 6px; font-weight: 600; }
    </style>
    """,
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

LEVEL_COLORS = {
    "Minimal": "#1FA855",
    "Low": "#3DDC84",
    "Medium": "#E0A317",
    "High": "#E0483E",
    "Critical": "#B0241B",
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


def pill(label: str, ok: bool) -> str:
    cls = "pill-ok" if ok else "pill-flagged"
    text = "Verified" if label == "rules_of_origin" or label == "hs_code" else ("Clear" if ok else "Flagged")
    return f'<span class="sg-pill {cls}">{text}</span>'


def traffic_light_svg(level: str) -> str:
    red = "#FF4D4D" if level in ("Critical", "High") else "#4A2326"
    amber = "#FFB020" if level == "Medium" else "#4A3D26"
    green = "#3DDC84" if level in ("Minimal", "Low") else "#264A35"
    return f"""
    <svg width="42" height="104" viewBox="0 0 42 104" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="38" height="100" rx="12" fill="#1E293B"/>
        <circle cx="21" cy="22" r="11" fill="{red}"/>
        <circle cx="21" cy="52" r="11" fill="{amber}"/>
        <circle cx="21" cy="82" r="11" fill="{green}"/>
    </svg>
    """


# ──────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = [
        {"ts": "Oct 21, 13:00:33", "framework": "AfCFTA", "level": "Medium", "status": "Processed"},
        {"ts": "Oct 24, 02:08:18", "framework": "WTO", "level": "Low", "status": "Finalized"},
        {"ts": "Oct 27, 13:06:30", "framework": "AfCFTA", "level": "High", "status": "Finalized"},
    ]

if "result" not in st.session_state:
    entities = intake_agent(DEFAULT_DOCUMENT)
    flags = compliance_agent(entities, "AfCFTA")
    audit = risk_broker(entities, flags)
    st.session_state.result = {"entities": entities, "flags": flags, "audit": audit, "framework": "AfCFTA", "port": "Dar es Salaam"}

# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR — DOCUMENT INTAKE
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📄 Submit Trade Document")
    document_text = st.text_area("Document text", value=DEFAULT_DOCUMENT, height=220)
    framework = st.selectbox("Trade framework", FRAMEWORKS, index=0)
    port = st.text_input("Target entrance port", value="Dar es Salaam")
    process = st.button("▶ Process Document", use_container_width=True, type="primary")
    st.caption("Intake → Compliance → Risk Broker pipeline runs on submit.")

if process:
    entities = intake_agent(document_text)
    flags = compliance_agent(entities, framework)
    audit = risk_broker(entities, flags)
    st.session_state.result = {"entities": entities, "flags": flags, "audit": audit, "framework": framework, "port": port}
    st.session_state.history.insert(0, {
        "ts": dt.datetime.now().strftime("%b %d, %H:%M:%S"),
        "framework": framework,
        "level": audit["level"],
        "status": "Finalized" if audit["score"] >= 60 else "Processed",
    })

result = st.session_state.result
entities, flags, audit = result["entities"], result["flags"], result["audit"]

# ──────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="sg-header">
        <h1>🛡️ SovereignGuard AI Trade Desk</h1>
        <p>Enterprise Trade Compliance Orchestration</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="sg-topbar">
        <div>☰&nbsp;&nbsp;⚙️&nbsp;&nbsp;🔔<sup>1</sup>&nbsp;&nbsp;👤</div>
        <div>Room ID: <b>212-5606</b> &nbsp;|&nbsp; Framework: <b>{result['framework']}</b> &nbsp;|&nbsp; Port: <b>{result['port']}</b></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# ACTIVE BAND ROOM COLLABORATION
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sg-section-title">ACTIVE BAND ROOM COLLABORATION</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 1, 1, 0.9])

with col1:
    st.markdown(
        f"""
        <div class="sg-card">
            <div class="sg-card-header hdr-intake">🔍 INTAKE AGENT</div>
            <div class="sg-card-body">
                <div class="sg-status">Status: Parsing Complete</div>
                <div class="sg-item">Carrier: {entities['carrier']}</div>
                <div class="sg-item">Origin: {entities['origin']}</div>
                <div class="sg-item">Destination: {entities['destination']}</div>
                <div class="sg-item">Commodity: {entities['commodity']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="sg-card">
            <div class="sg-card-header hdr-compliance">⚖️ COMPLIANCE AGENT</div>
            <div class="sg-card-body">
                <div class="sg-status">Framework Analysis ({result['framework']})<br>Status: Analysis Finalized</div>
                <div class="sg-item">Rules-of-Origin {pill('rules_of_origin', flags['rules_of_origin']=='Verified')}</div>
                <div class="sg-item">HS Code Validation {pill('hs_code', flags['hs_code']=='Verified')}</div>
                <div class="sg-item">Sanctions List {pill('sanctions', flags['sanctions']=='Clear')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    score_color = LEVEL_COLORS[audit["level"]]
    st.markdown(
        f"""
        <div class="sg-card">
            <div class="sg-card-header hdr-auditor">🛡️ AUDITOR AGENT</div>
            <div class="sg-card-body">
                <div class="sg-status">✅ Audit Complete — {audit['action']}</div>
                <div class="sg-item">🔒 Audit Trail Packet (cryptographically hashed audit trail generated)</div>
                <div class="sg-score-badge" style="background:{score_color};">RISK SCORE: {audit['score']} [{audit['level'].upper()}]</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
        <div class="sg-infobox">
            <h4>ROOM STATUS</h4>
            <div class="row"><span>Orchestrator</span><b style="color:#1FA855;">Online</b></div>
            <div class="row"><span>Agents</span><b>3/3 Active</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="sg-infobox" style="text-align:center;">
            <h4>RISK ASSESSMENT</h4>
            {traffic_light_svg(audit['level'])}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────
# COMPLIANCE CHECKLIST MATRIX
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sg-section-title">COMPLIANCE CHECKLIST MATRIX</div>', unsafe_allow_html=True)

status_colors = {"Finalized": "#1FA855", "Processed": "#5A6679", "Red": "#E0483E"}
rows_html = ""
for row in st.session_state.history[:6]:
    color = status_colors.get(row["status"], "#5A6679")
    rows_html += (
        f"<tr><td>{row['ts']}</td><td>{row['framework']}</td>"
        f"<td>{row['level']}</td>"
        f"<td style='color:{color}; font-weight:700;'>{row['status']}</td>"
        f"<td><a href='#' style='color:#2D6CB0;'>View generated audit packet ↗</a></td></tr>"
    )

st.markdown(
    f"""
    <table style="width:100%; border-collapse: collapse; font-size:13px;">
        <thead style="background:#EDF2F8; color:#1B3A5C;">
            <tr>
                <th style="text-align:left; padding:8px;">Recent Transaction</th>
                <th style="text-align:left; padding:8px;">Framework</th>
                <th style="text-align:left; padding:8px;">Risk Level</th>
                <th style="text-align:left; padding:8px;">Status</th>
                <th style="text-align:left; padding:8px;">Audit Packet</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# HUMAN REVIEW ACTION
# ──────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

if audit["escalation_required"]:
    st.markdown(
        f"""
        <div class="sg-escalation">
            <h3>⚠️ {"CRITICAL ESCALATION" if audit['level']=="Critical" else "ESCALATION REQUIRED"}</h3>
            <p>Human auditor intervention required due to a {audit['level'].lower()} risk flag.<br>
            {' '.join(audit['reasons'])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    b1, b2, _ = st.columns([1, 1, 2])
    with b1:
        if st.button("🔏 Override & Sign Audit Packet", type="primary", use_container_width=True):
            st.success("Audit packet signed and override logged.")
    with b2:
        if st.button("✖ Reject Manifest", use_container_width=True):
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
