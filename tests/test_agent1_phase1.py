"""
Comprehensive unit tests for Agent 1 - Data Validation Engine
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agents_phase1 import Agent1DataValidation, agent_1_validation

@pytest.fixture
def sample_record():
    """Single valid provider record for testing"""
    return {
        'id': 1,
        'name': 'Dr. Rajesh Sharma',
        'phone': '9876543210',
        'city': 'Bangalore',
        'specialty': 'Cardiology',
        'registration_no': 'MCI10012345',
        'years_practice': 8,
        'clinic_address': '123 MG Road Bangalore',
        'pincode': '560001'
    }

class TestAgent1Initialization:
    """Test Agent 1 initialization and metadata"""

    def setup_method(self):
        self.agent = Agent1DataValidation()

    def test_agent_creation(self):
        """Test agent can be created"""
        assert self.agent is not None
        assert self.agent.agent is not None

    def test_agent_info(self):
        """Test agent metadata"""
        info = self.agent.get_agent_info()
        assert 'name' in info
        assert 'role' in info
        assert 'tools' in info
        assert len(info['tools']) == 5

class TestAgent1PerfectRecords:
    """Test Agent 1 with perfectly valid records"""

    def setup_method(self):
        self.agent = Agent1DataValidation()

    def test_perfect_record(self, sample_record):
        """Test validation of perfect record"""
        result = self.agent.validate_record(sample_record)
        assert result['confidence_agent1'] == 100
        assert len(result['issues_validation']) == 0
        assert result['execution_time_agent1'] >= 0

    def test_multiple_perfect_records(self):
        """Test batch validation of perfect records"""
        records = [
            {
                'id': i,
                'name': f'Dr. Test {i}',
                'phone': f'987654321{i}',
                'city': 'Bangalore',
                'specialty': 'Cardiology',
                'registration_no': f'MCI1001234{i}',
                'years_practice': 5,
                'clinic_address': f'Address {i}',
                'pincode': '560001'
            }
            for i in range(5)
        ]
        results = self.agent.validate_batch(records)
        assert len(results) == 5
        assert all(r['confidence_agent1'] == 100 for r in results)

class TestAgent1PhoneValidation:
    """Test phone number validation logic"""

    def setup_method(self):
        self.agent = Agent1DataValidation()
        self.record_base = {'name': 'Dr. Test', 'city': 'Bangalore', 'specialty': 'Cardiology', 'registration_no': 'MCI10012345', 'clinic_address': 'Test', 'pincode': '560001'}

    def test_valid_10_digit_phone(self):
        record = self.record_base.copy()
        record['phone'] = '9876543210'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 100

    def test_valid_phone_with_91(self):
        record = self.record_base.copy()
        record['phone'] = '+919876543210'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 100

    def test_invalid_phone_too_short(self):
        record = self.record_base.copy()
        record['phone'] = '12345'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 80
        assert any('phone' in issue.lower() for issue in result['issues_validation'])

    def test_invalid_phone_wrong_prefix(self):
        record = self.record_base.copy()
        record['phone'] = '1234567890'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 80

class TestAgent1PincodeValidation:
    """Test pincode validation logic"""
    def setup_method(self):
        self.agent = Agent1DataValidation()
        self.record_base = {'name': 'Dr. Test', 'phone': '9876543210', 'city': 'Bangalore', 'specialty': 'Cardiology', 'registration_no': 'MCI10012345', 'clinic_address': 'Test'}

    def test_valid_6_digit_pincode(self):
        record = self.record_base.copy()
        record['pincode'] = '560001'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 100

    def test_invalid_pincode_too_short(self):
        record = self.record_base.copy()
        record['pincode'] = '12345'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 80
        assert any('pincode' in issue.lower() for issue in result['issues_validation'])

    def test_invalid_pincode_non_numeric(self):
        record = self.record_base.copy()
        record['pincode'] = 'ABCDEF'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 80

class TestAgent1SpecialtyValidation:
    """Test specialty validation logic"""
    def setup_method(self):
        self.agent = Agent1DataValidation()
        self.record_base = {'name': 'Dr. Test', 'phone': '9876543210', 'city': 'Bangalore', 'registration_no': 'MCI10012345', 'clinic_address': 'Test', 'pincode': '560001'}

    def test_valid_specialty_exact_match(self):
        record = self.record_base.copy()
        record['specialty'] = 'Cardiology'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 100

    def test_valid_specialty_case_insensitive(self):
        record = self.record_base.copy()
        record['specialty'] = 'CARDIOLOGY'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 100

    def test_invalid_specialty_not_in_list(self):
        record = self.record_base.copy()
        record['specialty'] = 'FakeSpecialty'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 80
        assert any('specialty' in issue.lower() for issue in result['issues_validation'])

class TestAgent1RegistrationValidation:
    """Test registration number validation"""
    def setup_method(self):
        self.agent = Agent1DataValidation()
        self.record_base = {'name': 'Dr. Test', 'phone': '9876543210', 'city': 'Bangalore', 'specialty': 'Cardiology', 'clinic_address': 'Test', 'pincode': '560001'}

    def test_valid_registration_no_dash(self):
        record = self.record_base.copy()
        record['registration_no'] = 'MCI10012345'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 100

    def test_valid_registration_with_dash(self):
        record = self.record_base.copy()
        record['registration_no'] = 'MCI-10012345'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 100

    # ----- START OF REPLACEMENT -----
    def test_truly_invalid_registration_format(self):
        """Test that non-conforming registration formats are still rejected."""
        record = self.record_base.copy()
        record['registration_no'] = 'INVALID_TEXT_ONLY'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] < 100
        assert any('registration' in issue.lower() for issue in result['issues_validation'])

    def test_valid_short_registration_no(self):
        """Test that a short registration number (3 digits) is now VALID."""
        record = self.record_base.copy()
        record['registration_no'] = 'MCI-123'
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 100
        assert "Invalid registration number format" not in str(result.get('issues_validation', []))
    # ----- END OF REPLACEMENT -----

class TestAgent1RequiredFields:
    """Test required fields validation"""
    def setup_method(self):
        self.agent = Agent1DataValidation()

    def test_all_fields_present(self, sample_record):
        result = self.agent.validate_record(sample_record)
        assert result['confidence_agent1'] == 100

    def test_missing_phone(self):
        record = {'name': 'Dr. Test', 'city': 'Bangalore'}
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 0
        assert any('missing' in issue.lower() for issue in result['issues_validation'])

    def test_empty_field(self):
        record = {
            'name': 'Dr. Test', 'phone': '', 'city': 'Bangalore', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012345', 'clinic_address': 'Test', 'pincode': '560001'
        }
        result = self.agent.validate_record(record)
        assert result['confidence_agent1'] == 0

class TestAgent1Performance:
    """Test Agent 1 performance metrics"""
    def setup_method(self):
        self.agent = Agent1DataValidation()

    def test_execution_time_recorded(self, sample_record):
        result = self.agent.validate_record(sample_record)
        assert 'execution_time_agent1' in result
        assert result['execution_time_agent1'] >= 0

    def test_performance_target(self, sample_record):
        result = self.agent.validate_record(sample_record)
        assert result['execution_time_agent1'] < 100

class TestAgent1BackwardCompatibility:
    """Test backward-compatible function"""
    def test_function_works(self, sample_record):
        result = agent_1_validation(sample_record)
        assert 'confidence_agent1' in result
        assert 'issues_validation' in result
        assert result['confidence_agent1'] == 100

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

