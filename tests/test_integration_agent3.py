"""
Integration tests for Agent 3 - Cross-Validation Engine
Tests Agent 3 with real data and full multi-agent pipeline
"""
import pytest
import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agents_phase1 import Agent1DataValidation, Agent2DataEnrichment, Agent3CrossValidation


class TestAgent3Integration:
    """Test Agent 3 with real data scenarios"""
    
    def setup_method(self):
        """Setup for each test"""
        self.agent3 = Agent3CrossValidation()
        self.agent3.clear_database()
    
    def test_agent3_with_sample_data(self):
        """Test Agent 3 with sample CSV data"""
        data_path = Path(__file__).parent.parent / 'data' / 'sample_data.csv'
        if not data_path.exists():
            pytest.skip("Sample data file not found")
        
        df = pd.read_csv(data_path)
        
        # Test first 5 records
        for idx in range(min(5, len(df))):
            record = df.iloc[idx].to_dict()
            result = self.agent3.cross_validate_record(record)
            
            # Basic assertions
            assert 'confidence_agent3' in result
            assert 'cross_validation_flags' in result
            assert 'cross_validation_details' in result
            assert 'execution_time_agent3' in result
            
            # Score should be 0-40
            assert 0 <= result['confidence_agent3'] <= 40
            
            # Execution time should be reasonable
            assert result['execution_time_agent3'] < 100  # Less than 100ms
    
    def test_agent3_batch_with_sample_data(self):
        """Test Agent 3 batch processing with sample data"""
        data_path = Path(__file__).parent.parent / 'data' / 'sample_data.csv'
        if not data_path.exists():
            pytest.skip("Sample data file not found")
        
        df = pd.read_csv(data_path)
        
        # Test batch of 10 records
        records = df.head(10).to_dict('records')
        results = self.agent3.cross_validate_batch(records)
        
        assert len(results) == 10
        assert all('confidence_agent3' in r for r in results)
        assert all('cross_validation_flags' in r for r in results)


class TestFullMultiAgentPipeline:
    """Test complete Agent 1 + Agent 2 + Agent 3 pipeline"""
    
    def setup_method(self):
        """Setup all agents"""
        self.agent1 = Agent1DataValidation()
        self.agent2 = Agent2DataEnrichment()
        self.agent3 = Agent3CrossValidation()
        self.agent3.clear_database()
    
    def test_full_pipeline_perfect_record(self):
        """Test complete pipeline with perfect record"""
        record = {
            'name': 'Dr. Pipeline Test',
            'phone': '9876543210',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012399',
            'years_practice': 10,
            'clinic_address': '123 MG Road Bangalore',
            'pincode': '560001'
        }
        
        # Step 1: Validate
        val_result = self.agent1.validate_record(record)
        assert val_result['confidence_agent1'] == 100
        
        # Step 2: Enrich
        enr_result = self.agent2.enrich_record(record)
        enriched_record = enr_result['record_enriched']
        
        # Step 3: Cross-validate
        cross_result = self.agent3.cross_validate_record(enriched_record)
        assert cross_result['confidence_agent3'] == 40
        
        # Combined score
        # Note: Perfect record needs no enrichment, so Agent 2 score is low (10)
        # This is CORRECT behavior - validation passes, cross-validation passes
        total = (val_result['confidence_agent1'] + 
                enr_result['confidence_agent2'] + 
                cross_result['confidence_agent3'])
        assert total >= 140  # High quality (validation + cross-validation = 140)
        assert val_result['confidence_agent1'] == 100  # Perfect validation
        assert cross_result['confidence_agent3'] == 40  # Perfect cross-validation

    
    def test_full_pipeline_with_enrichment(self):
        """Test pipeline with record needing enrichment"""
        record = {
            'name': 'Dr. Enrichment Test',
            'phone': '+91-9876543211',  # Needs normalization
            'city': 'MUMBAI',  # Needs case correction
            'specialty': 'Cardio',  # Needs expansion
            'registration_no': 'MCI10012400',
            'years_practice': 12,
            'clinic_address': '45 Marine Drive Mumbai',
            'pincode': '400001'
        }
        
        # Step 1: Validate (should pass despite formatting)
        val_result = self.agent1.validate_record(record)
        assert val_result['confidence_agent1'] > 0
        
        # Step 2: Enrich (should fix formatting)
        enr_result = self.agent2.enrich_record(record)
        assert len(enr_result['enrichment_changes']) > 0
        
        # Step 3: Cross-validate enriched record
        cross_result = self.agent3.cross_validate_record(enr_result['record_enriched'])
        assert cross_result['confidence_agent3'] > 0
    
    def test_full_pipeline_with_validation_issues(self):
        """Test pipeline with validation issues"""
        record = {
            'name': 'Dr',  # Too short
            'phone': '98765',  # Invalid
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012401',
            'years_practice': 8,
            'clinic_address': 'Test',
            'pincode': '560001'
        }
        
        # Step 1: Should fail validation
        val_result = self.agent1.validate_record(record)
        assert val_result['confidence_agent1'] < 100
        assert len(val_result['issues_validation']) > 0
        
        # Step 2: Enrichment still runs
        enr_result = self.agent2.enrich_record(record)
        
        # Step 3: Cross-validation still runs
        cross_result = self.agent3.cross_validate_record(record)
        assert 'confidence_agent3' in cross_result
    
    def test_full_pipeline_fraud_detection(self):
        """Test pipeline detects fraud"""
        record = {
            'name': 'Dr. Fraud Test',
            'phone': '9876543212',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012402',
            'years_practice': 10,
            'clinic_address': '123 Test',
            'pincode': '560001'
        }
        
        # First submission - should pass
        val1 = self.agent1.validate_record(record)
        enr1 = self.agent2.enrich_record(record)
        cross1 = self.agent3.cross_validate_record(enr1['record_enriched'])
        
        assert cross1['confidence_agent3'] == 40
        assert len(cross1['cross_validation_flags']) == 0
        
        # Register the provider
        self.agent3.register_provider(record)
        
        # Second submission - should detect duplicate
        cross2 = self.agent3.cross_validate_record(record)
        assert cross2['confidence_agent3'] < 40
        assert len(cross2['cross_validation_flags']) > 0
        assert any('DUPLICATE' in flag for flag in cross2['cross_validation_flags'])


class TestFraudDetectionScenarios:
    """Test various fraud detection scenarios"""
    
    def setup_method(self):
        """Setup agents"""
        self.agent3 = Agent3CrossValidation()
        self.agent3.clear_database()
    
    def test_registration_fraud_wrong_council(self):
        """Test fraud: Delhi council registration in Mumbai"""
        record = {
            'name': 'Dr. Fraud',
            'phone': '9876543213',
            'city': 'Mumbai',
            'specialty': 'Cardiology',
            'registration_no': 'DMC10012345',  # Delhi council
            'years_practice': 10,
            'clinic_address': '45 Marine Drive Mumbai',
            'pincode': '400001'
        }
        
        result = self.agent3.cross_validate_record(record)
        assert '⚠️ REGISTRATION_INVALID' in result['cross_validation_flags']
        assert result['confidence_agent3'] < 40
    
    def test_geographic_fraud_address_mismatch(self):
        """Test fraud: Address mentions different city"""
        record = {
            'name': 'Dr. Fraud',
            'phone': '9876543214',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012403',
            'years_practice': 10,
            'clinic_address': '45 Marine Drive Mumbai',  # Mumbai address
            'pincode': '560001'  # Bangalore pincode
        }
        
        result = self.agent3.cross_validate_record(record)
        assert '⚠️ GEOGRAPHIC_MISMATCH' in result['cross_validation_flags']
    
    def test_statistical_fraud_practice_years(self):
        """Test fraud: Impossible years of practice"""
        record = {
            'name': 'Dr. Fraud',
            'phone': '9876543215',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012404',
            'years_practice': 60,  # Unrealistic
            'clinic_address': '123 Test Bangalore',
            'pincode': '560001'
        }
        
        result = self.agent3.cross_validate_record(record)
        assert '⚠️ ANOMALY_PRACTICE_YEARS' in result['cross_validation_flags']
    
    def test_multiple_fraud_indicators(self):
        """Test record with multiple fraud indicators"""
        record = {
            'name': 'Dr. Multiple Fraud',
            'phone': '9876543216',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'INVALID123',  # Invalid format
            'years_practice': 65,  # Outlier
            'clinic_address': '45 Marine Drive Mumbai',  # Wrong city
            'pincode': '560001'
        }
        
        result = self.agent3.cross_validate_record(record)
        assert len(result['cross_validation_flags']) >= 3
        assert result['confidence_agent3'] < 20


class TestAgent3DataQuality:
    """Test Agent 3 impact on data quality"""
    
    def setup_method(self):
        """Setup agents"""
        self.agent1 = Agent1DataValidation()
        self.agent2 = Agent2DataEnrichment()
        self.agent3 = Agent3CrossValidation()
        self.agent3.clear_database()
    
    def test_high_quality_record_high_score(self):
        """Test high-quality record gets high combined score"""
        record = {
            'name': 'Dr. High Quality',
            'phone': '9876543217',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012405',
            'years_practice': 10,
            'clinic_address': '123 MG Road Bangalore',
            'pincode': '560001'
        }
        
        val = self.agent1.validate_record(record)
        enr = self.agent2.enrich_record(record)
        cross = self.agent3.cross_validate_record(record)
        
        combined = val['confidence_agent1'] + enr['confidence_agent2'] + cross['confidence_agent3']
        
        # High quality means validation + cross-validation both pass
        # Enrichment score is low because record doesn't need enrichment (which is good!)
        assert combined >= 140  # At least 70% overall confidence
        assert val['confidence_agent1'] == 100  # Perfect validation
        assert cross['confidence_agent3'] == 40  # Perfect cross-validation

    
    def test_low_quality_record_low_score(self):
        """Test low-quality record gets low combined score"""
        record = {
            'name': 'Dr',
            'phone': '98765',
            'city': 'Bangalore',
            'specialty': 'Unknown',
            'registration_no': 'INVALID',
            'years_practice': -5,
            'clinic_address': 'Test',
            'pincode': '123'
        }
        
        val = self.agent1.validate_record(record)
        enr = self.agent2.enrich_record(record)
        cross = self.agent3.cross_validate_record(record)
        
        combined = val['confidence_agent1'] + enr['confidence_agent2'] + cross['confidence_agent3']
        assert combined < 100  # Less than 50% confidence
    
    def test_cross_validation_adds_value(self):
        """Test Agent 3 adds value beyond Agents 1 & 2"""
        record = {
            'name': 'Dr. Test Value',
            'phone': '9876543218',
            'city': 'Mumbai',
            'specialty': 'Cardiology',
            'registration_no': 'DMC10012345',  # Wrong council for Mumbai
            'years_practice': 10,
            'clinic_address': '45 Marine Drive Mumbai',
            'pincode': '400001'
        }
        
        # Agents 1 & 2 might pass
        val = self.agent1.validate_record(record)
        enr = self.agent2.enrich_record(record)
        
        # Agent 3 should catch the registration issue
        cross = self.agent3.cross_validate_record(record)
        assert '⚠️ REGISTRATION_INVALID' in cross['cross_validation_flags']
        assert cross['confidence_agent3'] < 40


class TestAgent3Performance:
    """Test Agent 3 performance with various loads"""
    
    def setup_method(self):
        """Setup agent"""
        self.agent3 = Agent3CrossValidation()
        self.agent3.clear_database()
    
    def test_single_record_performance(self):
        """Test single record performance"""
        record = {
            'name': 'Dr. Performance',
            'phone': '9876543219',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012406',
            'years_practice': 10,
            'clinic_address': '123 Test',
            'pincode': '560001'
        }
        
        result = self.agent3.cross_validate_record(record)
        assert result['execution_time_agent3'] < 50  # Less than 50ms
    
    def test_batch_performance(self):
        """Test batch processing performance"""
        records = []
        for i in range(20):
            records.append({
                'name': f'Dr. Batch {i}',
                'phone': f'987654{i:04d}',
                'city': 'Bangalore',
                'specialty': 'Cardiology',
                'registration_no': f'MCI1001{i:04d}',
                'years_practice': 10,
                'clinic_address': '123 Test',
                'pincode': '560001'
            })
        
        import time
        start = time.time()
        results = self.agent3.cross_validate_batch(records)
        elapsed = (time.time() - start) * 1000
        
        assert len(results) == 20
        assert elapsed < 1000  # Less than 1 second for 20 records


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
