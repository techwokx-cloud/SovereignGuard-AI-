# utils/gemini_client.py
import google.generativeai as genai
import os
from typing import Dict, Any, Optional
import json
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    """Wrapper for Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY not found. Using mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def generate_compliance_audit(self, framework: str, port: str, compliance_verdict: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk audit using Gemini"""
        
        if self.mock_mode:
            return self._mock_response(framework, port, compliance_verdict)
        
        prompt = self._build_audit_prompt(framework, port, compliance_verdict)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 4096,
                }
            )
            return self._parse_gemini_response(response.text)
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return self._mock_response(framework, port, compliance_verdict, error=str(e))
    
    def _build_audit_prompt(self, framework: str, port: str, compliance_verdict: Dict) -> str:
        """Build the complete prompt for Gemini"""
        return f"""
You are the "🛡