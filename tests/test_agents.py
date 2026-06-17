# tests/test_agents.py
import unittest
from agents.intake_agent import IntakeAgent
from agents.compliance_agent import ComplianceAgent
from agents.risk_broker_agent import RiskBrokerAgent

class TestAgents(unittest.TestCase):
    
    def setUp(self):
        self.intake = IntakeAgent()
        self.compliance = ComplianceAgent()
        self.risk_broker = RiskBrokerAgent()
        
        self.sample_document = """
        BILL OF LADING
        Shipper: ABC Trading Ltd.
        Consignee: XYZ Importers
        HS Code: 8471.30
        Origin: South Africa
        Destination: Tanzania
        Description: Computer equipment
        Weight: 500 kg
        """
    
    def test_intake_extraction(self):
        entities = self.intake.extract_entities(self.sample_document)
        
        self.assertEqual(entities.get('shipper'), 'ABC Trading Ltd.')
        self.assertEqual(entities.get('consignee'), 'XYZ Importers')
        self.assertEqual(entities.get('hs_code'), '8471.30')
        self.assertEqual(entities.get('origin'), 'South Africa')
        self.assertEqual(entities.get('destination'), 'Tanzania')
        self.assertTrue(entities.get('is_complete'))
    
    def test_compliance_check(self):
        entities = self.intake.extract_entities(self.sample_document)
        result = self.compliance.check_compliance(entities, 'AfCFTA')
        
        self.assertEqual(result['compliance_status'], 'PASSED')
        self.assertEqual(result['framework'], 'AfCFTA')
        self.assertIn('framework_checks', result)
    
    def test_risk_audit(self):
        entities = self.intake.extract_entities(self.sample_document)
        compliance_result = self.compliance.check_compliance(entities, 'AfCFTA')
        audit = self.risk_broker.audit_trade_document('AfCFTA', 'Dar es Salaam', compliance_result)
        
        self.assertIn('room_id', audit)
        self.assertIn('calculated_risk_index', audit)
        self.assertIsInstance(audit['calculated_risk_index'], int)
        self.assertTrue(0 <= audit['calculated_risk_index'] <= 100)
    
    def test_invalid_hs_code(self):
        doc = self.sample_document.replace('8471.30', 'INVALID')
        entities = self.intake.extract_entities(doc)
        self.assertFalse(self.intake.validate_hs_code(entities.get('hs_code')))

if __name__ == '__main__':
    unittest.main()