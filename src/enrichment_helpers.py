"""
MediSure Enrichment Helper Functions
Provides data enrichment and normalization utilities
"""

import re
from typing import Tuple, Dict, Any, Optional
from fuzzywuzzy import fuzz, process

# Import lookup tables
from lookup_tables_extended import (
    CITY_LIST,
    SPECIALTY_LIST,
    normalize_specialty as lookup_normalize_specialty
)


# ============================================================================
# PINCODE-CITY MAPPING (Sample - expand as needed)
# ============================================================================

PINCODE_CITY_MAP = {
    # Bangalore
    '560001': 'Bangalore', '560002': 'Bangalore', '560003': 'Bangalore',
    '560004': 'Bangalore', '560005': 'Bangalore', '560010': 'Bangalore',
    
    # Mumbai
    '400001': 'Mumbai', '400002': 'Mumbai', '400003': 'Mumbai',
    '400004': 'Mumbai', '400005': 'Mumbai', '400010': 'Mumbai',
    
    # Delhi
    '110001': 'Delhi', '110002': 'Delhi', '110003': 'Delhi',
    '110004': 'Delhi', '110005': 'Delhi', '110010': 'Delhi',
    
    # Chennai
    '600001': 'Chennai', '600002': 'Chennai', '600003': 'Chennai',
    '600004': 'Chennai', '600005': 'Chennai', '600010': 'Chennai',
    '600018': 'Chennai',
    
    # Kolkata
    '700001': 'Kolkata', '700002': 'Kolkata', '700003': 'Kolkata',
    
    # Hyderabad
    '500001': 'Hyderabad', '500002': 'Hyderabad', '500003': 'Hyderabad',
    
    # Pune
    '411001': 'Pune', '411002': 'Pune', '411003': 'Pune',
}


# ============================================================================
# 1. PHONE NORMALIZATION
# ============================================================================

def normalize_phone(phone: str) -> Tuple[str, bool, Optional[str]]:
    """
    Normalize Indian phone number to standard 10-digit format.
    
    Args:
        phone: Input phone number (any format)
    
    Returns:
        tuple: (normalized_phone, was_changed, change_description)
        
    Examples:
        '+91 9876543210' → ('9876543210', True, 'Removed country code and spaces')
        '98765-43210' → ('9876543210', True, 'Removed dashes')
        '9876543210' → ('9876543210', False, None)
    """
    if not phone:
        return phone, False, None
    
    original = str(phone).strip()
    
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', original)
    
    # Remove country code if present (91 at start)
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    
    # Check if we made any changes
    if cleaned != original:
        changes = []
        if '+' in original or '-' in original or ' ' in original:
            changes.append('Removed formatting characters')
        if original.startswith('+91') or original.startswith('91'):
            changes.append('Removed country code')
        
        change_desc = ', '.join(changes) if changes else 'Normalized format'
        return cleaned, True, change_desc
    
    return original, False, None


# ============================================================================
# 2. CITY FUZZY MATCHING
# ============================================================================

def fuzzy_match_city(city: str, threshold: int = 85) -> Tuple[str, bool, Optional[str], int]:
    """
    Match city name using fuzzy string matching.
    
    Args:
        city: Input city name
        threshold: Minimum similarity score (0-100)
    
    Returns:
        tuple: (matched_city, was_changed, change_description, similarity_score)
        
    Examples:
        'Banaglore' → ('Bangalore', True, 'Fuzzy matched: Banaglore → Bangalore', 94)
        'MUMBAI' → ('Mumbai', True, 'Case corrected', 100)
        'Bangalore' → ('Bangalore', False, None, 100)
    """
    if not city:
        return city, False, None, 0
    
    original = str(city).strip()
    
    # Try exact match (case-insensitive)
    for valid_city in CITY_LIST:
        if original.upper() == valid_city.upper():
            if original != valid_city:
                # Case differs
                return valid_city, True, f'Case corrected: {original} → {valid_city}', 100
            else:
                # Exact match
                return original, False, None, 100
    
    # Try fuzzy matching
    result = process.extractOne(original, CITY_LIST, scorer=fuzz.ratio)
    
    if result:
        matched_city, similarity = result
        
        if similarity >= threshold:
            if matched_city != original:
                return matched_city, True, f'Fuzzy matched: {original} → {matched_city}', similarity
            else:
                return original, False, None, similarity
    
    # No match found
    return original, False, None, 0


# ============================================================================
# 3. SPECIALTY NORMALIZATION
# ============================================================================

def normalize_specialty_enhanced(specialty: str, threshold: int = 80) -> Tuple[str, bool, Optional[str], int]:
    """
    Normalize medical specialty using exact match, fuzzy match, and abbreviations.
    
    Args:
        specialty: Input specialty
        threshold: Minimum similarity score for fuzzy match
    
    Returns:
        tuple: (normalized_specialty, was_changed, change_description, similarity_score)
        
    Examples:
        'CARDIOLOGY' → ('Cardiology', True, 'Case corrected', 100)
        'Cardio' → ('Cardiology', True, 'Fuzzy matched: Cardio → Cardiology', 86)
        'Cardiology' → ('Cardiology', False, None, 100)
    """
    if not specialty:
        return specialty, False, None, 0
    
    original = str(specialty).strip()
    
    # Try exact match (case-insensitive)
    for valid_specialty in SPECIALTY_LIST:
        if original.upper() == valid_specialty.upper():
            if original != valid_specialty:
                return valid_specialty, True, f'Case corrected: {original} → {valid_specialty}', 100
            else:
                return original, False, None, 100
    
    # Try fuzzy matching
    result = process.extractOne(original, SPECIALTY_LIST, scorer=fuzz.ratio)
    
    if result:
        matched_specialty, similarity = result
        
        if similarity >= threshold:
            if matched_specialty != original:
                return matched_specialty, True, f'Fuzzy matched: {original} → {matched_specialty}', similarity
            else:
                return original, False, None, similarity
    
    # Try using existing normalize_specialty from lookup_tables
    normalized = lookup_normalize_specialty(original)
    if normalized and normalized != original:
        return normalized, True, f'Normalized via lookup: {original} → {normalized}', 90
    
    # No match found
    return original, False, None, 0


# ============================================================================
# 4. PINCODE-CITY VERIFICATION
# ============================================================================

def verify_pincode_city(pincode: str, city: str) -> Tuple[bool, Optional[str]]:
    """
    Verify if pincode matches the city.
    
    Args:
        pincode: 6-digit pincode
        city: City name
    
    Returns:
        tuple: (is_valid, warning_message)
        
    Examples:
        ('560001', 'Bangalore') → (True, None)
        ('400001', 'Bangalore') → (False, 'Pincode 400001 belongs to Mumbai, not Bangalore')
        ('999999', 'Bangalore') → (False, 'Pincode 999999 not in database')
    """
    if not pincode or not city:
        return True, None  # Can't verify if data missing
    
    pincode = str(pincode).strip()
    city = str(city).strip()
    
    expected_city = PINCODE_CITY_MAP.get(pincode)
    
    if expected_city:
        # Pincode is in our database
        if expected_city.upper() == city.upper():
            return True, None  # Match!
        else:
            return False, f'Pincode {pincode} belongs to {expected_city}, not {city}'
    else:
        # Pincode not in database - can't verify
        return True, f'Pincode {pincode} not in verification database'


# ============================================================================
# 5. ADDRESS ENRICHMENT (PLACEHOLDER)
# ============================================================================

def enrich_address(address: str, city: str, pincode: str) -> Tuple[str, bool, Optional[str]]:
    """
    Enrich clinic address with standardized formatting.
    
    Args:
        address: Clinic address
        city: City name
        pincode: Pincode
    
    Returns:
        tuple: (enriched_address, was_changed, change_description)
        
    Note: This is a placeholder for future enhancement (Phase 2/3)
    """
    # For Phase 1, just return original
    # In Phase 2/3, we could:
    # - Standardize address format
    # - Add missing city/pincode
    # - Geocode address
    
    if not address:
        return address, False, None
    
    return str(address).strip(), False, None


# ============================================================================
# COMPREHENSIVE ENRICHMENT FUNCTION
# ============================================================================

def enrich_record_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply all enrichment functions to a record.
    
    Args:
        record: Provider record dictionary
    
    Returns:
        dict: {
            'enriched_record': dict (updated record),
            'changes': list of str (audit trail),
            'score': int (enrichment score 0-60)
        }
    """
    enriched = record.copy()
    changes = []
    score = 0
    
    # 1. Phone normalization (+15 points if changed)
    if 'phone' in record:
        norm_phone, phone_changed, phone_desc = normalize_phone(record['phone'])
        if phone_changed:
            enriched['phone'] = norm_phone
            changes.append(f'Phone: {phone_desc}')
            score += 15
    
    # 2. City fuzzy matching (+20 points if changed)
    if 'city' in record:
        matched_city, city_changed, city_desc, city_sim = fuzzy_match_city(record['city'])
        if city_changed:
            enriched['city'] = matched_city
            changes.append(f'City: {city_desc}')
            score += 20
    
    # 3. Specialty normalization (+15 points if changed)
    if 'specialty' in record:
        norm_spec, spec_changed, spec_desc, spec_sim = normalize_specialty_enhanced(record['specialty'])
        if spec_changed:
            enriched['specialty'] = norm_spec
            changes.append(f'Specialty: {spec_desc}')
            score += 15
    
    # 4. Pincode-city verification (+10 points if verified)
    if 'pincode' in record and 'city' in enriched:
        is_valid, warning = verify_pincode_city(record['pincode'], enriched['city'])
        if is_valid and not warning:
            score += 10
        elif warning:
            changes.append(f'WARNING: {warning}')
    
    return {
        'enriched_record': enriched,
        'changes': changes,
        'score': score
    }


# ============================================================================
# SELF-TEST (Run when module is executed directly)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ENRICHMENT HELPERS - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Test 1: Phone Normalization
    print("\n" + "-"*70)
    print("TEST 1: Phone Normalization")
    print("-"*70)
    test_phones = [
        '9876543210',
        '+91 9876543210',
        '+91-98765-43210',
        '98765 43210',
        '12345'
    ]
    for phone in test_phones:
        result, changed, desc = normalize_phone(phone)
        print(f"   '{phone}' → '{result}' (Changed: {changed}) {desc or ''}")
    
    # Test 2: City Fuzzy Matching
    print("\n" + "-"*70)
    print("TEST 2: City Fuzzy Matching")
    print("-"*70)
    test_cities = [
        'Bangalore',
        'Banaglore',
        'MUMBAI',
        'Bengaluru',
        'XYZ City'
    ]
    for city in test_cities:
        result, changed, desc, sim = fuzzy_match_city(city)
        print(f"   '{city}' → '{result}' (Changed: {changed}, Similarity: {sim}%) {desc or ''}")
    
    # Test 3: Specialty Normalization
    print("\n" + "-"*70)
    print("TEST 3: Specialty Normalization")
    print("-"*70)
    test_specs = [
        'Cardiology',
        'CARDIOLOGY',
        'Cardio',
        'Neuro',
        'InvalidSpec'
    ]
    for spec in test_specs:
        result, changed, desc, sim = normalize_specialty_enhanced(spec)
        print(f"   '{spec}' → '{result}' (Changed: {changed}, Similarity: {sim}%) {desc or ''}")
    
    # Test 4: Pincode-City Verification
    print("\n" + "-"*70)
    print("TEST 4: Pincode-City Verification")
    print("-"*70)
    test_pairs = [
        ('560001', 'Bangalore'),
        ('400001', 'Mumbai'),
        ('400001', 'Bangalore'),
        ('999999', 'Delhi')
    ]
    for pincode, city in test_pairs:
        is_valid, warning = verify_pincode_city(pincode, city)
        print(f"   {pincode} + {city} → Valid: {is_valid} {warning or ''}")
    
    # Test 5: Complete Record Enrichment
    print("\n" + "-"*70)
    print("TEST 5: Complete Record Enrichment")
    print("-"*70)
    test_record = {
        'name': 'Dr. Test',
        'phone': '+91-98765-43210',
        'city': 'Banaglore',
        'specialty': 'Cardio',
        'pincode': '560001'
    }
    result = enrich_record_fields(test_record)
    print(f"   Original: {test_record}")
    print(f"   Enriched: {result['enriched_record']}")
    print(f"   Score: {result['score']}/60")
    print(f"   Changes: {result['changes']}")
    
    print("\n" + "="*70)
    print("✅ ALL HELPER TESTS COMPLETE")
    print("="*70)
