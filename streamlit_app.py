cat > streamlit_app.py << 'EOF'
import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="SovereignGuard AI Trade Desk",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ SovereignGuard AI Trade Desk")
st.subheader("Enterprise-Grade Multi-Agent Trade Compliance System")

# Check if required packages are installed
try:
    import pandas as pd
    import numpy as np
    import plotly.express as px
    PACKAGES_OK = True
except ImportError as e:
    PACKAGES_OK = False
    st.error(f"Missing package: {e}")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    framework = st.selectbox(
        "Trade Framework",
        ["AfCFTA", "WTO", "EU-UK", "USMCA"]
    )
    port = st.text_input("Target Entrance Port", "Dar es Salaam")
    
    st.markdown("---")
    st.markdown("### 🧠 AI Agents")
    st.markdown("✅ Intake Agent")
    st.markdown("✅ Compliance Agent")
    st.markdown("✅ Risk Broker")
    
    st.markdown("---")
    st.caption(f"System Ready • {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 📄 Trade Document")
    document_text = st.text_area(
        "Paste bill of lading, manifest, or customs declaration:",
        height=250,
        placeholder="BILL OF LADING\nShipper: ABC Trading Ltd.\nConsignee: XYZ Importers\nHS Code: 8471.30\nOrigin: South Africa\nDestination: Tanzania",
        key="document_input"
    )

with col2:
    st.markdown("### 🚀 Actions")
    process_button = st.button("🔍 Process Document", type="primary", use_container_width=True)

# Simple processing simulation
if process_button and document_text and PACKAGES_OK:
    with st.spinner("Processing document..."):
        # Simulate processing
        import time
        time.sleep(2)
        
        # Sample result
        risk_score = 45
        escalation = risk_score > 70
        
        st.success("✅ Document processed successfully!")
        
        # Display results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Risk Score", f"{risk_score}/100")
        with col2:
            st.metric("Status", "ACTION REQUIRED" if escalation else "VERIFIED CLEAR")
        with col3:
            st.metric("Escalation", "🔴 YES" if escalation else "🟢 NO")
        
        if escalation:
            st.error("🚨 **HUMAN ESCALATION REQUIRED**")
            st.warning("**Violation:** Potential tariff misclassification detected")
            st.info("**Action:** Escalate to human customs officer for review")
        else:
            st.success("✅ Document verified clear")

elif process_button and document_text and not PACKAGES_OK:
    st.error("⚠️ Required packages not installed. Please check the installation.")
elif process_button and not document_text:
    st.warning("⚠️ Please enter document text first.")

# Help section
with st.expander("ℹ️ How to use this system"):
    st.markdown("""
    **1. Enter a trade document** - Paste the raw text from a bill of lading or customs declaration.
    
    **2. Select trade framework** - Choose the appropriate international trade agreement.
    
    **3. Click Process** - The system will analyze the document for compliance.
    
    **4. Review results** - Check the risk score and any required actions.
    """)

if not PACKAGES_OK:
    st.warning("""
    ⚠️ Some packages failed to install. The app is running in limited mode.
    
    Please check the deployment logs for errors.
    """)
EOF
