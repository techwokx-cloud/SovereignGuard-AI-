# agents/risk_broker_agent.py
from typing import Dict, Any, Optional
import json
import re
from datetime import datetime

class RiskBrokerAgent:
    """Performs adversarial audit and risk assessment"""
    
    def __init__(self, model_type="deepseek"):
        self.model_type = model_type
        
        # Risk scoring weights
        self.risk_weights = {
            'tariff_misclassification': 30,
            'origin_fraud': 25,
            'sanctions_evasion': 40,
            'circuitous_routing': 20,
            'document_inconsistency': 15
        }
    
    def audit_trade_document(self, framework: str, port: str, compliance_verdict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform adversarial audit on trade document compliance
        
        Args:
            framework: Trade framework (e.g., "AfCFTA", "WTO")
            port: Target entrance port
            compliance_verdict: Output from Compliance Agent
            
        Returns:
            Dict containing audit results
        """
        
        # Simulate DeepSeek-R1 reasoning (for demo purposes)
        # In production, this would call the actual DeepSeek API
        
        # Extract data for analysis
        entities = compliance_verdict.get('entities', {})
        violations = compliance_verdict.get('violations', [])
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(entities, violations, framework, port)
        
        # Determine escalation
        escalation_required = risk_score > 70
        
        # Generate reasoning
        reasoning = self._generate_reasoning(entities, risk_score, violations, framework)
        
        # Determine primary violation
        primary_violation = self._identify_primary_violation(violations, entities)
        
        # Build result
        return {
            "room_id": "room_afcfta_212-5606",
            "audit_status": "ACTION REQUIRED" if escalation_required else "VERIFIED CLEAR",
            "calculated_risk_index": risk_score,
            "escalation_required": escalation_required,
            "primary_violation_flagged": primary_violation,
            "recommended_action": self._get_recommended_action(escalation_required, primary_violation),
            "_metadata": {
                "audit_timestamp": datetime.now().isoformat(),
                "risk_level": self._get_risk_level(risk_score),
                "reasoning_preview": reasoning,
                "model_used": self.model_type,
                "framework": framework,
                "port": port,
                "compliance_status": compliance_verdict.get('compliance_status'),
                "confidence_score": compliance_verdict.get('confidence_score', 0)
            }
        }
    
    def _calculate_risk_score(self, entities: Dict, violations: List, framework: str, port: str) -> int:
        """Calculate numerical risk score (0-100)"""
        risk_score = 0
        
        # Tariff misclassification
        if not entities.get('has_hs_code'):
            risk_score += 25
        elif not self._validate_hs_code(entities.get('hs_code', '')):
            risk_score += 15
        
        # Origin issues
        if not entities.get('origin'):
            risk_score += 20
        elif self._is_sanctioned_country(entities.get('origin', '')):
            risk_score += 35
        
        # Destination issues
        if not entities.get('destination'):
            risk_score += 10
        elif self._is_sanctioned_country(entities.get('destination', '')):
            risk_score += 25
        
        # Document completeness
        if not entities.get('is_complete'):
            risk_score += 15
        
        # Violations
        risk_score += len(violations) * 5
        
        # Framework-specific adjustments
        if framework == "AfCFTA":
            if entities.get('origin') and not self._is_african_country(entities.get('origin', '')):
                risk_score += 10
        
        # Port-specific (if known high-risk port)
        high_risk_ports = ['Port Moresby', 'Colombo', 'Kingston']
        if port in high_risk_ports:
            risk_score += 10
        
        # Cap at 100
        return min(risk_score, 100)
    
    def _generate_reasoning(self, entities: Dict, risk_score: int, violations: List, framework: str) -> str:
        """Generate reasoning for the risk assessment"""
        reasoning = f"Adversarial audit conducted for {framework} framework. "
        
        if risk_score > 70:
            reasoning += "Significant risk indicators detected: "
        elif risk_score > 40:
            reasoning += "Moderate risk indicators detected: "
        else:
            reasoning += "Minimal risk indicators detected. "
        
        # Add specific findings
        findings = []
        
        if not entities.get('has_hs_code'):
            findings.append("Missing HS code classification")
        elif not self._validate_hs_code(entities.get('hs_code', '')):
            findings.append(f"Invalid HS code format: {entities.get('hs_code')}")
        
        if not entities.get('origin'):
            findings.append("Missing country of origin")
        elif self._is_sanctioned_country(entities.get('origin', '')):
            findings.append(f"Sanctioned country of origin: {entities.get('origin')}")
        
        if not entities.get('destination'):
            findings.append("Missing destination")
        elif self._is_sanctioned_country(entities.get('destination', '')):
            findings.append(f"Sanctioned destination: {entities.get('destination')}")
        
        if violations:
            findings.append(f"Compliance violations: {', '.join(violations)}")
        
        if findings:
            reasoning += " " + " ".join(findings)
        
        return reasoning
    
    def _identify_primary_violation(self, violations: List, entities: Dict) -> Optional[str]:
        """Identify the primary violation"""
        if violations:
            return violations[0]
        
        if not entities.get('has_hs_code'):
            return "Missing or invalid HS code"
        
        if not entities.get('origin'):
            return "Missing country of origin"
        
        if not entities.get('destination'):
            return "Missing destination"
        
        if not entities.get('is_complete'):
            return "Incomplete documentation"
        
        return None
    
    def _get_recommended_action(self, escalation_required: bool, primary_violation: Optional[str]) -> str:
        """Get recommended action based on audit results"""
        if escalation_required:
            if primary_violation:
                return f"Escalate to human customs officer for review of: {primary_violation}"
            return "Escalate to human customs officer for comprehensive review"
        
        if primary_violation:
            return f"Request additional documentation for: {primary_violation}"
        
        return "Auto-approve with standard clearance procedures"
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Convert risk score to human-readable level"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _validate_hs_code(self, hs_code: str) -> bool:
        """Validate HS code format"""
        if not hs_code:
            return False
        import re
        clean_code = re.sub(r'[^0-9.]', '', str(hs_code))
        return bool(re.match(r'^\d{4,10}$', clean_code))
    
    def _is_sanctioned_country(self, country: str) -> bool:
        """Check if country is in sanctions list"""
        if not country:
            return False
        sanctions_list = ['North Korea', 'Iran', 'Syria', 'Crimea', 'Russia']
        return any(sanctioned.lower() in country.lower() for sanctioned in sanctions_list)
    
    def _is_african_country(self, country: str) -> bool:
        """Check if country is in Africa"""
        if not country:
            return False
        african_countries = ['South Africa', 'Nigeria', 'Kenya', 'Tanzania', 'Ghana', 'Egypt', 
                             'Morocco', 'Algeria', 'Angola', 'Ethiopia']
        return any(african.lower() in country.lower() for african in african_countries)

### 3. **Configuration Files**

#### `config/__init__.py`
```python
# config/__init__.py
from .settings import Settings
from .frameworks import FRAMEWORKS, FRAMEWORK_RULES

__all__ = ['Settings', 'FRAMEWORKS', 'FRAMEWORK_RULES']