# agents.py
"""
MedVerify AI - Autonomous Validation Agents
Multi-agent system for healthcare provider directory validation
"""

import time
import re
from lookup_tables import (
    SPECIALTY_LIST,
    CITY_TYPOS,
    PINCODE_TO_CITY,
    is_valid_indian_phone,
    is_valid_pincode,
    matches_reg_pattern,
    all_required_fields_present,
    REQUIRED_FIELDS
)

# ============================================================================
# AGENT 1: DATA VALIDATION ENGINE
# ============================================================================
# Purpose: Validate provider data fields against strict rules
# Scoring: 5 checks × 20 points = 0-100
# ============================================================================

def _validate_phone(phone, issues_list):
    """
    Check if phone number is valid Indian format.
    
    Args:
        phone (str): Phone number to validate
        issues_list (list): List to append issues to
    
    Returns:
        int: 20 if valid, 0 if invalid
    """
    if not is_valid_indian_phone(phone):
        issues_list.append("Invalid phone format")
        return 0
    return 20


def _validate_pincode(pincode, issues_list):
    """
    Check if pincode is valid 6-digit Indian postal code.
    
    Args:
        pincode (str): Pincode to validate
        issues_list (list): List to append issues to
    
    Returns:
        int: 20 if valid, 0 if invalid
    """
    if not is_valid_pincode(pincode):
        issues_list.append("Invalid pincode format")
        return 0
    return 20


def _validate_specialty(specialty, issues_list):
    """
    Check if specialty is in approved SPECIALTY_LIST.
    
    Case-insensitive matching.
    
    Args:
        specialty (str): Specialty to validate
        issues_list (list): List to append issues to
    
    Returns:
        int: 20 if valid, 0 if invalid
    """
    if not specialty:
        issues_list.append("Specialty not provided")
        return 0
    
    # Case-insensitive check
    specialty_upper = str(specialty).strip().upper()
    specialty_list_upper = [s.upper() for s in SPECIALTY_LIST]
    
    if specialty_upper not in specialty_list_upper:
        issues_list.append(f"Specialty '{specialty}' not in approved list")
        return 0
    
    return 20


def _validate_registration_number(registration_no, issues_list):
    """
    Check if registration number matches expected pattern.
    
    Expected: 2-4 letter prefix + 5-11 digits
    Examples: MCI10012345, TN0001234, KA123456
    
    Args:
        registration_no (str): Registration number to validate
        issues_list (list): List to append issues to
    
    Returns:
        int: 20 if valid, 0 if invalid
    """
    if not matches_reg_pattern(registration_no):
        issues_list.append(f"Registration number '{registration_no}' format invalid")
        return 0
    
    return 20


def _validate_required_fields(record, issues_list):
    """
    Check if all required fields are present and non-empty.
    
    Args:
        record (dict): Record to validate
        issues_list (list): List to append issues to
    
    Returns:
        int: 20 if all present, 0 if any missing
    """
    if not all_required_fields_present(record):
        missing = []
        for field in REQUIRED_FIELDS:
            if field not in record or str(record[field]).strip() == '':
                missing.append(field)
        issues_list.append(f"Missing required fields: {', '.join(missing)}")
        return 0
    
    return 20


def agent_1_validation(record):
    """
    AGENT 1: Data Validation Engine
    
    Validates provider record fields against strict rules.
    
    Scoring System:
    - Phone format: 20 points
    - Pincode format: 20 points
    - Specialty in approved list: 20 points
    - Registration number pattern: 20 points
    - Required fields present: 20 points
    Total: 0-100 points
    
    Args:
        record (dict): Single provider record from DataFrame
    
    Returns:
        dict: {
            'confidence_agent1': int (0-100),
            'issues_validation': list of str,
            'execution_time_agent1': float (milliseconds)
        }
    """
    start_time = time.time()
    
    score = 0
    issues = []
    
    # ====================================================================
    # CHECK 1: REQUIRED FIELDS PRESENT (20 points)
    # ====================================================================
    score += _validate_required_fields(record, issues)
    
    # If required fields missing, we can't validate further
    if score == 0:
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        return {
            'confidence_agent1': 0,
            'issues_validation': issues,
            'execution_time_agent1': round(execution_time, 2)
        }
    
    # ====================================================================
    # CHECK 2: PHONE FORMAT (20 points)
    # ====================================================================
    phone = record.get('phone', '')
    score += _validate_phone(phone, issues)
    
    # ====================================================================
    # CHECK 3: PINCODE FORMAT (20 points)
    # ====================================================================
    pincode = record.get('pincode', '')
    score += _validate_pincode(pincode, issues)
    
    # ====================================================================
    # CHECK 4: SPECIALTY IN APPROVED LIST (20 points)
    # ====================================================================
    specialty = record.get('specialty', '')
    score += _validate_specialty(specialty, issues)
    
    # ====================================================================
    # CHECK 5: REGISTRATION NUMBER PATTERN (20 points)
    # ====================================================================
    registration_no = record.get('registration_no', '')
    score += _validate_registration_number(registration_no, issues)
    
    # ====================================================================
    # CALCULATE EXECUTION TIME
    # ====================================================================
    execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # ====================================================================
    # RETURN RESULTS
    # ====================================================================
    return {
        'confidence_agent1': score,  # 0-100
        'issues_validation': issues,  # List of what failed
        'execution_time_agent1': round(execution_time, 2)  # ms
    }


# ============================================================================
# TEST SUITE FOR AGENT 1
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AGENT 1 - DATA VALIDATION ENGINE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Test Case 1: Perfect Record
    print("\n📋 TEST 1: Perfect Record (All fields valid)")
    print("-" * 70)
    perfect_record = {
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
    result = agent_1_validation(perfect_record)
    print(f"  Confidence: {result['confidence_agent1']}/100")
    print(f"  Issues: {result['issues_validation'] if result['issues_validation'] else 'None'}")
    print(f"  Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 100, "Perfect record should score 100"
    print("  ✓ PASSED")
    
    # Test Case 2: Invalid Phone
    print("\n📋 TEST 2: Invalid Phone Number")
    print("-" * 70)
    invalid_phone_record = {
        'id': 10,
        'name': 'Dr. Nisha Nair',
        'phone': '98765',  # Too short
        'city': 'Chennai',
        'specialty': 'Neurology',
        'registration_no': 'MCI10012354',
        'years_practice': 2,
        'clinic_address': '444 Teynampet Chennai',
        'pincode': '600018'
    }
    result = agent_1_validation(invalid_phone_record)
    print(f"  Confidence: {result['confidence_agent1']}/100")
    print(f"  Issues: {result['issues_validation']}")
    print(f"  Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 80, "Should have 4 valid checks, 1 invalid"
    assert 'Invalid phone format' in result['issues_validation'], "Should flag phone"
    print("  ✓ PASSED")
    
    # Test Case 3: Invalid Specialty
    print("\n📋 TEST 3: Invalid Specialty")
    print("-" * 70)
    invalid_specialty_record = {
        'id': 12,
        'name': 'Dr. Kavya Singh',
        'phone': '9776543210',
        'city': 'Mumbai',
        'specialty': 'InvalidSpec',  # Not in list
        'registration_no': 'MCI10012356',
        'years_practice': 7,
        'clinic_address': '45 Fort Mumbai',
        'pincode': '400001'
    }
    result = agent_1_validation(invalid_specialty_record)
    print(f"  Confidence: {result['confidence_agent1']}/100")
    print(f"  Issues: {result['issues_validation']}")
    print(f"  Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 80, "Should have 4 valid checks, 1 invalid"
    assert any('Specialty' in issue for issue in result['issues_validation']), "Should flag specialty"
    print("  ✓ PASSED")
    
    # Test Case 4: Invalid Registration
    print("\n📋 TEST 4: Invalid Registration Number")
    print("-" * 70)
    invalid_reg_record = {
        'id': 9,
        'name': 'Dr. Amit Joshi',
        'phone': '9988123456',
        'city': 'Ahmedabad',
        'specialty': 'Pathology',
        'registration_no': 'INVALID_REG',  # Bad format
        'years_practice': 6,
        'clinic_address': '333 SG Highway Ahmedabad',
        'pincode': '380015'
    }
    result = agent_1_validation(invalid_reg_record)
    print(f"  Confidence: {result['confidence_agent1']}/100")
    print(f"  Issues: {result['issues_validation']}")
    print(f"  Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 80, "Should have 4 valid checks, 1 invalid"
    assert any('Registration' in issue for issue in result['issues_validation']), "Should flag registration"
    print("  ✓ PASSED")
    
    # Test Case 5: Missing Required Fields
    print("\n📋 TEST 5: Missing Required Fields")
    print("-" * 70)
    missing_fields_record = {
        'id': 99,
        'name': 'Dr. Unknown',
        # Missing phone, city, specialty, registration_no, clinic_address, pincode
    }
    result = agent_1_validation(missing_fields_record)
    print(f"  Confidence: {result['confidence_agent1']}/100")
    print(f"  Issues: {result['issues_validation']}")
    print(f"  Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 0, "Should score 0 if required fields missing"
    assert any('Missing' in issue for issue in result['issues_validation']), "Should flag missing fields"
    print("  ✓ PASSED")
    
    # Test Case 6: Multiple Issues
    print("\n📋 TEST 6: Multiple Issues (Invalid Phone + Specialty)")
    print("-" * 70)
    multi_issue_record = {
        'id': 100,
        'name': 'Dr. Test',
        'phone': '12345',  # Invalid
        'city': 'TestCity',
        'specialty': 'FakeSpecialty',  # Invalid
        'registration_no': 'MCI10012300',
        'years_practice': 5,
        'clinic_address': 'Test Address',
        'pincode': '560001'
    }
    result = agent_1_validation(multi_issue_record)
    print(f"  Confidence: {result['confidence_agent1']}/100")
    print(f"  Issues: {result['issues_validation']}")
    print(f"  Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 60, "Should have 3 valid checks, 2 invalid"
    assert len(result['issues_validation']) == 2, "Should have 2 issues"
    print("  ✓ PASSED")
    
    # Test Case 7: +91 Format Phone
    print("\n📋 TEST 7: Phone with +91 Format")
    print("-" * 70)
    plus91_record = {
        'id': 7,
        'name': 'Dr. Sanjay Reddy',
        'phone': '+919876123456',  # +91 format
        'city': 'Bangalore',
        'specialty': 'Ophthalmology',
        'registration_no': 'MCI10012351',
        'years_practice': 10,
        'clinic_address': '111 Whitefield Bangalore',
        'pincode': '560066'
    }
    result = agent_1_validation(plus91_record)
    print(f"  Confidence: {result['confidence_agent1']}/100")
    print(f"  Issues: {result['issues_validation']}")
    print(f"  Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 100, "Should accept +91 format"
    print("  ✓ PASSED")
    
    # Test Case 8: Case-Insensitive Specialty
    print("\n📋 TEST 8: Case-Insensitive Specialty")
    print("-" * 70)
    case_insensitive_record = {
        'id': 50,
        'name': 'Dr. Test',
        'phone': '9876543210',
        'city': 'Bangalore',
        'specialty': 'CARDIOLOGY',  # Uppercase
        'registration_no': 'MCI10012500',
        'years_practice': 5,
        'clinic_address': 'Test Address',
        'pincode': '560001'
    }
    result = agent_1_validation(case_insensitive_record)
    print(f"  Confidence: {result['confidence_agent1']}/100")
    print(f"  Issues: {result['issues_validation']}")
    assert result['confidence_agent1'] == 100, "Should accept uppercase specialty"
    print("  ✓ PASSED")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - AGENT 1 VALIDATION ENGINE WORKING CORRECTLY")
    print("="*70)

