"""
Comprehensive unit tests for Agent 2 - Information Enrichment Engine
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agents_phase1 import Agent2DataEnrichment, agent_2_enrichment


class TestAgent2Initialization:
    """Test Agent 2 initialization and metadata"""
    
    def test_agent_creation(self):
        """Test agent can be created"""
        agent = Agent2DataEnrichment()
        assert agent is not None
        assert agent.agent is not None
    
    def test_agent_info(self):
        """Test agent metadata"""
        agent = Agent2DataEnrichment()
        info = agent.get_agent_info()
        assert 'name' in info
        assert 'role' in info
        assert 'tools' in info
        assert len(info['tools']) == 5


class TestAgent2PhoneNormalization:
    """Test phone number normalization"""
    
    def test_phone_already_clean(self):
        """Test phone already in correct format"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012345', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['phone'] == '9876543210'
        assert result['confidence_agent2'] == 10  # Only pincode verified
    
    def test_phone_with_country_code(self):
        """Test phone with +91 prefix"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '+919876543210',
            'city': 'Mumbai', 'specialty': 'Neurology',
            'registration_no': 'MCI10012346', 'clinic_address': 'Test',
            'pincode': '400001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['phone'] == '9876543210'
        assert result['confidence_agent2'] == 25  # Phone(15) + Pincode(10)
        assert any('Phone:' in change for change in result['enrichment_changes'])
    
    def test_phone_with_dashes(self):
        """Test phone with dashes"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '98765-43210',
            'city': 'Delhi', 'specialty': 'Orthopedics',
            'registration_no': 'MCI10012347', 'clinic_address': 'Test',
            'pincode': '110001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['phone'] == '9876543210'
        assert result['confidence_agent2'] == 25  # Phone(15) + Pincode(10)
    
    def test_phone_with_spaces(self):
        """Test phone with spaces"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '98765 43210',
            'city': 'Chennai', 'specialty': 'Dermatology',
            'registration_no': 'MCI10012348', 'clinic_address': 'Test',
            'pincode': '600001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['phone'] == '9876543210'
        assert result['confidence_agent2'] == 25  # Phone(15) + Pincode(10)
    
    def test_phone_complex_format(self):
        """Test phone with complex formatting"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '+91-98765-43210',
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012349', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['phone'] == '9876543210'
        assert result['confidence_agent2'] == 25  # Phone(15) + Pincode(10)


class TestAgent2CityFuzzyMatching:
    """Test city fuzzy matching"""
    
    def test_city_exact_match(self):
        """Test city with exact match"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012345', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['city'] == 'Bangalore'
        assert result['confidence_agent2'] == 10  # Only pincode verified
    
    def test_city_case_correction(self):
        """Test city case correction"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'MUMBAI', 'specialty': 'Neurology',
            'registration_no': 'MCI10012346', 'clinic_address': 'Test',
            'pincode': '400001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['city'] == 'Mumbai'
        assert result['confidence_agent2'] == 30  # City(20) + Pincode(10)
        assert any('City:' in change for change in result['enrichment_changes'])
    
    def test_city_typo_correction(self):
        """Test city typo correction"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Banaglore', 'specialty': 'Orthopedics',
            'registration_no': 'MCI10012347', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['city'] == 'Bangalore'
        assert result['confidence_agent2'] == 30  # City(20) + Pincode(10)
        assert any('Banaglore → Bangalore' in change for change in result['enrichment_changes'])
    
    def test_city_synonym(self):
        """Test city that needs fuzzy matching"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Mumbi',  # Typo - will fuzzy match to Mumbai
            'specialty': 'Dermatology',
            'registration_no': 'MCI10012348', 'clinic_address': 'Test',
            'pincode': '400001'  # Mumbai pincode
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['city'] == 'Mumbai'
        assert result['confidence_agent2'] == 30  # City(20) + Pincode(10)
    
    def test_city_no_match(self):
        """Test city with no fuzzy match"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'UnknownCity', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012349', 'clinic_address': 'Test',
            'pincode': '999999'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['city'] == 'UnknownCity'
        # No city enrichment, no pincode verification
        assert result['confidence_agent2'] == 0


class TestAgent2SpecialtyNormalization:
    """Test specialty normalization"""
    
    def test_specialty_exact_match(self):
        """Test specialty exact match"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012345', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['specialty'] == 'Cardiology'
        assert result['confidence_agent2'] == 10  # Only pincode verified
    
    def test_specialty_case_correction(self):
        """Test specialty case correction"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Mumbai', 'specialty': 'NEUROLOGY',
            'registration_no': 'MCI10012346', 'clinic_address': 'Test',
            'pincode': '400001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['specialty'] == 'Neurology'
        assert result['confidence_agent2'] == 25  # Specialty(15) + Pincode(10)
        assert any('Specialty:' in change for change in result['enrichment_changes'])
    
    def test_specialty_fuzzy_match(self):
        """Test specialty fuzzy match"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Delhi', 'specialty': 'Ortho',
            'registration_no': 'MCI10012347', 'clinic_address': 'Test',
            'pincode': '110001'
        }
        result = agent.enrich_record(record)
        # "Ortho" matches to "Orthopedic Surgery" in lookup table
        assert 'Orthopedic' in result['record_enriched']['specialty']
        assert result['confidence_agent2'] >= 25  # Specialty(15) + Pincode(10)
    
    def test_specialty_abbreviation(self):
        """Test specialty abbreviation expansion"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Chennai', 'specialty': 'Derm',
            'registration_no': 'MCI10012348', 'clinic_address': 'Test',
            'pincode': '600001'
        }
        result = agent.enrich_record(record)
        # Should match to Dermatology
        assert 'Dermatology' in result['record_enriched']['specialty']
        assert result['confidence_agent2'] >= 25
    
    def test_specialty_no_match(self):
        """Test specialty with no match"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'InvalidSpecialty',
            'registration_no': 'MCI10012349', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent.enrich_record(record)
        assert result['record_enriched']['specialty'] == 'InvalidSpecialty'
        # Only pincode verified
        assert result['confidence_agent2'] == 10


class TestAgent2PincodeCityVerification:
    """Test pincode-city verification"""
    
    def test_pincode_city_match(self):
        """Test matching pincode and city"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012345', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent.enrich_record(record)
        assert result['confidence_agent2'] == 10  # Pincode verified
        assert len([c for c in result['enrichment_changes'] if 'Pincode' in c]) == 0
    
    def test_pincode_city_mismatch(self):
        """Test mismatched pincode and city"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'Neurology',
            'registration_no': 'MCI10012346', 'clinic_address': 'Test',
            'pincode': '400001'  # Mumbai pincode
        }
        result = agent.enrich_record(record)
        assert result['confidence_agent2'] == 0  # Mismatch detected
        assert any('Mumbai' in change for change in result['enrichment_changes'])
    
    def test_pincode_unknown(self):
        """Test unknown pincode"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'Orthopedics',
            'registration_no': 'MCI10012347', 'clinic_address': 'Test',
            'pincode': '999999'  # Unknown pincode
        }
        result = agent.enrich_record(record)
        # Can't verify unknown pincode, but no penalty
        assert result['confidence_agent2'] == 0
    
    def test_pincode_verification_after_city_enrichment(self):
        """Test pincode verified after city is corrected"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Banaglore',  # Typo, will be corrected to Bangalore
            'specialty': 'Dermatology',
            'registration_no': 'MCI10012348', 'clinic_address': 'Test',
            'pincode': '560001'  # Bangalore pincode
        }
        result = agent.enrich_record(record)
        # City(20) + Pincode(10) = 30
        assert result['confidence_agent2'] == 30
        assert result['record_enriched']['city'] == 'Bangalore'


class TestAgent2CompleteEnrichment:
    """Test complete enrichment scenarios"""
    
    def test_full_enrichment(self):
        """Test record needing all enrichments"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '+91-98765-43210',
            'city': 'Banaglore', 'specialty': 'NEUROLOGY',
            'registration_no': 'MCI10012345', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent.enrich_record(record)
        # Phone(15) + City(20) + Specialty(15) + Pincode(10) = 60
        assert result['confidence_agent2'] == 60
        assert result['record_enriched']['phone'] == '9876543210'
        assert result['record_enriched']['city'] == 'Bangalore'
        assert result['record_enriched']['specialty'] == 'Neurology'
        assert len(result['enrichment_changes']) == 3
    
    def test_no_enrichment_needed(self):
        """Test clean record"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Perfect', 'phone': '9876543210',
            'city': 'Mumbai', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012346', 'clinic_address': 'Test',
            'pincode': '400001'
        }
        result = agent.enrich_record(record)
        assert result['confidence_agent2'] == 10  # Only pincode verified
        assert len(result['enrichment_changes']) == 0
    
    def test_partial_enrichment(self):
        """Test record needing partial enrichment"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'DELHI', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012347', 'clinic_address': 'Test',
            'pincode': '110001'
        }
        result = agent.enrich_record(record)
        # City(20) + Pincode(10) = 30
        assert result['confidence_agent2'] == 30
        assert result['record_enriched']['city'] == 'Delhi'


class TestAgent2BatchProcessing:
    """Test batch processing"""
    
    def test_batch_enrichment(self):
        """Test batch enrichment of multiple records"""
        agent = Agent2DataEnrichment()
        records = [
            {
                'name': 'Dr. A', 'phone': '+919876543210',
                'city': 'Bangalore', 'specialty': 'Cardiology',
                'registration_no': 'MCI10012345', 'clinic_address': 'Test',
                'pincode': '560001'
            },
            {
                'name': 'Dr. B', 'phone': '9876543211',
                'city': 'MUMBAI', 'specialty': 'Neurology',
                'registration_no': 'MCI10012346', 'clinic_address': 'Test',
                'pincode': '400001'
            }
        ]
        results = agent.enrich_batch(records)
        
        assert len(results) == 2
        assert all('confidence_agent2' in r for r in results)
        assert all('enrichment_changes' in r for r in results)


class TestAgent2Performance:
    """Test Agent 2 performance metrics"""
    
    def test_execution_time_recorded(self):
        """Test execution time is recorded"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012345', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent.enrich_record(record)
        assert 'execution_time_agent2' in result
        assert result['execution_time_agent2'] >= 0
    
    def test_performance_target(self):
        """Test performance meets target"""
        agent = Agent2DataEnrichment()
        record = {
            'name': 'Dr. Test', 'phone': '+91-98765-43210',
            'city': 'Banaglore', 'specialty': 'NEUROLOGY',
            'registration_no': 'MCI10012345', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent.enrich_record(record)
        # Should complete in reasonable time
        assert result['execution_time_agent2'] < 100  # Less than 100ms


class TestAgent2BackwardCompatibility:
    """Test backward-compatible function"""
    
    def test_function_works(self):
        """Test backward-compatible function"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012345', 'clinic_address': 'Test',
            'pincode': '560001'
        }
        result = agent_2_enrichment(record)
        assert 'confidence_agent2' in result
        assert 'enrichment_changes' in result
        assert result['confidence_agent2'] == 10


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
