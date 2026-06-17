import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import hashlib
import json

# Page configuration
st.set_page_config(
    page_title="SovereignGuard AI Trade Desk",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 4px solid #00d4ff;
    }
    .header-title {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        padding: 0;
    }
    .header-subtitle {
        color: #8899bb;
        font-size: 1rem;
        margin: 0;
        padding: 0;
    }
    .agent-card {
        background: #1a1a2e;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #2a2a4a;
        margin-bottom: 1rem;
        height: 100%;
    }
    .agent-title {
        color: #00d4ff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #2a2a4a;
        padding-bottom: 0.5rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-success { background: #00ff88; color: #000; }
    .status-warning { background: #ffaa00; color: #000; }
    .status-danger { background: #ff4444; color: #fff; }
    .status-info { background: #00d4ff; color: #000; }
    .risk-high { 
        background: #ff4444; 
        color: #fff; 
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        font-weight: 700;
        text-align: center;
    }
    .risk-gauge {
        background: #1a1a2e;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #ff4444;
    }
    .room-id {
        background: #2a2a4a;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-family: monospace;
        color: #00d4ff;
        font-size: 1.2rem;
    }
    .checklist-header {
        background: #1a1a2e;
        padding: 0.75rem;
        border-radius: 5px 5px 0 0;
        font-weight: 600;
        color: #00d4ff;
    }
    .action-button {
        background: #ff4444;
        color: #fff;
        padding: 0.75rem 2rem;
        border: none;
        border-radius: 5px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
    }
    .action-button:hover {
        background: #cc0000;
        transform: scale(1.02);
    }
    .packet-link {
        color: #00d4ff;
        text-decoration: none;
        font-size: 0.85rem;
        word-break: break-all;
    }
    .packet-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1 class="header-title">🛡️ 'SovereignGuard AI' Trade Desk</h1>
    <p class="header-subtitle">Enterprise Trade Compliance Orchestration</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for demo data
if 'transactions' not in st.session_state:
    st.session_state.transactions = [
        {
            'date': 'Oct 27, 2023 10:05:58',
            'status': 'Running',
            'status_type': 'danger',
            'packet': 'https://www.ar.generated-audit-packet-1'
        },
        {
            'date': 'Oct 27, 2023 13:06:30',
            'status': 'Finalized',
            'status_type': 'success',
            'packet': 'https://www.ar.generated-audit-packet-2'
        },
        {
            'date': 'Oct 21, 2023 13:00:33',
            'status': 'Processed',
            'status_type': 'warning',
            'packet': 'https://www.ar.generated-audit-packet-3'
        },
        {
            'date': 'Oct 21, 2023 02:08:18',
            'status': 'Finalized',
            'status_type': 'success',
            'packet': 'https://www.ar.generated-audit-packet-4'
        }
    ]

# Generate a unique room ID
room_id = f"212-{random.randint(1000, 9999)}"

# Main layout - Three columns
col1, col2, col3 = st.columns([2, 1.5, 1.5])

# COLUMN 1: Active Band Room Collaboration
with col1:
    st.markdown("### 🎯 Active Band Room Collaboration")
    
    # INTAKE AGENT
    with st.container():
        st.markdown("""
        <div class="agent-card">
            <div class="agent-title">📄 INTAKE AGENT</div>
        """, unsafe_allow_html=True)
        
        # Parsed Documents
        st.markdown("**Parsed Documents**")
        st.markdown('<span class="status-badge status-success">✓ Parsing Complete</span>', unsafe_allow_html=True)
        
        doc_data = {
            "Carrier": "MSC",
            "Origin": "GZ",
            "Destination": "MBA",
            "Commodity": "E-Bikes"
        }
        for key, value in doc_data.items():
            st.markdown(f"**{key}:** `{value}`")
        
        st.markdown("---")
        
        # Framework Analysis
        st.markdown("**Framework Analysis**")
        st.markdown('<span class="status-badge status-info">Analysis Finalized</span>', unsafe_allow_html=True)
        st.markdown('📌 ACFTA v. Mombasa Protocols')
        
        checks = [
            ("Rules-of-Origin", "⚠️ Flagged mismatch", "warning"),
            ("HS Code Validation", "✓ Verified", "success"),
            ("Sanctions List", "✓ Clear", "success")
        ]
        for check, status, status_type in checks:
            color = "#00ff88" if status_type == "success" else "#ffaa00"
            st.markdown(f"- {check}: <span style='color: {color};'>{status}</span>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # AUDITOR AGENT
    with st.container():
        st.markdown("""
        <div class="agent-card">
            <div class="agent-title">🔍 AUDITOR AGENT</div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Adversarial Risk Audit**")
        st.markdown('<span class="status-badge status-danger">Audit Complete - Action Required</span>', unsafe_allow_html=True)
        
        st.markdown("**Audit Trail Packet**")
        st.markdown('🔐 *cryptographically hashed Audit Trail generated*')
        
        st.markdown("---")
        
        # Risk Score Display
        st.markdown("""
        <div class="risk-gauge">
            <div style="font-size: 0.9rem; color: #8899bb;">RISK SCORE</div>
            <div style="font-size: 3rem; font-weight: 700; color: #ff4444;">74</div>
            <div style="font-size: 0.9rem; color: #ff4444; font-weight: 600;">⚠️ HIGH</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# COLUMN 2: Room Status & System
with col2:
    # Room Status
    st.markdown("### 🏠 Room Status")
    st.markdown(f'<div class="room-id">Room ID: {room_id}</div>', unsafe_allow_html=True)
    
    # System Monitor
    st.markdown("### 🖥️ System")
    st.markdown("**Monitor & Actions**")
    
    # Quick actions
    col2a, col2b = st.columns(2)
    with col2a:
        st.button("🔄 Refresh", use_container_width=True)
    with col2b:
        st.button("📊 Export", use_container_width=True)
    
    # System status
    st.markdown("---")
    st.markdown("**System Status**")
    st.markdown('<span class="status-badge status-success">● All Systems Operational</span>', unsafe_allow_html=True)
    st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # Risk Assessment Summary
    st.markdown("### 🚨 Risk Assessment")
    st.markdown("""
    <div style="background: #1a1a2e; padding: 1rem; border-radius: 10px; border-left: 4px solid #ff4444;">
        <div style="color: #ff4444; font-weight: 700; font-size: 1.2rem;">74</div>
        <div style="color: #8899bb;">Risk Score</div>
        <div style="color: #ff4444; font-weight: 600;">⚠️ HIGH RISK</div>
    </div>
    """, unsafe_allow_html=True)

# COLUMN 3: Compliance Checklist & Actions
with col3:
    st.markdown("### 📋 Compliance Checklist Matrix")
    
    # Create DataFrame for transactions
    df = pd.DataFrame(st.session_state.transactions)
    
    # Display as a styled table
    for idx, row in df.iterrows():
        with st.container():
            col_a, col_b, col_c = st.columns([1.5, 0.8, 1.5])
            with col_a:
                st.caption(row['date'])
            with col_b:
                if row['status_type'] == 'success':
                    st.markdown(f'<span class="status-badge status-success">{row["status"]}</span>', unsafe_allow_html=True)
                elif row['status_type'] == 'warning':
                    st.markdown(f'<span class="status-badge status-warning">{row["status"]}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="status-badge status-danger">{row["status"]}</span>', unsafe_allow_html=True)
            with col_c:
                st.markdown(f'<a href="{row["packet"]}" target="_blank" class="packet-link">📎 View Packet</a>', unsafe_allow_html=True)
        st.divider()
    
    # Human Review Action
    st.markdown("### 👤 HUMAN REVIEW ACTION")
    
    st.markdown("""
    <div style="background: #2a1a1a; padding: 1rem; border-radius: 10px; border: 2px solid #ff4444;">
        <div style="color: #ff4444; font-weight: 600;">🔴 CRITICAL ESCALATION:</div>
        <div style="color: #ffaaaa; font-size: 0.9rem;">Human Auditor Intervention Required due to High Risk Flag</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Action Buttons
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ OVERRIDE & SIGN\nAUDIT PACKET", use_container_width=True):
            st.success("Override initiated! Audit packet signed.")
    
    with col_b:
        if st.button("❌ REJECT MANIFEST", use_container_width=True):
            st.error("Manifest rejected. Escalation initiated.")
    
    # Footer
    st.markdown("---")
    st.caption("**POWERED BY:** BAND, AI/ML API, & FEATHERLESS AI")

# Additional styling for dark theme
st.markdown("""
<style>
    .stApp {
        background: #0d0d1a;
    }
    .stButton button {
        background: #2a2a4a;
        color: #ffffff;
        border: 1px solid #3a3a5a;
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background: #3a3a6a;
        border-color: #00d4ff;
        color: #ffffff;
    }
    .stSelectbox, .stTextInput {
        background: #1a1a2e;
    }
    .stMetric {
        background: #1a1a2e;
        padding: 0.5rem;
        border-radius: 5px;
    }
    .stDivider {
        background: #2a2a4a;
    }
</style>
""", unsafe_allow_html=True)

# Generate Audit Trail Packet (simulated)
def generate_audit_trail():
    data = {
        "room_id": room_id,
        "timestamp": datetime.now().isoformat(),
        "risk_score": 74,
        "compliance_status": "ACTION REQUIRED",
        "audit_actions": [
            "Rules-of-Origin Mismatch Detected",
            "Sanctions Check Passed",
            "HS Code Validation Passed"
        ]
    }
    packet_hash = hashlib.sha256(json.dumps(data).encode()).hexdigest()[:16]
    return {
        "data": data,
        "hash": packet_hash,
        "link": f"https://www.ar.generated-audit-packet-{packet_hash}"
    }

# Store audit packet in session
if 'audit_packet' not in st.session_state:
    st.session_state.audit_packet = generate_audit_trail()

# Optional: Display audit packet in sidebar
with st.sidebar:
    st.markdown("## 🔐 Audit Trail")
    st.markdown(f"**Hash:** `{st.session_state.audit_packet['hash']}`")
    st.markdown(f"**Link:** {st.session_state.audit_packet['link']}")
    st.json(st.session_state.audit_packet['data'])
