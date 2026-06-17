# utils/ui_formatter.py
from typing import Dict, Any

def format_for_streamlit(audit_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the Risk Broker output for Streamlit UI rendering
    """
    risk_index = audit_result["calculated_risk_index"]
    
    # Determine UI color scheme
    if risk_index >= 70:
        status_color = "🔴"
        alert_level = "CRITICAL"
    elif risk_index >= 40:
        status_color = "🟡"
        alert_level = "WARNING"
    else:
        status_color = "🟢"
        alert_level = "CLEAR"
    
    return {
        "ui_components": {
            "risk_gauge": {
                "value": risk_index,
                "max": 100,
                "color": status_color,
                "label": f"Risk Score: {risk_index}/100"
            },
            "status_badge": {
                "text": audit_result["audit_status"],
                "color": "red" if audit_result["escalation_required"] else "green"
            },
            "alert_panel": {
                "visible": audit_result["escalation_required"],
                "title": "🚨 HUMAN ESCALATION REQUIRED",
                "content": f"Violation: {audit_result['primary_violation_flagged']}",
                "action": audit_result["recommended_action"]
            },
            "reasoning_panel": {
                "title": "🔍 Audit Reasoning",
                "content": audit_result.get("_metadata", {}).get("reasoning_preview", "Reasoning not available")
            }
        },
        "json_payload": audit_result
    }

def format_risk_gauge(risk_score: int) -> str:
    """Format risk score as visual gauge"""
    if risk_score >= 70:
        return f"🔴 {risk_score}/100"
    elif risk_score >= 40:
        return f"🟡 {risk_score}/100"
    else:
        return f"🟢 {risk_score}/100"