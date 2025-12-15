"""
Integration tests for Agent 2 - Information Enrichment Engine
Tests Agent 2 with real data and Agent 1+2 pipeline
"""
import pytest
import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agents_phase1 import Agent1DataValidation, Agent2DataEnrichment


class TestAgent2Integration:
    """Test Agent 2 with real data scenarios"""
    
    def test_agent2_with_sample_data(self):
        """Test Agent 2 with sample CSV data"""
        # Load sample data
        data_path = Path(__file__).parent.parent / 'data' / 'sample_data.csv'
        if not data_path.exists():
            pytest.skip("Sample data file not found")
        
        df = pd.read_csv(data_path)
        agent2 = Agent2DataEnrichment()
        
        # Test first 5 records
        for idx in range(min(5, len(df))):
            record = df.iloc[idx].to_dict()
            result = agent2.enrich_record(record)
            
            # Basic assertions
            assert 'confidence_agent2' in result
            assert 'enrichment_changes' in result
            assert 'record_enriched' in result
            assert 'execution_time_agent2' in result
            
            # Score should be 0-60
            assert 0 <= result['confidence_agent2'] <= 60
            
            # Execution time should be reasonable
            assert result['execution_time_agent2'] < 100  # Less than 100ms
    
    def test_agent2_batch_with_sample_data(self):
        """Test Agent 2 batch processing with sample data"""
        data_path = Path(__file__).parent.parent / 'data' / 'sample_data.csv'
        if not data_path.exists():
            pytest.skip("Sample data file not found")
        
        df = pd.read_csv(data_path)
        agent2 = Agent2DataEnrichment()
        
        # Test batch of 10 records
        records = df.head(10).to_dict('records')
        results = agent2.enrich_batch(records)
        
        assert len(results) == 10
        assert all('confidence_agent2' in r for r in results)
        assert all('enrichment_changes' in r for r in results)


class TestAgent1Agent2Pipeline:
    """Test combined Agent 1 + Agent 2 pipeline"""
    
    def test_validation_then_enrichment(self):
        """Test Agent 1 validation followed by Agent 2 enrichment"""
        agent1 = Agent1DataValidation()
        agent2 = Agent2DataEnrichment()
        
        # Test record with validation issues and enrichment needs
        record = {
            'name': 'Dr. Integration Test',
            'phone': '+91-98765-43210',  # Needs normalization
            'city': 'Banaglore',  # Typo
            'specialty': 'NEUROLOGY',  # Case issue
            'registration_no': 'MCI10012345',
            'clinic_address': 'Test Address',
            'pincode': '560001'
        }
        
        # Step 1: Validate
        val_result = agent1.validate_record(record)
        assert val_result['confidence_agent1'] == 100  # Should pass validation
        
        # Step 2: Enrich
        enr_result = agent2.enrich_record(record)
        assert enr_result['confidence_agent2'] == 60  # Full enrichment
        
        # Combined confidence
        combined_score = val_result['confidence_agent1'] + enr_result['confidence_agent2']
        assert combined_score == 160  # Maximum possible
        
        # Check enriched record
        enriched = enr_result['record_enriched']
        assert enriched['phone'] == '9876543210'
        assert enriched['city'] == 'Bangalore'
        assert enriched['specialty'] == 'Neurology'
    
    def test_failed_validation_still_enriches(self):
        """Test that Agent 2 still enriches even if Agent 1 fails"""
        agent1 = Agent1DataValidation()
        agent2 = Agent2DataEnrichment()
        
        # Record with validation failures
        record = {
            'name': 'Dr. Test',
            'phone': '12345',  # Invalid
            'city': 'Banaglore',  # Typo (will be enriched)
            'specialty': 'InvalidSpec',
            'registration_no': 'INVALID',
            'clinic_address': 'Test',
            'pincode': '999999'  # Invalid
        }
        
        # Agent 1 will fail
        val_result = agent1.validate_record(record)
        assert val_result['confidence_agent1'] < 100
        
        # Agent 2 should still enrich what it can
        enr_result = agent2.enrich_record(record)
        assert enr_result['record_enriched']['city'] == 'Bangalore'
        assert enr_result['confidence_agent2'] >= 20  # At least city enrichment
    
    def test_pipeline_with_perfect_record(self):
        """Test pipeline with already-perfect record"""
        agent1 = Agent1DataValidation()
        agent2 = Agent2DataEnrichment()
        
        record = {
            'name': 'Dr. Perfect Record',
            'phone': '9876543210',
            'city': 'Mumbai',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012345',
            'clinic_address': 'Perfect Address',
            'pincode': '400001'
        }
        
        val_result = agent1.validate_record(record)
        assert val_result['confidence_agent1'] == 100
        
        enr_result = agent2.enrich_record(record)
        assert enr_result['confidence_agent2'] == 10  # Only pincode verified
        assert len(enr_result['enrichment_changes']) == 0  # No changes needed
    
    def test_pipeline_batch_processing(self):
        """Test batch processing through both agents"""
        agent1 = Agent1DataValidation()
        agent2 = Agent2DataEnrichment()
        
        records = [
            {
                'name': 'Dr. A', 'phone': '+919876543210',
                'city': 'Bangalore', 'specialty': 'Cardiology',
                'registration_no': 'MCI10012345', 'clinic_address': 'Test',
                'pincode': '560001'
            },
            {
                'name': 'Dr. B', 'phone': '9876543211',
                'city': 'MUMBAI', 'specialty': 'NEUROLOGY',
                'registration_no': 'MCI10012346', 'clinic_address': 'Test',
                'pincode': '400001'
            }
        ]
        
        # Validate all
        val_results = agent1.validate_batch(records)
        assert len(val_results) == 2
        assert all(r['confidence_agent1'] == 100 for r in val_results)
        
        # Enrich all
        enr_results = agent2.enrich_batch(records)
        assert len(enr_results) == 2
        assert all('confidence_agent2' in r for r in enr_results)


class TestAgent2EdgeCases:
    """Test Agent 2 with edge cases and error conditions"""
    
    def test_missing_fields(self):
        """Test enrichment with missing fields"""
        agent2 = Agent2DataEnrichment()
        
        # Minimal record (only required fields)
        record = {
            'name': 'Dr. Minimal',
            'phone': '9876543210',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012345',
            'clinic_address': 'Test',
            'pincode': '560001'
        }
        
        result = agent2.enrich_record(record)
        assert 'confidence_agent2' in result
        assert result['confidence_agent2'] >= 0  # No errors
    
    def test_empty_string_fields(self):
        """Test enrichment with empty string fields"""
        agent2 = Agent2DataEnrichment()
        
        record = {
            'name': 'Dr. Test',
            'phone': '',  # Empty
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012345',
            'clinic_address': 'Test',
            'pincode': '560001'
        }
        
        result = agent2.enrich_record(record)
        # Should not crash
        assert 'confidence_agent2' in result
    
    def test_special_characters_in_city(self):
        """Test city with special characters"""
        agent2 = Agent2DataEnrichment()
        
        record = {
            'name': 'Dr. Test',
            'phone': '9876543210',
            'city': 'Banga!ore',  # Special char
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012345',
            'clinic_address': 'Test',
            'pincode': '560001'
        }
        
        result = agent2.enrich_record(record)
        # Should attempt fuzzy match despite special chars
        assert 'confidence_agent2' in result
    
    def test_very_long_specialty_name(self):
        """Test with very long specialty name"""
        agent2 = Agent2DataEnrichment()
        
        record = {
            'name': 'Dr. Test',
            'phone': '9876543210',
            'city': 'Bangalore',
            'specialty': 'A' * 200,  # Very long
            'registration_no': 'MCI10012345',
            'clinic_address': 'Test',
            'pincode': '560001'
        }
        
        result = agent2.enrich_record(record)
        # Should handle gracefully
        assert 'confidence_agent2' in result
    
    def test_unicode_in_name(self):
        """Test with unicode characters in name"""
        agent2 = Agent2DataEnrichment()
        
        record = {
            'name': 'Dr. राजेश शर्मा',  # Unicode
            'phone': '9876543210',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012345',
            'clinic_address': 'Test',
            'pincode': '560001'
        }
        
        result = agent2.enrich_record(record)
        # Should handle unicode
        assert 'confidence_agent2' in result
        assert result['record_enriched']['name'] == 'Dr. राजेश शर्मा'


class TestAgent2PerformanceIntegration:
    """Test Agent 2 performance with larger datasets"""
    
    def test_enrichment_speed_baseline(self):
        """Test enrichment speed meets performance target"""
        agent2 = Agent2DataEnrichment()
        
        record = {
            'name': 'Dr. Performance Test',
            'phone': '+91-98765-43210',
            'city': 'Banaglore',
            'specialty': 'NEUROLOGY',
            'registration_no': 'MCI10012345',
            'clinic_address': 'Test',
            'pincode': '560001'
        }
        
        # Run 10 times and check average
        times = []
        for _ in range(10):
            result = agent2.enrich_record(record)
            times.append(result['execution_time_agent2'])
        
        avg_time = sum(times) / len(times)
        assert avg_time < 50  # Average should be < 50ms
    
    def test_batch_performance(self):
        """Test batch processing performance"""
        agent2 = Agent2DataEnrichment()
        
        # Create 50 records
        records = [
            {
                'name': f'Dr. Test {i}',
                'phone': f'987654{i:04d}',
                'city': 'Bangalore',
                'specialty': 'Cardiology',
                'registration_no': f'MCI100{i:05d}',
                'clinic_address': 'Test',
                'pincode': '560001'
            }
            for i in range(50)
        ]
        
        import time
        start = time.time()
        results = agent2.enrich_batch(records)
        total_time = (time.time() - start) * 1000
        
        assert len(results) == 50
        assert total_time < 5000  # Should complete in < 5 seconds


class TestAgent2DataQualityImpact:
    """Test Agent 2's impact on data quality"""
    
    def test_enrichment_improves_quality(self):
        """Test that enrichment measurably improves data quality"""
        agent2 = Agent2DataEnrichment()
        
        # Record with multiple quality issues
        dirty_record = {
            'name': 'Dr. Test',
            'phone': '+91-98765-43210',  # Needs normalization
            'city': 'MUMBAI',  # Wrong case
            'specialty': 'CARDIO',  # Abbreviation
            'registration_no': 'MCI10012345',
            'clinic_address': 'Test',
            'pincode': '400001'
        }
        
        result = agent2.enrich_record(dirty_record)
        clean_record = result['record_enriched']
        
        # Verify improvements
        assert clean_record['phone'] == '9876543210'  # Normalized
        assert clean_record['city'] == 'Mumbai'  # Proper case
        assert 'Cardio' in clean_record['specialty']  # Expanded
        
        # Quality score should be high
        assert result['confidence_agent2'] >= 40
        
        # Should have made changes
        assert len(result['enrichment_changes']) >= 2
    
    def test_enrichment_audit_trail(self):
        """Test that enrichment maintains audit trail"""
        agent2 = Agent2DataEnrichment()
        
        record = {
            'name': 'Dr. Test',
            'phone': '+91 9876543210',
            'city': 'Banaglore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012345',
            'clinic_address': 'Test',
            'pincode': '560001'
        }
        
        result = agent2.enrich_record(record)
        changes = result['enrichment_changes']
        
        # Should document all changes
        assert any('Phone:' in c for c in changes)
        assert any('City:' in c for c in changes)
        
        # Changes should be descriptive
        for change in changes:
            assert len(change) > 10  # Not just "Phone changed"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
