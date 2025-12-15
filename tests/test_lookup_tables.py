"""
Unit tests for lookup_tables_extended.py
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from lookup_tables_extended import (
    is_valid_indian_phone,
    is_valid_pincode,
    matches_reg_pattern,
    all_required_fields_present,
    normalize_phone,
    normalize_specialty,
    normalize_city,
    get_city_from_pincode,
    validate_pincode_city_match,
    get_lookup_stats,
    SPECIALTY_LIST,
    CITY_LIST,
    REQUIRED_FIELDS
)


class TestPhoneValidation:
    """Tests for phone number validation"""
    
    def test_valid_10_digit_phone(self):
        assert is_valid_indian_phone("9876543210") == True
        assert is_valid_indian_phone("8765432109") == True
        assert is_valid_indian_phone("7654321098") == True
        assert is_valid_indian_phone("6543210987") == True
    
    def test_valid_phone_with_91_prefix(self):
        assert is_valid_indian_phone("+919876543210") == True
        assert is_valid_indian_phone("919876543210") == True
    
    def test_valid_phone_with_0_prefix(self):
        assert is_valid_indian_phone("09876543210") == True
    
    def test_invalid_phone_too_short(self):
        assert is_valid_indian_phone("98765") == False
        assert is_valid_indian_phone("12345") == False
    
    def test_invalid_phone_wrong_prefix(self):
        assert is_valid_indian_phone("1234567890") == False  # Starts with 1
        assert is_valid_indian_phone("5234567890") == False  # Starts with 5
    
    def test_invalid_phone_empty(self):
        assert is_valid_indian_phone("") == False
        assert is_valid_indian_phone(None) == False


class TestPincodeValidation:
    """Tests for pincode validation"""
    
    def test_valid_pincode(self):
        assert is_valid_pincode("560001") == True
        assert is_valid_pincode("400001") == True
        assert is_valid_pincode("110001") == True
    
    def test_invalid_pincode_wrong_length(self):
        assert is_valid_pincode("12345") == False
        assert is_valid_pincode("1234567") == False
    
    def test_invalid_pincode_non_numeric(self):
        assert is_valid_pincode("abcdef") == False
        assert is_valid_pincode("56000A") == False
    
    def test_invalid_pincode_empty(self):
        assert is_valid_pincode("") == False
        assert is_valid_pincode(None) == False


class TestRegistrationValidation:
    """Tests for registration number validation"""
    
    def test_valid_registration_no_dash(self):
        assert matches_reg_pattern("MCI10012345") == True
        assert matches_reg_pattern("TN0001234") == True
        assert matches_reg_pattern("KA123456") == True
    
    def test_valid_registration_with_dash(self):
        assert matches_reg_pattern("MCI-10012345") == True
        assert matches_reg_pattern("TN-0001234") == True
    
    def test_invalid_registration_no_digits(self):
        assert matches_reg_pattern("INVALID") == False
        assert matches_reg_pattern("ABC") == False
    
    def test_invalid_registration_only_digits(self):
        assert matches_reg_pattern("12345678") == False
    
    def test_invalid_registration_empty(self):
        assert matches_reg_pattern("") == False
        assert matches_reg_pattern(None) == False


class TestRequiredFields:
    """Tests for required fields check"""
    
    def test_all_fields_present(self, sample_record):
        assert all_required_fields_present(sample_record) == True
    
    def test_missing_phone(self):
        record = {'name': 'Dr. Test', 'city': 'Bangalore'}
        assert all_required_fields_present(record) == False
    
    def test_empty_field(self):
        record = {
            'name': 'Dr. Test',
            'phone': '',  # Empty
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI001',
            'clinic_address': 'Test',
            'pincode': '560001'
        }
        assert all_required_fields_present(record) == False


class TestNormalization:
    """Tests for normalization functions"""
    
    def test_normalize_phone(self):
        assert normalize_phone("9876543210") == "919876543210"
        assert normalize_phone("+919876543210") == "919876543210"
        assert normalize_phone("09876543210") == "919876543210"
    
    def test_normalize_city_typo(self):
        assert normalize_city("Banaglore") == "Bangalore"
        assert normalize_city("Bombay") == "Mumbai"
        assert normalize_city("Calcutta") == "Kolkata"
    
    def test_normalize_city_valid(self):
        assert normalize_city("Bangalore") == "Bangalore"
        assert normalize_city("Chennai") == "Chennai"
    
    def test_normalize_specialty(self):
        assert normalize_specialty("CARDIOLOGY") == "Cardiology"
        assert normalize_specialty("cardiology") == "Cardiology"
        assert normalize_specialty("General Medicine") == "General Medicine"
    
    def test_normalize_specialty_invalid(self):
        assert normalize_specialty("FakeSpecialty") == None
        assert normalize_specialty("") == None


class TestPincodeCityMapping:
    """Tests for pincode-city lookup"""
    
    def test_get_city_from_pincode(self):
        assert get_city_from_pincode("560001") == "Bangalore"
        assert get_city_from_pincode("400001") == "Mumbai"
        assert get_city_from_pincode("110001") == "Delhi"
        assert get_city_from_pincode("600018") == "Chennai"
    
    def test_get_city_unknown_pincode(self):
        assert get_city_from_pincode("999999") == None
    
    def test_validate_pincode_city_match(self):
        is_match, expected = validate_pincode_city_match("560001", "Bangalore")
        assert is_match == True
        assert expected == "Bangalore"
    
    def test_validate_pincode_city_mismatch(self):
        is_match, expected = validate_pincode_city_match("560001", "Mumbai")
        assert is_match == False
        assert expected == "Bangalore"


class TestLookupStats:
    """Tests for lookup statistics"""
    
    def test_get_stats(self):
        stats = get_lookup_stats()
        assert 'specialties' in stats
        assert 'cities' in stats
        assert 'pincodes' in stats
        assert stats['specialties'] > 50
        assert stats['cities'] > 30
        assert stats['pincodes'] > 50


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
