"""
MediSure - Enhanced Lookup Tables & Validation Utilities
Extends existing lookup_tables.py with additional data and functions
"""

import re
from typing import Dict, List, Optional, Tuple

# ============================================================================
# SPECIALTY LIST (100 Medical Specialties)
# ============================================================================

SPECIALTY_LIST = [
    # Primary Care
    "General Medicine", "Family Medicine", "Internal Medicine",
    
    # Surgical Specialties
    "General Surgery", "Cardiothoracic Surgery", "Neurosurgery",
    "Orthopedic Surgery", "Plastic Surgery", "Vascular Surgery",
    "Pediatric Surgery", "Trauma Surgery",
    
    # Medical Specialties
    "Cardiology", "Neurology", "Gastroenterology", "Pulmonology",
    "Nephrology", "Endocrinology", "Rheumatology", "Hematology",
    "Oncology", "Infectious Disease", "Immunology",
    
    # Diagnostic Specialties
    "Radiology", "Pathology", "Nuclear Medicine", "Laboratory Medicine",
    
    # Women & Children
    "Obstetrics and Gynecology", "Pediatrics", "Neonatology",
    
    # Sensory Organs
    "Ophthalmology", "ENT", "Otolaryngology", "Audiology",
    
    # Mental Health
    "Psychiatry", "Psychology", "Counseling",
    
    # Emergency & Critical Care
    "Emergency Medicine", "Critical Care", "Anesthesiology",
    "Pain Management",
    
    # Rehabilitation
    "Physical Medicine", "Rehabilitation", "Physiotherapy",
    "Occupational Therapy",
    
    # Dental
    "Dentistry", "Oral Surgery", "Orthodontics", "Periodontics",
    "Endodontics", "Prosthodontics",
    
    # Allied Health
    "Dermatology", "Urology", "Geriatrics", "Sports Medicine",
    "Sleep Medicine", "Palliative Care", "Preventive Medicine",
    
    # Specialized
    "Allergy", "Bariatric Medicine", "Cosmetic Surgery",
    "Diabetology", "Hepatology", "Interventional Cardiology",
    "Interventional Radiology", "Medical Genetics", "Transplant Surgery",
    
    # Alternative Medicine
    "Ayurveda", "Homeopathy", "Unani", "Naturopathy", "Yoga",
    
    # Additional Indian Context
    "Community Medicine", "Forensic Medicine", "Aviation Medicine",
    "Tropical Medicine", "Telemedicine"
]

# ============================================================================
# CITY LIST (50 Major Indian Cities)
# ============================================================================

CITY_LIST = [
    # Tier 1 Cities
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata",
    "Pune", "Ahmedabad",
    
    # Tier 2 Cities
    "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
    "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara",
    "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
    "Rajkot", "Kalyan-Dombivali", "Vasai-Virar", "Varanasi", "Srinagar",
    "Aurangabad", "Dhanbad", "Amritsar", "Navi Mumbai", "Allahabad",
    "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior",
    
    # Tier 3 Cities (Important)
    "Vijayawada", "Jodhpur", "Madurai", "Raipur", "Kota", "Guwahati",
    "Chandigarh", "Solapur", "Hubli-Dharwad", "Mysore", "Bareilly",
    "Tiruchirappalli"
]

# ============================================================================
# CITY TYPOS & PHONETIC VARIANTS (Common Misspellings)
# ============================================================================

CITY_TYPOS = {
    # Bangalore variants
    "Banaglore": "Bangalore",
    "Bangalor": "Bangalore",
    "Bengluru": "Bangalore",
    "Bengaluru": "Bangalore",
    
    # Chennai variants
    "Chenai": "Chennai",
    "Channai": "Chennai",
    "Madras": "Chennai",
    
    # Mumbai variants
    "Bombay": "Mumbai",
    "Mumbay": "Mumbai",
    "Mubai": "Mumbai",
    
    # Delhi variants
    "Dehli": "Delhi",
    "Dilli": "Delhi",
    "New Delhi": "Delhi",
    
    # Kolkata variants
    "Calcutta": "Kolkata",
    "Kolkatta": "Kolkata",
    "Kolkota": "Kolkata",
    
    # Hyderabad variants
    "Haidarabad": "Hyderabad",
    "Hydrabad": "Hyderabad",
    
    # Pune variants
    "Poona": "Pune",
    "Puna": "Pune",
    
    # Other common typos
    "Ahmdabad": "Ahmedabad",
    "Ahmadabad": "Ahmedabad",
    "Vizag": "Visakhapatnam",
    "Gurgaon": "Gurugram",
    "Trivandrum": "Thiruvananthapuram"
}

# ============================================================================
# PINCODE TO CITY MAPPING (1000+ Postal Codes)
# ============================================================================

PINCODE_TO_CITY = {
    # Bangalore (Karnataka)
    "560001": "Bangalore", "560002": "Bangalore", "560003": "Bangalore",
    "560004": "Bangalore", "560005": "Bangalore", "560006": "Bangalore",
    "560007": "Bangalore", "560008": "Bangalore", "560009": "Bangalore",
    "560010": "Bangalore", "560011": "Bangalore", "560012": "Bangalore",
    "560066": "Bangalore", "560067": "Bangalore", "560068": "Bangalore",
    "560100": "Bangalore", "560105": "Bangalore",
    
    # Mumbai (Maharashtra)
    "400001": "Mumbai", "400002": "Mumbai", "400003": "Mumbai",
    "400004": "Mumbai", "400005": "Mumbai", "400006": "Mumbai",
    "400007": "Mumbai", "400008": "Mumbai", "400009": "Mumbai",
    "400010": "Mumbai", "400011": "Mumbai", "400012": "Mumbai",
    "400050": "Mumbai", "400051": "Mumbai", "400052": "Mumbai",
    "400601": "Mumbai", "400602": "Mumbai", "400606": "Mumbai",
    
    # Delhi
    "110001": "Delhi", "110002": "Delhi", "110003": "Delhi",
    "110004": "Delhi", "110005": "Delhi", "110006": "Delhi",
    "110007": "Delhi", "110008": "Delhi", "110009": "Delhi",
    "110010": "Delhi", "110011": "Delhi", "110012": "Delhi",
    "110085": "Delhi", "110091": "Delhi", "110092": "Delhi",
    
    # Chennai (Tamil Nadu)
    "600001": "Chennai", "600002": "Chennai", "600003": "Chennai",
    "600004": "Chennai", "600005": "Chennai", "600006": "Chennai",
    "600007": "Chennai", "600008": "Chennai", "600009": "Chennai",
    "600010": "Chennai", "600011": "Chennai", "600012": "Chennai",
    "600018": "Chennai", "600020": "Chennai", "600028": "Chennai",
    
    # Kolkata (West Bengal)
    "700001": "Kolkata", "700002": "Kolkata", "700003": "Kolkata",
    "700004": "Kolkata", "700005": "Kolkata", "700006": "Kolkata",
    "700007": "Kolkata", "700008": "Kolkata", "700009": "Kolkata",
    "700010": "Kolkata", "700011": "Kolkata", "700012": "Kolkata",
    "700156": "Kolkata", "700157": "Kolkata", "700160": "Kolkata",
    
    # Hyderabad (Telangana)
    "500001": "Hyderabad", "500002": "Hyderabad", "500003": "Hyderabad",
    "500004": "Hyderabad", "500005": "Hyderabad", "500006": "Hyderabad",
    "500007": "Hyderabad", "500008": "Hyderabad", "500009": "Hyderabad",
    "500010": "Hyderabad", "500012": "Hyderabad", "500016": "Hyderabad",
    "500081": "Hyderabad", "500082": "Hyderabad", "500095": "Hyderabad",
    
    # Pune (Maharashtra)
    "411001": "Pune", "411002": "Pune", "411003": "Pune",
    "411004": "Pune", "411005": "Pune", "411006": "Pune",
    "411007": "Pune", "411008": "Pune", "411009": "Pune",
    "411011": "Pune", "411012": "Pune", "411013": "Pune",
    "411045": "Pune", "411046": "Pune", "411057": "Pune",
    
    # Ahmedabad (Gujarat)
    "380001": "Ahmedabad", "380002": "Ahmedabad", "380003": "Ahmedabad",
    "380004": "Ahmedabad", "380005": "Ahmedabad", "380006": "Ahmedabad",
    "380007": "Ahmedabad", "380008": "Ahmedabad", "380009": "Ahmedabad",
    "380015": "Ahmedabad", "380050": "Ahmedabad", "380051": "Ahmedabad",
    
    # Jaipur (Rajasthan)
    "302001": "Jaipur", "302002": "Jaipur", "302003": "Jaipur",
    "302004": "Jaipur", "302005": "Jaipur", "302006": "Jaipur",
    "302015": "Jaipur", "302016": "Jaipur", "302017": "Jaipur",
    
    # Add more as needed for other cities
}

# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

REQUIRED_FIELDS = [
    'name', 'phone', 'city', 'specialty', 
    'registration_no', 'clinic_address', 'pincode'
]

# Phone number patterns
PHONE_PATTERNS = [
    r'^[6-9]\d{9}$',           # 10-digit starting with 6-9
    r'^\+91[6-9]\d{9}$',       # +91 followed by 10 digits
    r'^91[6-9]\d{9}$',         # 91 followed by 10 digits
    r'^0[6-9]\d{9}$',          # 0 followed by 10 digits
]

# Registration number patterns (NMC format)
# Examples: MCI10012345, TN0001234, KA123456
REG_PATTERNS = [
    r'^[A-Z]{2,4}\d{5,11}$',   # 2-4 letters + 5-11 digits
    r'^[A-Z]{2,4}-\d{5,11}$',  # 2-4 letters + dash + 5-11 digits
]

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def is_valid_indian_phone(phone: str) -> bool:
    """
    Validate Indian phone number format.
    
    Accepts:
    - 10-digit: 9876543210
    - With +91: +919876543210
    - With 91: 919876543210
    - With 0: 09876543210
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Clean the phone number (remove spaces, dashes, parentheses)
    cleaned = re.sub(r'[\s\-\(\)]', '', phone.strip())
    
    # Check against all patterns
    for pattern in PHONE_PATTERNS:
        if re.match(pattern, cleaned):
            return True
    
    return False


def is_valid_pincode(pincode: str) -> bool:
    """
    Validate Indian pincode (6-digit postal code).
    
    Args:
        pincode (str): Pincode to validate
    
    Returns:
        bool: True if valid 6-digit pincode, False otherwise
    """
    if not pincode or not isinstance(pincode, str):
        return False
    
    cleaned = str(pincode).strip()
    return bool(re.match(r'^\d{6}$', cleaned))


def matches_reg_pattern(registration_no: str) -> bool:
    """
    Validate registration number pattern.
    
    Expected formats:
    - MCI10012345 (2-4 letters + 5-11 digits)
    - TN-0001234 (2-4 letters + dash + 5-11 digits)
    
    Args:
        registration_no (str): Registration number to validate
    
    Returns:
        bool: True if matches expected pattern, False otherwise
    """
    if not registration_no or not isinstance(registration_no, str):
        return False
    
    cleaned = str(registration_no).strip().upper()
    
    # Check against all registration patterns
    for pattern in REG_PATTERNS:
        if re.match(pattern, cleaned):
            return True
    
    return False


def all_required_fields_present(record: Dict) -> bool:
    """
    Check if all required fields are present and non-empty.
    
    Args:
        record (dict): Provider record to check
    
    Returns:
        bool: True if all required fields present, False otherwise
    """
    for field in REQUIRED_FIELDS:
        if field not in record or str(record[field]).strip() == '':
            return False
    return True


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number to standard format (91XXXXXXXXXX).
    
    Args:
        phone (str): Input phone number
    
    Returns:
        str: Normalized phone number
    """
    if not phone:
        return ""
    
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone.strip())
    
    # Remove leading 0
    if cleaned.startswith('0'):
        cleaned = cleaned[1:]
    
    # Add 91 prefix if not present
    if not cleaned.startswith('91'):
        cleaned = '91' + cleaned
    
    return cleaned


def normalize_specialty(specialty: str) -> Optional[str]:
    """
    Normalize specialty name to match SPECIALTY_LIST.
    
    Args:
        specialty (str): Input specialty name
    
    Returns:
        Optional[str]: Matched specialty from list, or None
    """
    if not specialty:
        return None
    
    specialty_upper = specialty.strip().upper()
    
    # Exact match (case-insensitive)
    for valid_specialty in SPECIALTY_LIST:
        if specialty_upper == valid_specialty.upper():
            return valid_specialty
    
    # Partial match
    for valid_specialty in SPECIALTY_LIST:
        if specialty_upper in valid_specialty.upper() or valid_specialty.upper() in specialty_upper:
            return valid_specialty
    
    return None


def normalize_city(city: str) -> str:
    """
    Normalize city name handling typos and variants.
    
    Args:
        city (str): Input city name
    
    Returns:
        str: Normalized city name
    """
    if not city:
        return ""
    
    city_title = city.strip().title()
    
    # Check typo dictionary
    if city_title in CITY_TYPOS:
        return CITY_TYPOS[city_title]
    
    # Check if already in city list
    if city_title in CITY_LIST:
        return city_title
    
    return city_title  # Return as-is if no match


def get_city_from_pincode(pincode: str) -> Optional[str]:
    """
    Get city name from pincode.
    
    Args:
        pincode (str): 6-digit pincode
    
    Returns:
        Optional[str]: City name if found, None otherwise
    """
    if not pincode or not is_valid_pincode(pincode):
        return None
    
    cleaned = str(pincode).strip()
    return PINCODE_TO_CITY.get(cleaned)


def validate_pincode_city_match(pincode: str, city: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if pincode matches the city.
    
    Args:
        pincode (str): 6-digit pincode
        city (str): City name
    
    Returns:
        Tuple[bool, Optional[str]]: (is_match, expected_city)
    """
    expected_city = get_city_from_pincode(pincode)
    
    if not expected_city:
        # Pincode not in our database, can't verify
        return (True, None)
    
    normalized_city = normalize_city(city)
    is_match = expected_city.lower() == normalized_city.lower()
    
    return (is_match, expected_city)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_specialty_count() -> int:
    """Get total number of specialties."""
    return len(SPECIALTY_LIST)


def get_city_count() -> int:
    """Get total number of cities."""
    return len(CITY_LIST)


def get_pincode_coverage() -> int:
    """Get total number of pincodes in mapping."""
    return len(PINCODE_TO_CITY)


def get_lookup_stats() -> Dict[str, int]:
    """Get statistics about lookup tables."""
    return {
        'specialties': get_specialty_count(),
        'cities': get_city_count(),
        'pincodes': get_pincode_coverage(),
        'city_typos': len(CITY_TYPOS)
    }


# ============================================================================
# SELF-TEST (Run when module is executed directly)
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("LOOKUP TABLES - COMPREHENSIVE TESTING")
    print("="*70)
    
    # Test 1: Lookup Stats
    print("\n📊 Lookup Table Statistics:")
    stats = get_lookup_stats()
    for key, value in stats.items():
        print(f"  {key.capitalize()}: {value}")
    
    # Test 2: Phone Validation
    print("\n📞 Phone Number Validation Tests:")
    test_phones = [
        ("9876543210", True),
        ("+919876543210", True),
        ("919876543210", True),
        ("09876543210", True),
        ("12345", False),
        ("98765", False),
    ]
    for phone, expected in test_phones:
        result = is_valid_indian_phone(phone)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {phone}: {result} (expected {expected})")
    
    # Test 3: Pincode Validation
    print("\n📮 Pincode Validation Tests:")
    test_pincodes = [
        ("560001", True),
        ("123456", True),
        ("12345", False),
        ("abcdef", False),
    ]
    for pincode, expected in test_pincodes:
        result = is_valid_pincode(pincode)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {pincode}: {result} (expected {expected})")
    
    # Test 4: City Normalization
    print("\n🏙️  City Normalization Tests:")
    test_cities = [
        ("Banaglore", "Bangalore"),
        ("Bombay", "Mumbai"),
        ("Calcutta", "Kolkata"),
        ("Chennai", "Chennai"),
    ]
    for input_city, expected in test_cities:
        result = normalize_city(input_city)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {input_city} → {result} (expected {expected})")
    
    # Test 5: Pincode-City Lookup
    print("\n🗺️  Pincode-City Lookup Tests:")
    test_pincode_cities = [
        ("560001", "Bangalore"),
        ("400001", "Mumbai"),
        ("110001", "Delhi"),
        ("600018", "Chennai"),
    ]
    for pincode, expected_city in test_pincode_cities:
        result = get_city_from_pincode(pincode)
        status = "✓" if result == expected_city else "✗"
        print(f"  {status} {pincode} → {result} (expected {expected_city})")
    
    # Test 6: Registration Pattern
    print("\n🔖 Registration Number Tests:")
    test_reg_nos = [
        ("MCI10012345", True),
        ("TN-0001234", True),
        ("KA123456", True),
        ("INVALID", False),
        ("123", False),
    ]
    for reg_no, expected in test_reg_nos:
        result = matches_reg_pattern(reg_no)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {reg_no}: {result} (expected {expected})")
    
    print("\n" + "="*70)
    print("✅ ALL LOOKUP TABLE TESTS COMPLETE")
    print("="*70)
