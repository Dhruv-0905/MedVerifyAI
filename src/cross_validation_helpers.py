"""
MediSure Cross-Validation Helper Functions
Provides fraud detection and cross-validation utilities
"""

import re
from typing import Tuple, Dict, Any, Optional, List
from fuzzywuzzy import fuzz
import statistics

# Import existing helpers
from lookup_tables_extended import SPECIALTY_LIST


# ============================================================================
# DUPLICATE DETECTION DATABASE (In-memory for Phase 1)
# ============================================================================

# In production, this would be a real database
# For Phase 1, we'll use an in-memory dictionary
PROVIDER_DATABASE = {}


def register_provider(phone: str, registration_no: str, name: str):
    """
    Register a provider in the database (for duplicate detection)
    
    Args:
        phone: Phone number
        registration_no: Registration number
        name: Provider name
    """
    key = f"{phone}_{registration_no}"
    PROVIDER_DATABASE[key] = {
        'phone': phone,
        'registration_no': registration_no,
        'name': name
    }


def clear_provider_database():
    """Clear the provider database (for testing)"""
    global PROVIDER_DATABASE
    PROVIDER_DATABASE = {}


# ============================================================================
# 1. DUPLICATE DETECTION
# ============================================================================

def detect_duplicate(phone: str, registration_no: str, name: str, 
                     threshold: int = 80) -> Tuple[bool, Optional[str], int]:
    """
    Detect if provider is a duplicate based on phone, registration, and name.
    
    Args:
        phone: Phone number
        registration_no: Registration number
        name: Provider name
        threshold: Fuzzy match threshold for name similarity
    
    Returns:
        tuple: (is_duplicate, match_description, confidence_score)
        
    Examples:
        ('9876543210', 'MCI10012345', 'Dr. Rajesh Sharma')
        → (False, None, 100) if new
        → (True, 'Exact match: phone + registration', 0) if duplicate
    """
    if not phone or not registration_no:
        return False, None, 100  # Can't verify without key fields
    
    # Check for exact match on phone + registration
    key = f"{phone}_{registration_no}"
    
    if key in PROVIDER_DATABASE:
        existing = PROVIDER_DATABASE[key]
        
        # Check name similarity
        name_similarity = fuzz.ratio(name.upper(), existing['name'].upper())
        
        if name_similarity >= threshold:
            return True, f"Duplicate found: Same phone + registration (Name: {name_similarity}% match)", 0
        else:
            # Same phone + registration but different name = suspicious
            return True, f"SUSPICIOUS: Same phone + registration but different name ({existing['name']} vs {name})", 0
    
    # Check for partial duplicates (phone only or registration only)
    for existing_key, existing_data in PROVIDER_DATABASE.items():
        if existing_data['phone'] == phone:
            # Same phone, different registration = potential duplicate
            name_similarity = fuzz.ratio(name.upper(), existing_data['name'].upper())
            if name_similarity >= threshold:
                return True, f"Potential duplicate: Same phone, different registration", 50
        
        if existing_data['registration_no'] == registration_no:
            # Same registration, different phone = suspicious
            return True, f"SUSPICIOUS: Same registration, different phone", 0
    
    # No duplicate found
    return False, None, 100


# ============================================================================
# 2. REGISTRATION NUMBER VERIFICATION
# ============================================================================

VALID_REGISTRATION_PREFIXES = {
    'MCI': 'Medical Council of India',
    'DMC': 'Delhi Medical Council',
    'MMC': 'Maharashtra Medical Council',
    'KMC': 'Karnataka Medical Council',
    'TMC': 'Tamil Nadu Medical Council',
    'NMC': 'National Medical Commission'
}


def verify_registration_number(registration_no: str, specialty: str = None, 
                               city: str = None) -> Tuple[bool, Optional[str], int]:
    """
    Verify registration number authenticity and consistency.
    
    Args:
        registration_no: Registration number
        specialty: Medical specialty (optional)
        city: City (optional)
    
    Returns:
        tuple: (is_valid, warning_message, score)
        
    Examples:
        'MCI10012345' → (True, None, 10)
        'INVALID123' → (False, 'Invalid format', 0)
        'DMC10012345' in 'Mumbai' → (False, 'DMC is Delhi council, not Mumbai', 0)
    """
    if not registration_no:
        return False, "Registration number not provided", 0
    
    registration_no = str(registration_no).strip().upper()
    
    # Check format: PREFIX + DIGITS (at least 5 digits)
    pattern = r'^([A-Z]{3})(\d{5,})$'
    match = re.match(pattern, registration_no)
    
    if not match:
        return False, f"Invalid registration format: {registration_no}", 0
    
    prefix = match.group(1)
    
    # Check if prefix is valid
    if prefix not in VALID_REGISTRATION_PREFIXES:
        return False, f"Unknown registration council: {prefix}", 0
    
    # Additional checks based on city
    if city:
        city_upper = city.upper()
        
        # DMC should be in Delhi
        if prefix == 'DMC' and 'DELHI' not in city_upper:
            return False, f"DMC (Delhi Medical Council) registration but city is {city}", 0
        
        # MMC should be in Maharashtra cities
        if prefix == 'MMC' and 'MUMBAI' not in city_upper and 'PUNE' not in city_upper:
            return False, f"MMC (Maharashtra Medical Council) but city is {city}", 0
        
        # KMC should be in Karnataka cities
        if prefix == 'KMC' and 'BANGALORE' not in city_upper and 'BENGALURU' not in city_upper:
            return False, f"KMC (Karnataka Medical Council) but city is {city}", 0
        
        # TMC should be in Tamil Nadu cities
        if prefix == 'TMC' and 'CHENNAI' not in city_upper:
            return False, f"TMC (Tamil Nadu Medical Council) but city is {city}", 0
    
    # All checks passed
    return True, None, 10


# ============================================================================
# 3. YEARS OF PRACTICE VALIDATION
# ============================================================================

# Statistical parameters (would be calculated from real data in production)
MEAN_YEARS_PRACTICE = 12.0
STD_YEARS_PRACTICE = 6.0
MAX_REASONABLE_YEARS = 50


def validate_years_practice(years_practice: int) -> Tuple[bool, Optional[str], int]:
    """
    Validate years of practice using statistical analysis.
    
    Args:
        years_practice: Years of practice
    
    Returns:
        tuple: (is_valid, warning_message, score)
        
    Examples:
        12 → (True, None, 10)  # Normal
        55 → (False, 'Statistical outlier (z=7.2)', 0)  # Anomaly
        -5 → (False, 'Negative years', 0)  # Invalid
    """
    if years_practice is None:
        return True, "Years practice not provided (skipping check)", 10
    
        # Convert to string and check if empty or "None"
    years_str = str(years_practice).strip()
    
    if years_str == '' or years_str.lower() == 'none':
        return True, "Years practice not provided (skipping check)", 10
    try:
        years = int(years_practice)
    except (ValueError, TypeError):
        return False, f"Invalid years practice value: {years_practice}", 0
    
    # Check for negative
    if years < 0:
        return False, f"Negative years of practice: {years}", 0
    
    # Check for unreasonably high
    if years > MAX_REASONABLE_YEARS:
        return False, f"Unreasonably high years of practice: {years} (max expected: {MAX_REASONABLE_YEARS})", 0
    
    # Calculate z-score
    z_score = (years - MEAN_YEARS_PRACTICE) / STD_YEARS_PRACTICE
    
    # Check for statistical outlier (>3 standard deviations)
    if abs(z_score) > 3:
        return False, f"Statistical outlier: years={years}, z-score={z_score:.2f} (>3σ)", 0
    
    # Normal range
    return True, None, 10


# ============================================================================
# 4. GEOGRAPHIC CONSISTENCY VERIFICATION
# ============================================================================

def verify_geographic_consistency(clinic_address: str, city: str, 
                                 pincode: str) -> Tuple[bool, Optional[str], int]:
    """
    Verify that address, city, and pincode are geographically consistent.
    
    Args:
        clinic_address: Clinic address
        city: City name
        pincode: Pincode
    
    Returns:
        tuple: (is_consistent, warning_message, score)
        
    Examples:
        ('123 MG Road Bangalore', 'Bangalore', '560001')
        → (True, None, 10)
        
        ('45 Marine Drive Mumbai', 'Bangalore', '560001')
        → (False, 'Address mentions Mumbai but city is Bangalore', 0)
    """
    if not clinic_address or not city:
        return True, "Insufficient data for geographic check", 10
    
    address_upper = str(clinic_address).upper()
    city_upper = str(city).upper()
    
    # List of major cities to check
    MAJOR_CITIES = [
        'BANGALORE', 'BENGALURU', 'MUMBAI', 'DELHI', 'CHENNAI',
        'KOLKATA', 'HYDERABAD', 'PUNE', 'AHMEDABAD', 'JAIPUR'
    ]
    
    # Check if address mentions a different city
    for other_city in MAJOR_CITIES:
        if other_city in address_upper and other_city != city_upper:
            # Special case: Bangalore and Bengaluru are same
            if (city_upper in ['BANGALORE', 'BENGALURU'] and 
                other_city in ['BANGALORE', 'BENGALURU']):
                continue
            
            return False, f"Address mentions {other_city} but city is {city}", 0
    
    # Check if city is mentioned in address (good sign)
    if city_upper in address_upper or city_upper.replace(' ', '') in address_upper.replace(' ', ''):
        # City mentioned in address = good
        return True, None, 10
    
    # No obvious inconsistency, but city not mentioned
    return True, "City not mentioned in address (unable to fully verify)", 10


# ============================================================================
# 5. COMPREHENSIVE CROSS-VALIDATION
# ============================================================================

def cross_validate_record(record: Dict[str, Any], 
                         check_duplicates: bool = True) -> Dict[str, Any]:
    """
    Apply all cross-validation checks to a record.
    
    Args:
        record: Provider record dictionary
        check_duplicates: Whether to check for duplicates (set False for batch processing)
    
    Returns:
        dict: {
            'cross_validation_score': int (0-40),
            'cross_validation_flags': list of str,
            'cross_validation_details': dict
        }
    """
    score = 0
    flags = []
    details = {}
    
    # 1. Duplicate Detection (+10 if no duplicate, 0 if duplicate)
    if check_duplicates:
        phone = record.get('phone', '')
        registration_no = record.get('registration_no', '')
        name = record.get('name', '')
        
        is_dup, dup_msg, dup_score = detect_duplicate(phone, registration_no, name)
        
        # Cap duplicate check at 10 points
        if not is_dup:
            score += 10  # No duplicate found = +10
        else:
            score += 0   # Duplicate found = 0
        
        details['duplicate_check'] = {
            'is_duplicate': is_dup,
            'message': dup_msg,
            'score': 10 if not is_dup else 0
        }
        
        if is_dup:
            if 'SUSPICIOUS' in (dup_msg or ''):
                flags.append('🚨 SUSPICIOUS_DUPLICATE')
            else:
                flags.append('🚨 DUPLICATE_DETECTED')
    else:
        score += 10  # Skip duplicate check in batch mode
        details['duplicate_check'] = {'skipped': True, 'score': 10}
    
    # 2. Registration Verification (+10 or 0)
    registration_no = record.get('registration_no', '')
    specialty = record.get('specialty', '')
    city = record.get('city', '')
    
    reg_valid, reg_msg, reg_score = verify_registration_number(
        registration_no, specialty, city
    )
    score += reg_score  # Already returns 10 or 0
    details['registration_check'] = {
        'is_valid': reg_valid,
        'message': reg_msg,
        'score': reg_score
    }
    
    if not reg_valid:
        flags.append('⚠️ REGISTRATION_INVALID')
    
    # 3. Years Practice Validation (+10 or 0)
    years_practice = record.get('years_practice')
    
    years_valid, years_msg, years_score = validate_years_practice(years_practice)
    score += years_score  # Already returns 10 or 0
    details['years_practice_check'] = {
        'is_valid': years_valid,
        'message': years_msg,
        'score': years_score
    }
    
    if not years_valid:
        flags.append('⚠️ ANOMALY_PRACTICE_YEARS')
    
    # 4. Geographic Consistency (+10 or 0)
    clinic_address = record.get('clinic_address', '')
    
    geo_valid, geo_msg, geo_score = verify_geographic_consistency(
        clinic_address, city, record.get('pincode', '')
    )
    score += geo_score  # Already returns 10 or 0
    details['geographic_check'] = {
        'is_consistent': geo_valid,
        'message': geo_msg,
        'score': geo_score
    }
    
    if not geo_valid:
        flags.append('⚠️ GEOGRAPHIC_MISMATCH')
    
    # Ensure score is capped at 40
    score = min(score, 40)
    
    return {
        'cross_validation_score': score,
        'cross_validation_flags': flags,
        'cross_validation_details': details
    }

# ============================================================================
# SELF-TEST (Run when module is executed directly)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CROSS-VALIDATION HELPERS - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Test 1: Duplicate Detection
    print("\n" + "-"*70)
    print("TEST 1: Duplicate Detection")
    print("-"*70)
    
    clear_provider_database()
    
    # Register first provider
    register_provider('9876543210', 'MCI10012345', 'Dr. Rajesh Sharma')
    
    # Test 1a: No duplicate
    is_dup, msg, score = detect_duplicate('9876543211', 'MCI10012346', 'Dr. New Provider')
    print(f"   New provider: Duplicate={is_dup}, Score={score}")
    assert is_dup == False, "Should not be duplicate"
    
    # Test 1b: Exact duplicate
    is_dup, msg, score = detect_duplicate('9876543210', 'MCI10012345', 'Dr. Rajesh Sharma')
    print(f"   Exact duplicate: Duplicate={is_dup}, Score={score}")
    assert is_dup == True, "Should be duplicate"
    
    # Test 1c: Similar name
    is_dup, msg, score = detect_duplicate('9876543210', 'MCI10012345', 'Dr. R. Sharma')
    print(f"   Similar name: Duplicate={is_dup}, Score={score}")
    assert is_dup == True, "Should be duplicate (fuzzy match)"
    
    print("   ✓ PASSED")
    
    # Test 2: Registration Verification
    print("\n" + "-"*70)
    print("TEST 2: Registration Verification")
    print("-"*70)
    
    valid, msg, score = verify_registration_number('MCI10012345', 'Cardiology', 'Bangalore')
    print(f"   Valid MCI: Valid={valid}, Score={score}")
    assert valid == True, "Should be valid"
    
    valid, msg, score = verify_registration_number('DMC10012345', 'Cardiology', 'Mumbai')
    print(f"   DMC in Mumbai: Valid={valid}, Message={msg}")
    assert valid == False, "Should be invalid (DMC is Delhi)"
    
    valid, msg, score = verify_registration_number('INVALID123')
    print(f"   Invalid format: Valid={valid}, Score={score}")
    assert valid == False, "Should be invalid format"
    
    print("   ✓ PASSED")
    
    # Test 3: Years Practice Validation
    print("\n" + "-"*70)
    print("TEST 3: Years Practice Validation")
    print("-"*70)
    
    valid, msg, score = validate_years_practice(12)
    print(f"   Normal (12 years): Valid={valid}, Score={score}")
    assert valid == True, "Should be valid"
    
    valid, msg, score = validate_years_practice(55)
    print(f"   Outlier (55 years): Valid={valid}, Message={msg}")
    assert valid == False, "Should be outlier"
    
    valid, msg, score = validate_years_practice(-5)
    print(f"   Negative (-5 years): Valid={valid}, Score={score}")
    assert valid == False, "Should be invalid"
    
    print("   ✓ PASSED")
    
    # Test 4: Geographic Consistency
    print("\n" + "-"*70)
    print("TEST 4: Geographic Consistency")
    print("-"*70)
    
    valid, msg, score = verify_geographic_consistency('123 MG Road Bangalore', 'Bangalore', '560001')
    print(f"   Consistent: Valid={valid}, Score={score}")
    assert valid == True, "Should be consistent"
    
    valid, msg, score = verify_geographic_consistency('45 Marine Drive Mumbai', 'Bangalore', '560001')
    print(f"   Inconsistent: Valid={valid}, Message={msg}")
    assert valid == False, "Should be inconsistent"
    
    print("   ✓ PASSED")
    
    # Test 5: Complete Cross-Validation
    print("\n" + "-"*70)
    print("TEST 5: Complete Cross-Validation")
    print("-"*70)
    
    clear_provider_database()
    
    test_record = {
        'name': 'Dr. Test',
        'phone': '9876543210',
        'registration_no': 'MCI10012345',
        'specialty': 'Cardiology',
        'years_practice': 12,
        'city': 'Bangalore',
        'pincode': '560001',
        'clinic_address': '123 MG Road Bangalore'
    }
    
    result = cross_validate_record(test_record)
    print(f"   Score: {result['cross_validation_score']}/40")
    print(f"   Flags: {result['cross_validation_flags']}")
    assert result['cross_validation_score'] == 40, "Should score 40/40"
    
    print("   ✓ PASSED")
    
    print("\n" + "="*70)
    print("✅ ALL HELPER TESTS COMPLETE")
    print("="*70)
