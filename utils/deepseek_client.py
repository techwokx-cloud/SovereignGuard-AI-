# utils/deepseek_client.py
from typing import Dict, Any, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()

class DeepSeekClient:
    """Wrapper for DeepSeek-R1 API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            print("Warning: DEEPSEEK_API_KEY not found. Using mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            # In production, initialize actual DeepSeek client
            # from openai import OpenAI
            # self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com/v1")
    
    def generate_compliance_audit(self, framework: str, port: str, compliance_verdict: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk audit using DeepSeek-R1"""
        
        if self.mock_mode:
            return self._mock_response(framework, port, compliance_verdict)
        
        # In production, call DeepSeek API
        # response = self.client.chat.completions.create(
        #     model="deepseek-r1",
        #     messages=[{"role": "user", "content": self._build_prompt(framework, port, compliance_verdict)}]
        # )
        # return self._parse_response(response.choices[0].message.content)
        
        return self._mock_response(framework, port, compliance_verdict)
    
    def _build_prompt(self, framework: str, port: str, compliance_verdict: Dict) -> str:
        """Build prompt for DeepSeek"""
        return f"""
You are the Risk Broker agent in the SovereignGuard AI Trade Desk.
Framework: {framework}
Port: {port}
Compliance Verdict: {json.dumps(compliance_verdict, indent=2)}

Perform adversarial audit and return JSON with:
- room_id
- audit_status (ACTION REQUIRED or VERIFIED CLEAR)
- calculated_risk_index (0-100)
- escalation_required (true/false)
- primary_violation_flagged
- recommended_action
"""
    
    def _mock_response(self, framework: str, port: str, compliance_verdict: Dict) -> Dict[str, Any]:
        """Generate mock response when DeepSeek is not available"""
        # Use RiskBrokerAgent logic for mock
        from agents.risk_broker_agent import RiskBrokerAgent
        broker = RiskBrokerAgent()
        return broker.audit_trade_document(framework, port, compliance_verdict)