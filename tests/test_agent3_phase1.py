"""
Comprehensive unit tests for Agent 3 - Cross-Validation Engine
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agents_phase1 import Agent3CrossValidation, agent_3_cross_validation


class TestAgent3Initialization:
    """Test Agent 3 initialization and metadata"""
    
    def test_agent_creation(self):
        """Test agent can be created"""
        agent = Agent3CrossValidation()
        assert agent is not None
        assert agent.agent is not None
    
    def test_agent_info(self):
        """Test agent metadata"""
        agent = Agent3CrossValidation()
        info = agent.get_agent_info()
        assert 'name' in info
        assert 'role' in info
        assert 'tools' in info
        assert len(info['tools']) == 4


class TestAgent3DuplicateDetection:
    """Test duplicate detection functionality"""
    
    def setup_method(self):
        """Clear database before each test"""
        self.agent = Agent3CrossValidation()
        self.agent.clear_database()
    
    def test_no_duplicate_clean_record(self):
        """Test clean record with no duplicates"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 MG Road Bangalore',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        assert result['confidence_agent3'] == 40  # Full score
        assert len(result['cross_validation_flags']) == 0
    
    def test_exact_duplicate_detected(self):
        """Test exact duplicate detection"""
        record = {
            'name': 'Dr. Duplicate', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 10
        }
        
        # Register first
        self.agent.register_provider(record)
        
        # Try to add duplicate
        result = self.agent.cross_validate_record(record)
        assert result['confidence_agent3'] == 30  # -10 for duplicate
        assert '🚨 DUPLICATE_DETECTED' in result['cross_validation_flags']
    
    def test_similar_name_duplicate(self):
        """Test duplicate with similar name"""
        record1 = {
            'name': 'Dr. Rajesh Sharma', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 10
        }
        
        record2 = {
            'name': 'Dr. R. Sharma',  # Similar name
            'phone': '9876543210',  # Same phone
            'registration_no': 'MCI10012345',  # Same registration
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'clinic_address': '123 Test', 'pincode': '560001',
            'years_practice': 10
        }
        
        self.agent.register_provider(record1)
        result = self.agent.cross_validate_record(record2)
        assert result['confidence_agent3'] == 30  # Duplicate detected
        assert len(result['cross_validation_flags']) > 0
    
    def test_different_name_same_phone_registration(self):
        """Test suspicious case: same phone+registration, different name"""
        record1 = {
            'name': 'Dr. John Doe', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 10
        }
        
        record2 = {
            'name': 'Dr. Jane Smith',  # Completely different name
            'phone': '9876543210',  # Same phone
            'registration_no': 'MCI10012345',  # Same registration
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'clinic_address': '123 Test', 'pincode': '560001',
            'years_practice': 10
        }
        
        self.agent.register_provider(record1)
        result = self.agent.cross_validate_record(record2)
        assert result['confidence_agent3'] == 30  # Suspicious duplicate
        assert '🚨 SUSPICIOUS_DUPLICATE' in result['cross_validation_flags']
    
    def test_skip_duplicate_check(self):
        """Test skipping duplicate check"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 10
        }
        
        result = self.agent.cross_validate_record(record, check_duplicates=False)
        assert 'duplicate_check' in result['cross_validation_details']
        assert result['cross_validation_details']['duplicate_check'].get('skipped') == True


class TestAgent3RegistrationVerification:
    """Test registration number verification"""
    
    def setup_method(self):
        """Initialize agent"""
        self.agent = Agent3CrossValidation()
        self.agent.clear_database()
    
    def test_valid_mci_registration(self):
        """Test valid MCI registration"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        assert result['cross_validation_details']['registration_check']['is_valid'] == True
        assert result['cross_validation_details']['registration_check']['score'] == 10
    
    def test_invalid_registration_format(self):
        """Test invalid registration format"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'INVALID123', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        assert result['cross_validation_details']['registration_check']['is_valid'] == False
        assert '⚠️ REGISTRATION_INVALID' in result['cross_validation_flags']
    
    def test_dmc_registration_wrong_city(self):
        """Test DMC (Delhi) registration in wrong city"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'DMC10012345', 'city': 'Mumbai',  # Should be Delhi
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '400001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        assert result['cross_validation_details']['registration_check']['is_valid'] == False
        assert '⚠️ REGISTRATION_INVALID' in result['cross_validation_flags']
    
    def test_kmc_registration_bangalore(self):
        """Test KMC (Karnataka) registration in Bangalore"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'KMC10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        assert result['cross_validation_details']['registration_check']['is_valid'] == True


class TestAgent3YearsPracticeValidation:
    """Test years of practice validation"""
    
    def setup_method(self):
        """Initialize agent"""
        self.agent = Agent3CrossValidation()
        self.agent.clear_database()
    
    def test_normal_years_practice(self):
        """Test normal years of practice"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 12
        }
        result = self.agent.cross_validate_record(record)
        assert result['cross_validation_details']['years_practice_check']['is_valid'] == True
        assert result['cross_validation_details']['years_practice_check']['score'] == 10
    
    def test_outlier_years_practice(self):
        """Test statistical outlier (too high)"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 55  # Outlier
        }
        result = self.agent.cross_validate_record(record)
        assert result['cross_validation_details']['years_practice_check']['is_valid'] == False
        assert '⚠️ ANOMALY_PRACTICE_YEARS' in result['cross_validation_flags']
    
    def test_negative_years_practice(self):
        """Test negative years of practice"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': -5
        }
        result = self.agent.cross_validate_record(record)
        assert result['cross_validation_details']['years_practice_check']['is_valid'] == False
    
    def test_zero_years_practice(self):
        """Test zero years of practice (valid for new doctors)"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 0
        }
        result = self.agent.cross_validate_record(record)
        # 0 years is within acceptable range (z-score check)
        assert result['cross_validation_details']['years_practice_check']['score'] >= 0
    
    def test_missing_years_practice(self):
        """Test missing years of practice"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001'
            # years_practice missing
        }
        result = self.agent.cross_validate_record(record)
        # Should skip check and give points
        assert result['cross_validation_details']['years_practice_check']['score'] == 10


class TestAgent3GeographicConsistency:
    """Test geographic consistency checks"""
    
    def setup_method(self):
        """Initialize agent"""
        self.agent = Agent3CrossValidation()
        self.agent.clear_database()
    
    def test_consistent_geography(self):
        """Test consistent address-city-pincode"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 MG Road Bangalore',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        assert result['cross_validation_details']['geographic_check']['is_consistent'] == True
        assert result['cross_validation_details']['geographic_check']['score'] == 10
    
    def test_address_mentions_different_city(self):
        """Test address mentioning different city"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '45 Marine Drive Mumbai',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        assert result['cross_validation_details']['geographic_check']['is_consistent'] == False
        assert '⚠️ GEOGRAPHIC_MISMATCH' in result['cross_validation_flags']
    
    def test_city_not_in_address(self):
        """Test city not mentioned in address"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 MG Road',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        # Should still pass (unable to fully verify, but no contradiction)
        assert result['cross_validation_details']['geographic_check']['score'] == 10
    
    def test_bangalore_bengaluru_synonym(self):
        """Test Bangalore/Bengaluru treated as same city"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 MG Road Bengaluru',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        assert result['cross_validation_details']['geographic_check']['is_consistent'] == True


class TestAgent3CompleteValidation:
    """Test complete cross-validation scenarios"""
    
    def setup_method(self):
        """Initialize agent"""
        self.agent = Agent3CrossValidation()
        self.agent.clear_database()
    
    def test_perfect_record_full_score(self):
        """Test perfect record gets full 40 points"""
        record = {
            'name': 'Dr. Perfect', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 MG Road Bangalore',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        assert result['confidence_agent3'] == 40
        assert len(result['cross_validation_flags']) == 0
    
    def test_multiple_issues_low_score(self):
        """Test record with multiple issues"""
        record = {
            'name': 'Dr. Issues', 'phone': '9876543210',
            'registration_no': 'INVALID',  # Invalid format
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'clinic_address': '123 Marine Drive Mumbai',  # Wrong city
            'pincode': '560001',
            'years_practice': 60  # Outlier
        }
        result = self.agent.cross_validate_record(record)
        assert result['confidence_agent3'] < 40
        assert len(result['cross_validation_flags']) >= 3  # Multiple flags
    
    def test_batch_processing(self):
        """Test batch cross-validation"""
        records = [
            {
                'name': 'Dr. A', 'phone': '9876543210',
                'registration_no': 'MCI10012345', 'city': 'Bangalore',
                'specialty': 'Cardiology', 'clinic_address': '123 Test',
                'pincode': '560001', 'years_practice': 10
            },
            {
                'name': 'Dr. B', 'phone': '9876543211',
                'registration_no': 'MCI10012346', 'city': 'Mumbai',
                'specialty': 'Neurology', 'clinic_address': '456 Test',
                'pincode': '400001', 'years_practice': 15
            }
        ]
        results = self.agent.cross_validate_batch(records)
        assert len(results) == 2
        assert all('confidence_agent3' in r for r in results)


class TestAgent3Performance:
    """Test Agent 3 performance metrics"""
    
    def setup_method(self):
        """Initialize agent"""
        self.agent = Agent3CrossValidation()
        self.agent.clear_database()
    
    def test_execution_time_recorded(self):
        """Test execution time is recorded"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        assert 'execution_time_agent3' in result
        assert result['execution_time_agent3'] >= 0
    
    def test_performance_target(self):
        """Test performance meets target"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 10
        }
        result = self.agent.cross_validate_record(record)
        # Should complete in reasonable time
        assert result['execution_time_agent3'] < 100  # Less than 100ms


class TestAgent3BackwardCompatibility:
    """Test backward-compatible function"""
    
    def test_function_works(self):
        """Test backward-compatible function"""
        record = {
            'name': 'Dr. Test', 'phone': '9876543210',
            'registration_no': 'MCI10012345', 'city': 'Bangalore',
            'specialty': 'Cardiology', 'clinic_address': '123 Test',
            'pincode': '560001', 'years_practice': 10
        }
        result = agent_3_cross_validation(record)
        assert 'confidence_agent3' in result
        assert 'cross_validation_flags' in result


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
