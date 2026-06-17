# app.py
import streamlit as st
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Import agents
from agents.intake_agent import IntakeAgent
from agents.compliance_agent import ComplianceAgent
from agents.risk_broker_agent import RiskBrokerAgent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SovereignGuard AI Trade Desk",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SovereignGuardEngine:
    """Main orchestration engine for the trade desk"""
    
    def __init__(self):
        self.intake_agent = IntakeAgent()
        self.compliance_agent = ComplianceAgent()
        self.risk_broker = RiskBrokerAgent()
    
    def process_document(self, document_text: str, framework: str, port: str):
        """Process a trade document through all agents"""
        
        # Step 1: Intake - Extract entities
        with st.spinner("📄 Extracting entities with Intake Agent..."):
            intake_result = self.intake_agent.extract_entities(document_text)
        
        # Step 2: Compliance Check
        with st.spinner("⚖️ Verifying compliance with Compliance Agent..."):
            compliance_result = self.compliance_agent.check_compliance(
                intake_result, framework
            )
        
        # Step 3: Risk Audit
        with st.spinner("🛡️ Performing adversarial audit with Risk Broker..."):
            audit_result = self.risk_broker.audit_trade_document(
                framework=framework,
                port=port,
                compliance_verdict=compliance_result
            )
        
        # Step 4: Final Decision
        decision = self._make_decision(audit_result)
        
        return {
            "intake": intake_result,
            "compliance": compliance_result,
            "risk_audit": audit_result,
            "final_decision": decision,
            "timestamp": datetime.now().isoformat()
        }
    
    def _make_decision(self, audit):
        """Determine final routing decision"""
        if audit["escalation_required"]:
            return "🚨 ESCALATE TO HUMAN"
        elif audit["audit_status"] == "VERIFIED CLEAR":
            return "✅ AUTO-APPROVE"
        else:
            return "⚠️ REVIEW REQUIRED"

def main():
    # Sidebar
    with st.sidebar:
        st.image("https://img.shields.io/badge/SovereignGuard-AI_Trade_Desk-blue?style=for-the-badge&logo=artificial-intelligence", use_container_width=True)
        st.markdown("---")
        
        st.header("⚙️ Configuration")
        framework = st.selectbox(
            "Trade Framework",
            ["AfCFTA", "WTO", "EU-UK", "USMCA"],
            help="Select the international trade framework for compliance verification"
        )
        port = st.text_input("Target Entrance Port", "Dar es Salaam")
        
        st.markdown("---")
        st.markdown("### 🧠 AI Agents Status")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("✅ **Intake**")
            st.markdown("✅ **Compliance**")
            st.markdown("✅ **Risk Broker**")
        with col2:
            st.markdown("*(GPT-4o-mini)*")
            st.markdown("*(Llama-3-70B)*")
            st.markdown("*(DeepSeek-R1)*")
        
        st.markdown("---")
        st.caption(f"System Ready • {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Main content
    st.title("🛡️ SovereignGuard AI Trade Desk")
    st.subheader("Enterprise-Grade Multi-Agent Trade Compliance System")
    
    # Document Input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📄 Trade Document")
        document_text = st.text_area(
            "Paste bill of lading, manifest, or customs declaration:",
            height=250,
            placeholder="BILL OF LADING\nShipper: ABC Trading Ltd.\nConsignee: XYZ Importers\nHS Code: 8471.30\nOrigin: South Africa\nDestination: Tanzania\n\n...",
            key="document_input"
        )
    
    with col2:
        st.markdown("### 🚀 Actions")
        process_button = st.button("🔍 Process Document", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📊 Stats")
        st.metric("Processed Today", "0", delta="0")
        st.metric("Escalations", "0", delta="0")
    
    # Processing
    if process_button and document_text:
        try:
            # Initialize engine
            engine = SovereignGuardEngine()
            
            # Process document
            result = engine.process_document(
                document_text=document_text,
                framework=framework,
                port=port
            )
            
            # Display results
            display_results(result)
            
        except Exception as e:
            st.error(f"❌ Error processing document: {str(e)}")
            st.exception(e)
    
    elif process_button and not document_text:
        st.warning("⚠️ Please enter document text first.")
    
    # Help section
    with st.expander("ℹ️ How to use this system"):
        st.markdown("""
        **1. Enter a trade document** - Paste the raw text from a bill of lading, manifest, or customs declaration.
        
        **2. Select trade framework** - Choose the appropriate international trade agreement.
        
        **3. Click Process** - The system will run through all three AI agents:
        - 📄 **Intake Agent** extracts structured data
        - ⚖️ **Compliance Agent** verifies against the framework
        - 🛡️ **Risk Broker** performs adversarial audit
        
        **4. Review results** - Check the risk score, audit status, and escalation recommendations.
        """)

def display_results(result):
    """Display processing results with enhanced UI"""
    audit = result["risk_audit"]
    risk_score = audit["calculated_risk_index"]
    
    st.markdown("---")
    st.header("📊 Audit Results")
    
    # Risk Score Gauge
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # Determine color and status
        if risk_score >= 70:
            color = "🔴"
            status = "CRITICAL"
            status_color = "error"
        elif risk_score >= 40:
            color = "🟡"
            status = "WARNING"
            status_color = "warning"
        else:
            color = "🟢"
            status = "CLEAR"
            status_color = "success"
        
        # Display risk gauge
        st.metric(
            label=f"{color} Risk Score",
            value=f"{risk_score}/100",
            delta=status,
            delta_color="inverse"
        )
        
        # Progress bar
        st.progress(risk_score / 100)
    
    with col2:
        st.metric(
            "Audit Status",
            audit["audit_status"],
            help="Final determination from Risk Broker"
        )
    
    with col3:
        st.metric(
            "Escalation",
            "🔴 YES" if audit["escalation_required"] else "🟢 NO",
            help="Indicates if human review is required"
        )
    
    with col4:
        st.metric(
            "Framework",
            result.get("compliance", {}).get("framework", "N/A"),
            help="Trade framework used for compliance verification"
        )
    
    # Alert if escalation needed
    if audit["escalation_required"]:
        st.error("🚨 **HUMAN ESCALATION REQUIRED**")
        st.warning(f"**Violation:** {audit['primary_violation_flagged']}")
        st.info(f"**Recommended Action:** {audit['recommended_action']}")
    elif audit["audit_status"] == "VERIFIED CLEAR":
        st.success("✅ **Document Verified Clear** - Auto-approval recommended")
    
    # Detailed Results
    tabs = st.tabs(["🔍 Audit Reasoning", "📋 Pipeline Data", "📊 Compliance Details"])
    
    with tabs[0]:
        if "_metadata" in audit and "reasoning_preview" in audit["_metadata"]:
            st.markdown("### 🧠 Risk Broker Reasoning")
            st.markdown(audit["_metadata"]["reasoning_preview"])
        else:
            st.info("Reasoning not available")
    
    with tabs[1]:
        st.json(result)
    
    with tabs[2]:
        if "compliance" in result:
            compliance = result["compliance"]
            st.markdown("### ⚖️ Compliance Verification Results")
            
            # Display compliance checks
            if "framework_checks" in compliance:
                checks = compliance["framework_checks"]
                for check, value in checks.items():
                    if value:
                        st.success(f"✅ {check.replace('_', ' ').title()}: Passed")
                    else:
                        st.error(f"❌ {check.replace('_', ' ').title()}: Failed")
            
            # Display extracted entities
            if "entities" in compliance:
                st.markdown("### 📋 Extracted Entities")
                entities = compliance["entities"]
                for key, value in entities.items():
                    st.text(f"{key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    main()
