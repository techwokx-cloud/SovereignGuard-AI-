# agents/intake_agent.py
import re
from typing import Dict, Any, List
import json

class IntakeAgent:
    """Extracts structured entities from raw trade documents"""
    
    def __init__(self):
        self.entity_patterns = {
            'shipper': r'(?:shipper|exporter|seller)[:\s]+([^\n]+)',
            'consignee': r'(?:consignee|importer|buyer)[:\s]+([^\n]+)',
            'hs_code': r'(?:hs[- ]code|harmonized system|hs)[:\s]+([\d.]+)',
            'origin': r'(?:origin|country of origin)[:\s]+([^\n]+)',
            'destination': r'(?:destination|port of discharge)[:\s]+([^\n]+)',
            'vessel': r'(?:vessel|ship|carrier)[:\s]+([^\n]+)',
            'container': r'(?:container|equipment)[:\s]+([^\n]+)',
            'weight': r'(?:weight|cargo weight)[:\s]+([^\n]+)',
            'description': r'(?:description of goods|goods description)[:\s]+([^\n]+)',
            'invoice': r'(?:invoice|po|order)[:\s]+([^\n]+)'
        }
    
    def extract_entities(self, document_text: str) -> Dict[str, Any]:
        """Extract structured entities from document text"""
        entities = {}
        
        # Extract using regex patterns
        for key, pattern in self.entity_patterns.items():
            match = re.search(pattern, document_text, re.IGNORECASE)
            if match:
                entities[key] = match.group(1).strip()
            else:
                entities[key] = None
        
        # Additional analysis
        entities['has_hs_code'] = bool(entities.get('hs_code'))
        entities['has_origin'] = bool(entities.get('origin'))
        entities['has_destination'] = bool(entities.get('destination'))
        
        # Validate if all key fields are present
        required_fields = ['shipper', 'consignee', 'hs_code', 'origin', 'destination']
        entities['is_complete'] = all(entities.get(field) for field in required_fields)
        
        # Add metadata
        entities['_metadata'] = {
            'word_count': len(document_text.split()),
            'line_count': len(document_text.splitlines()),
            'extraction_timestamp': '2026-06-17T10:00:00Z'  # Will be replaced with actual timestamp
        }
        
        return entities
    
    def validate_hs_code(self, hs_code: str) -> bool:
        """Validate HS code format"""
        if not hs_code:
            return False
        # Remove any non-digit characters
        clean_code = re.sub(r'[^0-9.]', '', hs_code)
        # Check if it's a valid HS code (6-10 digits)
        return bool(re.match(r'^\d{4,10}$', clean_code))

#### `agents/compliance_agent.py`
```python
# agents/compliance_agent.py
from typing import Dict, Any, List
import json

class ComplianceAgent:
    """Verifies trade document compliance against frameworks"""
    
    def __init__(self):
        self.frameworks = {
            'AfCFTA': self._check_afcfta,
            'WTO': self._check_wto,
            'EU-UK': self._check_eu_uk,
            'USMCA': self._check_usmca
        }
        
        self.sanctions_list = {
            'entities': ['NORTH KOREA TRADING', 'IRAN SHIPPING', 'RUSSIAN OIL'],
            'countries': ['North Korea', 'Iran', 'Syria', 'Crimea']
        }
    
    def check_compliance(self, entities: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Check compliance against specified framework"""
        
        # Validate framework
        if framework not in self.frameworks:
            return {
                'compliance_status': 'ERROR',
                'error': f'Framework {framework} not supported',
                'framework': framework,
                'entities': entities
            }
        
        # Run framework-specific checks
        framework_checks = self.frameworks[framework](entities)
        
        # Run general checks
        general_checks = self._general_compliance_checks(entities)
        
        # Combined results
        all_passed = all(framework_checks.values()) and all(general_checks.values())
        
        # Determine violations
        violations = []
        for check, passed in framework_checks.items():
            if not passed:
                violations.append(check)
        
        for check, passed in general_checks.items():
            if not passed:
                violations.append(check)
        
        return {
            'compliance_status': 'PASSED' if all_passed else 'FAILED',
            'framework': framework,
            'framework_checks': framework_checks,
            'general_checks': general_checks,
            'violations': violations,
            'entities': entities,
            'confidence_score': self._calculate_confidence(all_passed, len(framework_checks) + len(general_checks)),
            'timestamp': '2026-06-17T10:00:00Z'
        }
    
    def _check_afcfta(self, entities: Dict) -> Dict[str, bool]:
        """AfCFTA-specific checks"""
        checks = {
            'rules_of_origin': self._check_origin_afcfta(entities),
            'tariff_classification': bool(entities.get('hs_code')),
            'sanctions_compliance': not self._is_sanctioned(entities),
            'documentation_complete': entities.get('is_complete', False)
        }
        return checks
    
    def _check_wto(self, entities: Dict) -> Dict[str, bool]:
        """WTO-specific checks"""
        checks = {
            'most_favored_nation': True,  # Simplified
            'national_treatment': True,   # Simplified
            'rules_of_origin': self._check_origin_wto(entities),
            'tariff_binding': bool(entities.get('hs_code')),
            'documentation_complete': entities.get('is_complete', False)
        }
        return checks
    
    def _check_eu_uk(self, entities: Dict) -> Dict[str, bool]:
        """EU-UK-specific checks"""
        checks = {
            'rules_of_origin': self._check_origin_eu_uk(entities),
            'tariff_classification': bool(entities.get('hs_code')),
            'sanctions_compliance': not self._is_sanctioned(entities),
            'documentation_complete': entities.get('is_complete', False)
        }
        return checks
    
    def _check_usmca(self, entities: Dict) -> Dict[str, bool]:
        """USMCA-specific checks"""
        checks = {
            'rules_of_origin': self._check_origin_usmca(entities),
            'tariff_classification': bool(entities.get('hs_code')),
            'sanctions_compliance': not self._is_sanctioned(entities),
            'documentation_complete': entities.get('is_complete', False),
            'north_american_content': True  # Simplified
        }
        return checks
    
    def _general_compliance_checks(self, entities: Dict) -> Dict[str, bool]:
        """General compliance checks applicable to all frameworks"""
        checks = {
            'has_valid_hs_code': self._validate_hs_code(entities.get('hs_code')),
            'has_valid_origin': bool(entities.get('origin')),
            'has_valid_destination': bool(entities.get('destination')),
            'shipper_consignee_diff': bool(entities.get('shipper')) and bool(entities.get('consignee')),
            'not_sanctioned_entity': not self._is_sanctioned_entity(entities.get('shipper', '')),
            'not_sanctioned_country': not self._is_sanctioned_country(entities.get('origin', ''))
        }
        return checks
    
    def _check_origin_afcfta(self, entities: Dict) -> bool:
        """AfCFTA rules of origin check"""
        origin = entities.get('origin', '')
        destination = entities.get('destination', '')
        # Simplified: Check if origin and destination are in Africa
        african_countries = ['South Africa', 'Nigeria', 'Kenya', 'Tanzania', 'Ghana', 'Egypt']
        return origin in african_countries and destination in african_countries
    
    def _check_origin_wto(self, entities: Dict) -> bool:
        """WTO rules of origin check"""
        return bool(entities.get('origin')) and bool(entities.get('destination'))
    
    def _check_origin_eu_uk(self, entities: Dict) -> bool:
        """EU-UK rules of origin check"""
        origin = entities.get('origin', '')
        destination = entities.get('destination', '')
        eu_countries = ['UK', 'France', 'Germany', 'Italy', 'Spain']
        return (origin in eu_countries and destination in eu_countries) or \
               (origin in eu_countries and destination == 'UK') or \
               (origin == 'UK' and destination in eu_countries)
    
    def _check_origin_usmca(self, entities: Dict) -> bool:
        """USMCA rules of origin check"""
        origin = entities.get('origin', '')
        usmca_countries = ['USA', 'Canada', 'Mexico']
        return origin in usmca_countries
    
    def _validate_hs_code(self, hs_code: str) -> bool:
        """Validate HS code format"""
        if not hs_code:
            return False
        import re
        clean_code = re.sub(r'[^0-9.]', '', str(hs_code))
        return bool(re.match(r'^\d{4,10}$', clean_code))
    
    def _is_sanctioned(self, entities: Dict) -> bool:
        """Check if any entity is sanctioned"""
        # Simple check for demonstration
        return False
    
    def _is_sanctioned_entity(self, name: str) -> bool:
        """Check if entity is in sanctions list"""
        if not name:
            return False
        return any(sanctioned.lower() in name.lower() for sanctioned in self.sanctions_list['entities'])
    
    def _is_sanctioned_country(self, country: str) -> bool:
        """Check if country is in sanctions list"""
        if not country:
            return False
        return any(sanctioned.lower() in country.lower() for sanctioned in self.sanctions_list['countries'])
    
    def _calculate_confidence(self, all_passed: bool, total_checks: int) -> float:
        """Calculate confidence score based on checks passed"""
        if not total_checks:
            return 0.0
        # In a real implementation, this would be more sophisticated
        return 0.90 if all_passed else 0.60