# lookup_tables.py

# ============================================================================
# SPECIALTY LIST - ~50 Common Indian Medical Specialties
# ============================================================================
# Used by Agent 1 (Validation Engine) to verify specialty against approved list
# Add/remove specialties as needed for your database

SPECIALTY_LIST = [
    # Core Medical Specialties
    "Cardiology",
    "Cardiothoracic Surgery",
    "Neurology",
    "Neurosurgery",
    "Orthopedics",
    "Orthopedic Surgery",
    "General Surgery",
    "Pediatrics",
    "Pediatric Surgery",
    "Obstetrics",
    "Gynecology",
    "Obstetrics and Gynecology",
    
    # Surgical Specialties
    "Urology",
    "Vascular Surgery",
    "Plastic Surgery",
    "Trauma Surgery",
    "Colorectal Surgery",
    "Hepatobiliary Surgery",
    
    # Diagnostic & Lab Specialties
    "Pathology",
    "Radiology",
    "Interventional Radiology",
    "Nuclear Medicine",
    "Microbiology",
    
    # Medical Specialties
    "Dermatology",
    "Psychiatry",
    "Oncology",
    "Medical Oncology",
    "Radiation Oncology",
    "Hematology",
    "Gastroenterology",
    "Hepatology",
    "Pulmonology",
    "Respiratory Medicine",
    "Nephrology",
    "Rheumatology",
    "Endocrinology",
    "Metabolism",
    
    # Sensory Specialties
    "Ophthalmology",
    "Eye Surgery",
    "Otolaryngology",
    "ENT",
    "Dentistry",
    "Dental Surgery",
    
    # Other Important Specialties
    "General Practice",
    "Family Medicine",
    "Internal Medicine",
    "Anesthesiology",
    "Critical Care",
    "Intensive Care",
    "Emergency Medicine",
    "Physiotherapy",
    "Ayurveda",
    "Homeopathy",
    "Naturopathy",
    "Yoga & Wellness",
]


# ============================================================================
# CITY TYPOS - Map common misspellings to correct city names
# ============================================================================
# Used by Agent 2 (Enrichment) to standardize city names
# Format: {"misspelled": "correct_city"}

CITY_TYPOS = {
    # Bangalore variations
    "Banaglore": "Bangalore",
    "Bengalure": "Bangalore",
    "Bangalor": "Bangalore",
    "Bengalore": "Bangalore",
    "Banglore": "Bangalore",
    
    # Mumbai variations
    "Mumbay": "Mumbai",
    "Bombay": "Mumbai",
    "Mumabi": "Mumbai",
    "Bombai": "Mumbai",
    "Mubai": "Mumbai",
    
    # Delhi variations
    "Delhii": "Delhi",
    "Dehli": "Delhi",
    "New Delhi": "Delhi",
    "Delih": "Delhi",
    
    # Pune variations
    "Punee": "Pune",
    "Poona": "Pune",
    "Puna": "Pune",
    
    # Hyderabad variations
    "Hydrabad": "Hyderabad",
    "Hyabad": "Hyderabad",
    "Hydrebad": "Hyderabad",
    "Secunderabad": "Hyderabad",
    
    # Chennai variations
    "Chenai": "Chennai",
    "Madras": "Chennai",
    "Chenna": "Chennai",
    
    # Kolkata variations
    "Calcutta": "Kolkata",
    "Kolkota": "Kolkata",
    "Kolkatta": "Kolkata",
    
    # Ahmedabad variations
    "Ahmednagar": "Ahmedabad",
    "Ahmd": "Ahmedabad",
    "Ahemedabad": "Ahmedabad",
    
    # Jaipur variations
    "Jaipur": "Jaipur",  # Already correct
    "Jaupur": "Jaipur",
    
    # Lucknow variations
    "Lucknow": "Lucknow",  # Already correct
    "Lakhnau": "Lucknow",
}

# ============================================================================
# PINCODE_TO_CITY - Map Indian postal codes to city names
# ============================================================================
# Used by Agent 2 (Enrichment) to fill missing city data from postal code
# Format: {"pincode": "city_name"}
# Note: Real data should use full pincode database; this is a sample

PINCODE_TO_CITY = {
    # Bangalore (560xxx)
    "560001": "Bangalore",
    "560002": "Bangalore",
    "560003": "Bangalore",
    "560004": "Bangalore",
    "560005": "Bangalore",
    "560010": "Bangalore",
    "560020": "Bangalore",
    "560034": "Bangalore",
    "560038": "Bangalore",
    "560066": "Bangalore",
    "560070": "Bangalore",
    "560075": "Bangalore",
    "560085": "Bangalore",
    "560095": "Bangalore",
    
    # Mumbai (400xxx, 401xxx)
    "400001": "Mumbai",
    "400004": "Mumbai",
    "400010": "Mumbai",
    "400013": "Mumbai",
    "400020": "Mumbai",
    "400025": "Mumbai",
    "400050": "Mumbai",
    "400070": "Mumbai",
    "400080": "Mumbai",
    "401201": "Mumbai",
    
    # Delhi (110xxx, 101xxx)
    "110001": "Delhi",
    "110002": "Delhi",
    "110003": "Delhi",
    "110006": "Delhi",
    "110007": "Delhi",
    "110008": "Delhi",
    "110011": "Delhi",
    "110014": "Delhi",
    "110016": "Delhi",
    "110020": "Delhi",
    "101201": "Delhi",
    
    # Pune (411xxx, 412xxx)
    "411001": "Pune",
    "411002": "Pune",
    "411004": "Pune",
    "411005": "Pune",
    "411006": "Pune",
    "411007": "Pune",
    "411009": "Pune",
    "411028": "Pune",
    "411038": "Pune",
    "412101": "Pune",
    
    # Hyderabad (500xxx, 501xxx)
    "500001": "Hyderabad",
    "500002": "Hyderabad",
    "500003": "Hyderabad",
    "500004": "Hyderabad",
    "500005": "Hyderabad",
    "500006": "Hyderabad",
    "500009": "Hyderabad",
    "500010": "Hyderabad",
    "500016": "Hyderabad",
    "500082": "Hyderabad",
    
    # Chennai (600xxx, 601xxx)
    "600001": "Chennai",
    "600002": "Chennai",
    "600004": "Chennai",
    "600006": "Chennai",
    "600010": "Chennai",
    "600014": "Chennai",
    "600018": "Chennai",
    "600020": "Chennai",
    "600028": "Chennai",
    "600052": "Chennai",
    
    # Kolkata (700xxx, 701xxx, 702xxx)
    "700001": "Kolkata",
    "700006": "Kolkata",
    "700009": "Kolkata",
    "700012": "Kolkata",
    "700017": "Kolkata",
    "700019": "Kolkata",
    "700020": "Kolkata",
    "700022": "Kolkata",
    "700026": "Kolkata",
    "701201": "Kolkata",
    
    # Ahmedabad (380xxx, 382xxx)
    "380001": "Ahmedabad",
    "380004": "Ahmedabad",
    "380005": "Ahmedabad",
    "380006": "Ahmedabad",
    "380009": "Ahmedabad",
    "380014": "Ahmedabad",
    "380015": "Ahmedabad",
    "380016": "Ahmedabad",
    "380022": "Ahmedabad",
    "382201": "Ahmedabad",
}


# ============================================================================
# PHONE VALIDATION - Indian phone number formats
# ============================================================================

def is_valid_indian_phone(phone):
    """
    Validate Indian phone numbers.
    
    Accepts:
    - 10-digit: "9876543210"
    - +91 prefix: "+919876543210"
    - With spaces/hyphens: "98 7654 3210" or "98-7654-3210"
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        bool: True if valid format, False otherwise
    """
    import re
    
    if not phone:
        return False
    
    # Remove spaces, hyphens, parentheses
    cleaned = str(phone).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Pattern 1: +91 followed by 10 digits
    if re.match(r'^\+91\d{10}$', cleaned):
        return True
    
    # Pattern 2: Exactly 10 digits (Indian mobile)
    if re.match(r'^\d{10}$', cleaned):
        return True
    
    # Pattern 3: 0 followed by 10 digits (landline format)
    if re.match(r'^0\d{10}$', cleaned):
        return True
    
    return False


# Test the function

# ============================================================================
# PINCODE VALIDATION - Indian postal codes
# ============================================================================

def is_valid_pincode(pincode):
    """
    Validate Indian postal codes (pincodes).
    
    Rules:
    - Must be exactly 6 digits
    - First digit: 1-9 (no leading 0)
    - Remaining digits: 0-9
    
    Args:
        pincode (str or int): Pincode to validate
    
    Returns:
        bool: True if valid format, False otherwise
    """
    import re
    
    if not pincode:
        return False
    
    # Convert to string and remove spaces
    pincode_str = str(pincode).strip().replace(" ", "")
    
    # Pattern: Exactly 6 digits, first digit 1-9
    if re.match(r'^[1-9]\d{5}$', pincode_str):
        return True
    
    return False


# Test the function

# ============================================================================
# REGISTRATION NUMBER VALIDATION - Medical registration patterns
# ============================================================================

def matches_reg_pattern(registration_no):
    """
    Validate medical registration number format.
    
    Common patterns in India:
    - NMC (National Medical Commission): MCI followed by digits
    - State Medical Councils: State code + digits
    - Pattern: Alphanumeric, 8-15 characters
    
    Examples:
    - "MCI10012345" ✓
    - "TN0001234" ✓
    - "INVALID_REG" ✗ (doesn't follow pattern)
    
    Args:
        registration_no (str): Registration number to validate
    
    Returns:
        bool: True if matches expected pattern, False otherwise
    """
    import re
    
    if not registration_no:
        return False
    
    reg_str = str(registration_no).strip().upper()
    
    # Pattern: 2-4 letter prefix (state/council code) + 5-11 digits
    # Examples: MCI10012345, TN0001234, KA123456
    if re.match(r'^[A-Z]{2,4}\d{5,11}$', reg_str):
        return True
    
    return False





# ============================================================================
# REQUIRED FIELDS VALIDATION
# ============================================================================

REQUIRED_FIELDS = ["id", "name", "phone", "city", "specialty", "registration_no", "years_practice", "clinic_address", "pincode"]

def all_required_fields_present(record):
    """
    Check if all required fields are present and non-empty in a record.
    
    Args:
        record (dict): A single record/row from the CSV
    
    Returns:
        bool: True if all required fields are present and non-empty
    """
    for field in REQUIRED_FIELDS:
        if field not in record:
            return False
        if record[field] is None or str(record[field]).strip() == "":
            return False
    
    return True


# Test the function
if __name__ == "__main__":
    test_records = [
        {"id": 1, "name": "Dr. X", "phone": "9876543210", "city": "Bangalore", "specialty": "Cardiology", "registration_no": "MCI123", "years_practice": 5, "clinic_address": "123 Road", "pincode": "560001"},  # Valid
        {"id": 2, "name": "Dr. Y", "phone": "", "city": "Mumbai", "specialty": "Dermatology", "registration_no": "MCI124", "years_practice": 3, "clinic_address": "456 Ave", "pincode": "400001"},  # Missing phone
        {"id": 3, "name": "Dr. Z", "city": "Delhi"},  # Missing many fields
    ]
    
    for i, rec in enumerate(test_records):
        result = all_required_fields_present(rec)
        print(f"  Record {i+1}: {result}")

    test_phones = [
        "9876543210",      # Valid: 10-digit
        "+919876543210",   # Valid: +91 format
        "98 7654 3210",    # Valid: with spaces
        "98-7654-3210",    # Valid: with hyphens
        "09876543210",     # Valid: with leading 0
        "98765",           # Invalid: too short
        "abc1234567890",   # Invalid: letters
        "",                # Invalid: empty
    ]
    
    for phone in test_phones:
        result = is_valid_indian_phone(phone)
        print(f"  {phone:20} -> {result}")


    test_pincodes = [
        "560001",      # Valid: standard format
        "400020",      # Valid: standard format
        "110001",      # Valid: standard format
        "56001",       # Invalid: only 5 digits
        "5600001",     # Invalid: 7 digits
        "060001",      # Invalid: starts with 0
        "abcdef",      # Invalid: letters
        "",            # Invalid: empty
    ]
    
    for pincode in test_pincodes:
        result = is_valid_pincode(pincode)
        print(f"  {pincode:20} -> {result}")


    test_regs = [
        "MCI10012345",      # Valid: NMC format
        "TN0001234",        # Valid: State council format
        "KA123456",         # Valid: Karnataka format
        "AP1234567890",     # Valid: Andhra Pradesh format
        "INVALID_REG",      # Invalid: doesn't match pattern
        "MCI1001",          # Invalid: too few digits
        "123456789",        # Invalid: no letter prefix
        "",                 # Invalid: empty
    ]
    
    for reg in test_regs:
        result = matches_reg_pattern(reg)
        print(f"  {reg:20} -> {result}")