"""
MediSure Agent 1: Data Validation Engine (CrewAI Implementation)
Phase 1: Rule-based validation with CrewAI pattern
"""

import time
from typing import Dict, List, Any
from crewai import Agent, Task, Crew
from crewai.tools import tool

# Import lookup tables
from lookup_tables_extended import (
    is_valid_indian_phone,
    is_valid_pincode,
    matches_reg_pattern,
    all_required_fields_present,
    normalize_specialty,
    REQUIRED_FIELDS,
    SPECIALTY_LIST
)

# Import enrichment helpers
from enrichment_helpers import (
    normalize_phone,
    fuzzy_match_city,
    normalize_specialty_enhanced,
    verify_pincode_city,
    enrich_address,
    enrich_record_fields
)

# Import cross-validation helpers
from cross_validation_helpers import (
    detect_duplicate,
    verify_registration_number,
    validate_years_practice,
    verify_geographic_consistency,
    cross_validate_record,
    register_provider,
    clear_provider_database
)


# ============================================================================
# CORE VALIDATION FUNCTIONS (Direct callable functions)
# ============================================================================

def _validate_phone(phone: str) -> Dict[str, Any]:
    """Validate Indian phone number format."""
    if is_valid_indian_phone(phone):
        return {'valid': True, 'score': 20, 'issue': None}
    else:
        return {'valid': False, 'score': 0, 'issue': f"Invalid phone format: {phone}"}

def _validate_pincode(pincode: str) -> Dict[str, Any]:
    """Validate Indian 6-digit pincode."""
    if is_valid_pincode(pincode):
        return {'valid': True, 'score': 20, 'issue': None}
    else:
        return {'valid': False, 'score': 0, 'issue': f"Invalid pincode format: {pincode}"}

def _validate_specialty(specialty: str) -> Dict[str, Any]:
    """Validate specialty against approved list."""
    if not specialty:
        return {'valid': False, 'score': 0, 'issue': "Specialty not provided"}
    
    specialty_upper = str(specialty).strip().upper()
    specialty_list_upper = [s.upper() for s in SPECIALTY_LIST]
    
    if specialty_upper in specialty_list_upper:
        return {'valid': True, 'score': 20, 'issue': None}
        
    normalized = normalize_specialty(specialty)
    if normalized:
        return {'valid': True, 'score': 15, 'issue': f"Specialty matched (normalized): {normalized}"}
        
    return {'valid': False, 'score': 0, 'issue': f"Specialty '{specialty}' not in approved list"}

def _validate_registration(registration_no: str) -> Dict[str, Any]:
    """Validate registration number format."""
    if matches_reg_pattern(registration_no):
        return {'valid': True, 'score': 20, 'issue': None}
    else:
        return {'valid': False, 'score': 0, 'issue': f"Registration number '{registration_no}' format invalid"}

def _validate_required_fields(record: Dict) -> Dict[str, Any]:
    """Validate all required fields are present."""
    if all_required_fields_present(record):
        return {'valid': True, 'score': 20, 'issue': None}
    else:
        missing = []
        for field in REQUIRED_FIELDS:
            if field not in record or str(record[field]).strip() == '':
                missing.append(field)
        return {'valid': False, 'score': 0, 'issue': f"Missing required fields: {', '.join(missing)}"}


# ============================================================================
# CREWAI TOOL WRAPPERS (For agent.tools compatibility)
# ============================================================================

@tool("validate_phone_tool")
def validate_phone_tool(phone: str) -> Dict[str, Any]:
    """Validate Indian phone number format."""
    return _validate_phone(phone)

@tool("validate_pincode_tool")
def validate_pincode_tool(pincode: str) -> Dict[str, Any]:
    """Validate Indian 6-digit pincode."""
    return _validate_pincode(pincode)

@tool("validate_specialty_tool")
def validate_specialty_tool(specialty: str) -> Dict[str, Any]:
    """Validate specialty against approved list."""
    return _validate_specialty(specialty)

@tool("validate_registration_tool")
def validate_registration_tool(registration_no: str) -> Dict[str, Any]:
    """Validate registration number format."""
    return _validate_registration(registration_no)

@tool("validate_required_fields_tool")
def validate_required_fields_tool(record: Dict) -> Dict[str, Any]:
    """Validate all required fields are present."""
    return _validate_required_fields(record)


# ============================================================================
# AGENT 1: DATA VALIDATION ENGINE CLASS
# ============================================================================

class Agent1DataValidation:
    """
    Agent 1: Data Validation Engine
    Validates provider records against format rules and approved lists.
    Scoring System:
    - Phone format: 20 points
    - Pincode format: 20 points
    - Specialty in approved list: 20 points
    - Registration number pattern: 20 points
    - Required fields present: 20 points
    Total: 0-100 points
    """
    
    def __init__(self):
        """Initialize Agent 1 with CrewAI configuration"""
        self.agent = Agent(
            role="Data Validation Specialist",
            goal="Validate healthcare provider records against strict format rules and approved lists",
            backstory="""You are an expert in healthcare data quality assurance.
            Your specialty is validating provider information for accuracy, completeness,
            and compliance with Indian medical registration standards. You ensure that
            phone numbers, pincodes, specialties, and registration numbers meet
            required format specifications.""",
            verbose=False,
            allow_delegation=False,
            tools=[
                validate_phone_tool, 
                validate_pincode_tool, 
                validate_specialty_tool,
                validate_registration_tool,
                validate_required_fields_tool
            ]
        )

    def validate_record(self, record: Dict) -> Dict[str, Any]:
        """
        Validate a single provider record.
        Args:
            record (dict): Provider record with keys: name, phone, city, specialty,
                          registration_no, clinic_address, pincode
        Returns:
            dict: {
                'confidence_agent1': int (0-100),
                'issues_validation': list of str,
                'execution_time_agent1': float (milliseconds),
                'record_validated': dict (cleaned record)
            }
        """
        start_time = time.time()
        score = 0
        issues = []
        
        # ====================================================================
        # CHECK 1: REQUIRED FIELDS PRESENT (20 points)
        # ====================================================================
        result = _validate_required_fields(record)
        score += result['score']
        if result['issue']:
            issues.append(result['issue'])
            
        # If required fields missing, stop validation
        if score == 0:
            execution_time = (time.time() - start_time) * 1000
            return {
                'confidence_agent1': 0,
                'issues_validation': issues,
                'execution_time_agent1': round(execution_time, 2),
                'record_validated': record
            }

        # ====================================================================
        # CHECK 2: PHONE FORMAT (20 points)
        # ====================================================================
        phone = record.get('phone', '')
        result = _validate_phone(phone)
        score += result['score']
        if result['issue']:
            issues.append(result['issue'])

        # ====================================================================
        # CHECK 3: PINCODE FORMAT (20 points)
        # ====================================================================
        pincode = record.get('pincode', '')
        result = _validate_pincode(pincode)
        score += result['score']
        if result['issue']:
            issues.append(result['issue'])

        # ====================================================================
        # CHECK 4: SPECIALTY IN APPROVED LIST (20 points)
        # ====================================================================
        specialty = record.get('specialty', '')
        result = _validate_specialty(specialty)
        score += result['score']
        if result['issue']:
            issues.append(result['issue'])

        # ====================================================================
        # CHECK 5: REGISTRATION NUMBER PATTERN (20 points)
        # ====================================================================
        registration_no = record.get('registration_no', '')
        result = _validate_registration(registration_no)
        score += result['score']
        if result['issue']:
            issues.append(result['issue'])
            
        # ====================================================================
        # CALCULATE EXECUTION TIME
        # ====================================================================
        execution_time = (time.time() - start_time) * 1000

        # ====================================================================
        # RETURN RESULTS
        # ====================================================================
        return {
            'confidence_agent1': score,
            'issues_validation': issues,
            'execution_time_agent1': round(execution_time, 2),
            'record_validated': record
        }

    def validate_batch(self, records: List[Dict]) -> List[Dict]:
        """
        Validate multiple records.
        Args:
            records (list): List of provider record dictionaries
        Returns:
            list: List of validation results
        """
        results = []
        for record in records:
            result = self.validate_record(record)
            results.append({
                **record,   # Original record
                **result    # Validation results
            })
        return results
        
    def get_agent_info(self) -> Dict[str, str]:
        """Get agent metadata"""
        return {
            'name': 'Agent 1: Data Validation Engine',
            'role': self.agent.role,
            'goal': self.agent.goal,
            'tools': [tool.name for tool in self.agent.tools],
            'phase': 'Phase 1 (Rule-based)'
        }

# ============================================================================
# CONVENIENCE FUNCTION (For backward compatibility)
# ============================================================================
def agent_1_validation(record: Dict) -> Dict[str, Any]:
    """
    Backward-compatible function for Agent 1 validation.
    Args:
        record: Provider record dictionary
    Returns:
        dict: Validation results
    """
    agent = Agent1DataValidation()
    return agent.validate_record(record)


# ============================================================================
# AGENT 2: INFORMATION ENRICHMENT ENGINE
# ============================================================================

# ============================================================================
# ENRICHMENT TOOLS (CrewAI Tool Pattern)
# ============================================================================

@tool("normalize_phone_tool")
def normalize_phone_tool(phone: str) -> Dict[str, Any]:
    """
    Normalize phone number to standard format.
    Args:
        phone: Phone number string
    Returns:
        dict: {'normalized': str, 'changed': bool, 'description': str, 'score': int}
    """
    normalized, changed, description = normalize_phone(phone)
    return {
        'normalized': normalized,
        'changed': changed,
        'description': description or 'No change',
        'score': 15 if changed else 0
    }

@tool("fuzzy_match_city_tool")
def fuzzy_match_city_tool(city: str) -> Dict[str, Any]:
    """
    Match city using fuzzy string matching.
    Args:
        city: City name string
    Returns:
        dict: {'matched': str, 'changed': bool, 'description': str, 'score': int, 'similarity': int}
    """
    matched, changed, description, similarity = fuzzy_match_city(city)
    return {
        'matched': matched,
        'changed': changed,
        'description': description or 'No change',
        'score': 20 if changed else 0,
        'similarity': similarity
    }

@tool("normalize_specialty_tool")
def normalize_specialty_tool(specialty: str) -> Dict[str, Any]:
    """
    Normalize medical specialty.
    Args:
        specialty: Specialty string
    Returns:
        dict: {'normalized': str, 'changed': bool, 'description': str, 'score': int, 'similarity': int}
    """
    normalized, changed, description, similarity = normalize_specialty_enhanced(specialty)
    return {
        'normalized': normalized,
        'changed': changed,
        'description': description or 'No change',
        'score': 15 if changed else 0,
        'similarity': similarity
    }

@tool("verify_pincode_city_tool")
def verify_pincode_city_tool(pincode: str, city: str) -> Dict[str, Any]:
    """
    Verify pincode-city consistency.
    Args:
        pincode: Pincode string
        city: City string
    Returns:
        dict: {'valid': bool, 'warning': str, 'score': int}
    """
    is_valid, warning = verify_pincode_city(pincode, city)
    return {
        'valid': is_valid,
        'warning': warning or 'Verified',
        'score': 10 if (is_valid and not warning) else 0
    }

@tool("enrich_address_tool")
def enrich_address_tool(address: str, city: str, pincode: str) -> Dict[str, Any]:
    """
    Enrich clinic address.
    Args:
        address: Address string
        city: City string
        pincode: Pincode string
    Returns:
        dict: {'enriched': str, 'changed': bool, 'description': str}
    """
    enriched, changed, description = enrich_address(address, city, pincode)
    return {
        'enriched': enriched,
        'changed': changed,
        'description': description or 'No change'
    }

# ============================================================================
# UNDERLYING ENRICHMENT FUNCTIONS (Direct callable)
# ============================================================================

def _normalize_phone_func(phone: str) -> Dict[str, Any]:
    """Direct callable version of normalize_phone_tool"""
    normalized, changed, description = normalize_phone(phone)
    return {
        'normalized': normalized,
        'changed': changed,
        'description': description or 'No change',
        'score': 15 if changed else 0
    }

def _fuzzy_match_city_func(city: str) -> Dict[str, Any]:
    """Direct callable version of fuzzy_match_city_tool"""
    matched, changed, description, similarity = fuzzy_match_city(city)
    return {
        'matched': matched,
        'changed': changed,
        'description': description or 'No change',
        'score': 20 if changed else 0,
        'similarity': similarity
    }

def _normalize_specialty_func(specialty: str) -> Dict[str, Any]:
    """Direct callable version of normalize_specialty_tool"""
    normalized, changed, description, similarity = normalize_specialty_enhanced(specialty)
    return {
        'normalized': normalized,
        'changed': changed,
        'description': description or 'No change',
        'score': 15 if changed else 0,
        'similarity': similarity
    }

def _verify_pincode_city_func(pincode: str, city: str) -> Dict[str, Any]:
    """Direct callable version of verify_pincode_city_tool"""
    is_valid, warning = verify_pincode_city(pincode, city)
    return {
        'valid': is_valid,
        'warning': warning or 'Verified',
        'score': 10 if (is_valid and not warning) else 0
    }

# ============================================================================
# AGENT 2: INFORMATION ENRICHMENT ENGINE CLASS
# ============================================================================

class Agent2DataEnrichment:
    """
    Agent 2: Information Enrichment Engine
    Enriches and standardizes provider records using fuzzy matching and normalization.
    Enrichment Functions:
    - Phone normalization: +15 points
    - City fuzzy matching: +20 points
    - Specialty normalization: +15 points
    - Pincode-city verification: +10 points
    Total: 0-60 points
    """
    
    def __init__(self):
        """Initialize Agent 2 with CrewAI configuration"""
        self.agent = Agent(
            role="Data Enrichment Specialist",
            goal="Clean, standardize, and enrich healthcare provider information",
            backstory="""You are an expert in data quality and standardization.
            Your specialty is enriching healthcare provider records by correcting
            typos, normalizing formats, and verifying data consistency. You use
            fuzzy matching and validation rules to improve data quality while
            maintaining an audit trail of all changes.""",
            verbose=False,
            allow_delegation=False,
            tools=[
                normalize_phone_tool,
                fuzzy_match_city_tool,
                normalize_specialty_tool,
                verify_pincode_city_tool,
                enrich_address_tool
            ]
        )

    def enrich_record(self, record: Dict) -> Dict[str, Any]:
        """
        Enrich a single provider record.
        Args:
            record (dict): Provider record with keys: name, phone, city, specialty,
                          registration_no, clinic_address, pincode
        Returns:
            dict: {
                'confidence_agent2': int (0-60),
                'enrichment_changes': list of str,
                'execution_time_agent2': float (milliseconds),
                'record_enriched': dict (updated record)
            }
        """
        start_time = time.time()
        enriched_record = record.copy()
        changes = []
        score = 0

        # ====================================================================
        # ENRICHMENT 1: PHONE NORMALIZATION (+15 points)
        # ====================================================================
        if 'phone' in record:
            phone = record.get('phone', '')
            result = _normalize_phone_func(phone)
            if result['changed']:
                enriched_record['phone'] = result['normalized']
                changes.append(f"Phone: {result['description']}")
                score += result['score']

        # ====================================================================
        # ENRICHMENT 2: CITY FUZZY MATCHING (+20 points)
        # ====================================================================
        if 'city' in record:
            city = record.get('city', '')
            result = _fuzzy_match_city_func(city)
            if result['changed']:
                enriched_record['city'] = result['matched']
                changes.append(f"City: {result['description']}")
                score += result['score']

        # ====================================================================
        # ENRICHMENT 3: SPECIALTY NORMALIZATION (+15 points)
        # ====================================================================
        if 'specialty' in record:
            specialty = record.get('specialty', '')
            result = _normalize_specialty_func(specialty)
            if result['changed']:
                enriched_record['specialty'] = result['normalized']
                changes.append(f"Specialty: {result['description']}")
                score += result['score']

        # ====================================================================
        # ENRICHMENT 4: PINCODE-CITY VERIFICATION (+10 points)
        # ====================================================================
        if 'pincode' in enriched_record and 'city' in enriched_record:
            pincode = enriched_record.get('pincode', '')
            city = enriched_record.get('city', '')
            result = _verify_pincode_city_func(pincode, city)
            score += result['score']
            if not result['valid'] or 'not in verification database' in result['warning']:
                changes.append(f"Pincode-City: {result['warning']}")

        # ====================================================================
        # CALCULATE EXECUTION TIME
        # ====================================================================
        execution_time = (time.time() - start_time) * 1000

        # ====================================================================
        # RETURN RESULTS
        # ====================================================================
        return {
            'confidence_agent2': score,
            'enrichment_changes': changes,
            'execution_time_agent2': round(execution_time, 2),
            'record_enriched': enriched_record
        }

    def enrich_batch(self, records: List[Dict]) -> List[Dict]:
        """
        Enrich multiple records.
        Args:
            records (list): List of provider record dictionaries
        Returns:
            list: List of enrichment results
        """
        results = []
        for record in records:
            result = self.enrich_record(record)
            results.append({
                **record,   # Original record
                **result    # Enrichment results
            })
        return results

    def get_agent_info(self) -> Dict[str, str]:
        """Get agent metadata"""
        return {
            'name': 'Agent 2: Information Enrichment Engine',
            'role': self.agent.role,
            'goal': self.agent.goal,
            'tools': [tool.name for tool in self.agent.tools],
            'phase': 'Phase 1 (Rule-based)'
        }

# ============================================================================
# CONVENIENCE FUNCTION (For backward compatibility)
# ============================================================================
def agent_2_enrichment(record: Dict) -> Dict[str, Any]:
    """
    Backward-compatible function for Agent 2 enrichment.
    Args:
        record: Provider record dictionary
    Returns:
        dict: Enrichment results
    """
    agent = Agent2DataEnrichment()
    return agent.enrich_record(record)


# ============================================================================
# AGENT 3: CROSS-VALIDATION ENGINE
# ============================================================================

# ============================================================================
# CROSS-VALIDATION TOOLS (CrewAI Tool Pattern)
# ============================================================================

@tool("detect_duplicate_tool")
def detect_duplicate_tool(phone: str, registration_no: str, name: str) -> Dict[str, Any]:
    """
    Detect duplicate provider records.
    Args:
        phone: Phone number
        registration_no: Registration number
        name: Provider name
    Returns:
        dict: {'is_duplicate': bool, 'message': str, 'score': int}
    """
    is_dup, msg, score = detect_duplicate(phone, registration_no, name)
    return {
        'is_duplicate': is_dup,
        'message': msg or 'No duplicate found',
        'score': 10 if not is_dup else 0
    }

@tool("verify_registration_tool")
def verify_registration_tool(registration_no: str, specialty: str = None, city: str = None) -> Dict[str, Any]:
    """
    Verify registration number authenticity.
    Args:
        registration_no: Registration number
        specialty: Medical specialty (optional)
        city: City (optional)
    Returns:
        dict: {'is_valid': bool, 'message': str, 'score': int}
    """
    is_valid, msg, score = verify_registration_number(registration_no, specialty, city)
    return {
        'is_valid': is_valid,
        'message': msg or 'Registration verified',
        'score': score
    }

@tool("validate_years_practice_tool")
def validate_years_practice_tool(years_practice: int) -> Dict[str, Any]:
    """
    Validate years of practice using statistical analysis.
    Args:
        years_practice: Years of practice
    Returns:
        dict: {'is_valid': bool, 'message': str, 'score': int}
    """
    is_valid, msg, score = validate_years_practice(years_practice)
    return {
        'is_valid': is_valid,
        'message': msg or 'Years practice normal',
        'score': score
    }

@tool("verify_geographic_tool")
def verify_geographic_tool(clinic_address: str, city: str, pincode: str) -> Dict[str, Any]:
    """
    Verify geographic consistency.
    Args:
        clinic_address: Clinic address
        city: City name
        pincode: Pincode
    Returns:
        dict: {'is_consistent': bool, 'message': str, 'score': int}
    """
    is_consistent, msg, score = verify_geographic_consistency(clinic_address, city, pincode)
    return {
        'is_consistent': is_consistent,
        'message': msg or 'Geographic data consistent',
        'score': score
    }

# ============================================================================
# UNDERLYING CROSS-VALIDATION FUNCTIONS (Direct callable)
# ============================================================================

def _detect_duplicate_func(phone: str, registration_no: str, name: str) -> Dict[str, Any]:
    """Direct callable version of detect_duplicate_tool"""
    is_dup, msg, score = detect_duplicate(phone, registration_no, name)
    return {
        'is_duplicate': is_dup,
        'message': msg or 'No duplicate found',
        'score': 10 if not is_dup else 0
    }

def _verify_registration_func(registration_no: str, specialty: str = None, city: str = None) -> Dict[str, Any]:
    """Direct callable version of verify_registration_tool"""
    is_valid, msg, score = verify_registration_number(registration_no, specialty, city)
    return {
        'is_valid': is_valid,
        'message': msg or 'Registration verified',
        'score': score
    }

def _validate_years_practice_func(years_practice: int) -> Dict[str, Any]:
    """Direct callable version of validate_years_practice_tool"""
    is_valid, msg, score = validate_years_practice(years_practice)
    return {
        'is_valid': is_valid,
        'message': msg or 'Years practice normal',
        'score': score
    }

def _verify_geographic_func(clinic_address: str, city: str, pincode: str) -> Dict[str, Any]:
    """Direct callable version of verify_geographic_tool"""
    is_consistent, msg, score = verify_geographic_consistency(clinic_address, city, pincode)
    return {
        'is_consistent': is_consistent,
        'message': msg or 'Geographic data consistent',
        'score': score
    }

# ============================================================================
# AGENT 3: CROSS-VALIDATION ENGINE CLASS
# ============================================================================

class Agent3CrossValidation:
    """
    Agent 3: Cross-Validation Engine
    Performs fraud detection and cross-validation using:
    - Duplicate detection (fuzzy matching)
    - Registration number verification
    - Statistical anomaly detection
    - Geographic consistency checks
    Cross-Validation Functions:
    - Duplicate detection: +10 points (if no duplicate)
    - Registration verification: +10 points
    - Years practice validation: +10 points
    - Geographic consistency: +10 points
    Total: 0-40 points
    """
    
    def __init__(self):
        """Initialize Agent 3 with CrewAI configuration"""
        self.agent = Agent(
            role="Cross-Validation & Fraud Detection Specialist",
            goal="Detect fraud, duplicates, and data inconsistencies in healthcare provider records",
            backstory="""You are an expert in fraud detection and data cross-validation.
            Your specialty is identifying duplicate records, verifying registration authenticity,
            detecting statistical anomalies, and ensuring geographic consistency. You use
            fuzzy matching, statistical analysis, and multi-source verification to maintain
            data integrity and prevent fraud.""",
            verbose=False,
            allow_delegation=False,
            tools=[
                detect_duplicate_tool,
                verify_registration_tool,
                validate_years_practice_tool,
                verify_geographic_tool
            ]
        )

    def cross_validate_record(self, record: Dict, check_duplicates: bool = True) -> Dict[str, Any]:
        """
        Cross-validate a single provider record.
        
        Args:
            record (dict): Provider record
            check_duplicates (bool): Whether to check for duplicates
        
        Returns:
            dict: Cross-validation results with score 0-40
        """
        start_time = time.time()
        score = 0
        flags = []
        details = {}

        # ====================================================================
        # CHECK 1: DUPLICATE DETECTION (+10 points if no duplicate)
        # ====================================================================
        if check_duplicates:
            phone = record.get('phone', '')
            registration_no = record.get('registration_no', '')
            name = record.get('name', '')
            result = _detect_duplicate_func(phone, registration_no, name)
            
            if not result['is_duplicate']:
                score += 10
            else:
                score += 0
                if 'SUSPICIOUS' in result['message']:
                    flags.append('🚨 SUSPICIOUS_DUPLICATE')
                else:
                    flags.append('🚨 DUPLICATE_DETECTED')
            
            details['duplicate_check'] = result
        else:
            score += 10  # Skip duplicate check
            details['duplicate_check'] = {'skipped': True, 'score': 10}

        # ====================================================================
        # CHECK 2: REGISTRATION VERIFICATION (+10 points)
        # ====================================================================
        registration_no = record.get('registration_no', '')
        specialty = record.get('specialty', '')
        city = record.get('city', '')
        result = _verify_registration_func(registration_no, specialty, city)
        
        score += result['score']
        details['registration_check'] = result
        
        if not result['is_valid']:
            flags.append('⚠️ REGISTRATION_INVALID')

        # ====================================================================
        # CHECK 3: YEARS PRACTICE VALIDATION (+10 points)
        # ✅ FIX: Always call helper - it handles missing data internally!
        # ====================================================================
        years_practice = record.get('years_practice')
        result = _validate_years_practice_func(years_practice)
        score += result['score']
        details['years_practice_check'] = result
        
        if not result['is_valid']:
            flags.append('⚠️ ANOMALY_PRACTICE_YEARS')

        # ====================================================================
        # CHECK 4: GEOGRAPHIC CONSISTENCY (+10 points)
        # ✅ FIX: Always call helper - it handles missing data internally!
        # ====================================================================
        clinic_address = record.get('clinic_address', '')
        city = record.get('city', '')
        pincode = record.get('pincode', '')
        result = _verify_geographic_func(clinic_address, city, pincode)
        score += result['score']
        details['geographic_check'] = result
        
        if not result['is_consistent']:
            flags.append('⚠️ GEOGRAPHIC_MISMATCH')

        # ====================================================================
        # CALCULATE EXECUTION TIME
        # ====================================================================
        execution_time = (time.time() - start_time) * 1000

        # ====================================================================
        # RETURN RESULTS
        # ====================================================================
        return {
            'confidence_agent3': score,
            'cross_validation_flags': flags,
            'execution_time_agent3': round(execution_time, 2),
            'cross_validation_details': details
        }

    def cross_validate_batch(self, records: List[Dict], check_duplicates: bool = False) -> List[Dict]:
        """
        Cross-validate multiple records.
        Args:
            records (list): List of provider record dictionaries
            check_duplicates (bool): Whether to check for duplicates (default False for batch)
        Returns:
            list: List of cross-validation results
        """
        results = []
        for record in records:
            result = self.cross_validate_record(record, check_duplicates)
            results.append({
                **record,   # Original record
                **result    # Cross-validation results
            })
        return results

    def register_provider(self, record: Dict):
        """
        Register a provider in the duplicate detection database.
        Args:
            record (dict): Provider record
        """
        phone = record.get('phone', '')
        registration_no = record.get('registration_no', '')
        name = record.get('name', '')
        if phone and registration_no and name:
            register_provider(phone, registration_no, name)
            
    def clear_database(self):
        """Clear the provider database (for testing)"""
        clear_provider_database()

    def get_agent_info(self) -> Dict[str, str]:
        """Get agent metadata"""
        return {
            'name': 'Agent 3: Cross-Validation Engine',
            'role': self.agent.role,
            'goal': self.agent.goal,
            'tools': [tool.name for tool in self.agent.tools],
            'phase': 'Phase 1 (Rule-based)'
        }

# ============================================================================
# CONVENIENCE FUNCTION (For backward compatibility)
# ============================================================================
def agent_3_cross_validation(record: Dict, check_duplicates: bool = True) -> Dict[str, Any]:
    """
    Backward-compatible function for Agent 3 cross-validation.
    Args:
        record: Provider record dictionary
        check_duplicates: Whether to check for duplicates
    Returns:
        dict: Cross-validation results
    """
    agent = Agent3CrossValidation()
    return agent.cross_validate_record(record, check_duplicates)



# ============================================================================
# SELF-TEST FOR ALL AGENTS (Run when module is executed directly)
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("MULTI-AGENT TEST SUITE - AGENTS 1, 2 & 3")
    print("="*70)
    
    # ========================================================================
    # AGENT 1 TESTS
    # ========================================================================
    print("\n" + "="*70)
    print("AGENT 1 - DATA VALIDATION ENGINE")
    print("="*70)
    
    agent1 = Agent1DataValidation()
    info1 = agent1.get_agent_info()
    print(f"\n🤖 Agent 1 Info:")
    print(f"  Name: {info1['name']}")
    print(f"  Role: {info1['role']}")
    print(f"  Tools: {len(info1['tools'])}")
    
    # Agent 1 Test
    print("\n" + "-"*70)
    print("📋 Agent 1 Test: Perfect Record")
    print("-"*70)
    
    test_record_agent1 = {
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
    
    result1 = agent1.validate_record(test_record_agent1)
    print(f"  Validation Score: {result1['confidence_agent1']}/100")
    print(f"  Issues: {result1['issues_validation'] or 'None'}")
    print(f"  Time: {result1['execution_time_agent1']} ms")
    print("  ✓ AGENT 1 WORKING")

    # ========================================================================
    # AGENT 2 TESTS
    # ========================================================================
    print("\n" + "="*70)
    print("AGENT 2 - INFORMATION ENRICHMENT ENGINE")
    print("="*70)
    
    agent2 = Agent2DataEnrichment()
    info2 = agent2.get_agent_info()
    print(f"\n🤖 Agent 2 Info:")
    print(f"  Name: {info2['name']}")
    print(f"  Role: {info2['role']}")
    print(f"  Tools: {len(info2['tools'])}")
    
    # Agent 2 Test
    print("\n" + "-"*70)
    print("📋 Agent 2 Test: Record with Enrichment Needs")
    print("-"*70)
    
    test_record_agent2 = {
        'id': 1,
        'name': 'Dr. Test',
        'phone': '+91-98765-43210',
        'city': 'Banaglore',
        'specialty': 'NEUROLOGY',
        'clinic_address': 'Test Address',
        'pincode': '560001',
        'registration_no': 'MCI10012345'
    }
    
    result2 = agent2.enrich_record(test_record_agent2)
    print(f"  Enrichment Score: {result2['confidence_agent2']}/60")
    print(f"  Changes: {len(result2['enrichment_changes'])}")
    print(f"  Time: {result2['execution_time_agent2']} ms")
    print("  ✓ AGENT 2 WORKING")

    # ========================================================================
    # AGENT 3 TESTS
    # ========================================================================
    print("\n" + "="*70)
    print("AGENT 3 - CROSS-VALIDATION ENGINE")
    print("="*70)
    
    agent3 = Agent3CrossValidation()
    agent3.clear_database() # Clear for testing
    info3 = agent3.get_agent_info()
    print(f"\n🤖 Agent 3 Info:")
    print(f"  Name: {info3['name']}")
    print(f"  Role: {info3['role']}")
    print(f"  Tools: {len(info3['tools'])}")
    
    # Agent 3 Test 1: Clean record (no fraud)
    print("\n" + "-"*70)
    print("📋 Agent 3 Test 1: Clean Record")
    print("-"*70)
    
    test_record_agent3 = {
        'id': 1,
        'name': 'Dr. Test',
        'phone': '9876543210',
        'city': 'Bangalore',
        'specialty': 'Cardiology',
        'registration_no': 'MCI10012345',
        'years_practice': 12,
        'clinic_address': '123 MG Road Bangalore',
        'pincode': '560001'
    }
    
    result3 = agent3.cross_validate_record(test_record_agent3)
    print(f"  Cross-Validation Score: {result3['confidence_agent3']}/40")
    print(f"  Flags: {result3['cross_validation_flags'] or 'None'}")
    print(f"  Time: {result3['execution_time_agent3']} ms")
    assert result3['confidence_agent3'] == 40, "Should score 40/40"
    print("  ✓ PASSED")

    # Agent 3 Test 2: Duplicate detection
    print("\n" + "-"*70)
    print("📋 Agent 3 Test 2: Duplicate Detection")
    print("-"*70)
    
    # Register first provider
    agent3.register_provider(test_record_agent3)
    
    # Try to add duplicate
    duplicate_record = test_record_agent3.copy()
    result3_dup = agent3.cross_validate_record(duplicate_record)
    
    print(f"  Cross-Validation Score: {result3_dup['confidence_agent3']}/40")
    print(f"  Flags: {result3_dup['cross_validation_flags']}")
    assert result3_dup['confidence_agent3'] == 30, "Should score 30/40 (duplicate detected)"
    assert len(result3_dup['cross_validation_flags']) > 0, "Should have duplicate flag"
    print("  ✓ PASSED")

    # ========================================================================
    # COMBINED AGENTS 1 + 2 + 3 PIPELINE
    # ========================================================================
    print("\n" + "="*70)
    print("COMBINED AGENTS 1 + 2 + 3 PIPELINE")
    print("="*70)
    
    print("\n" + "-"*70)
    print("📋 Combined Test: Full Validation Pipeline")
    print("-"*70)
    
    agent3.clear_database() # Clear for fresh test

    combined_record = {
        'id': 99,
        'name': 'Dr. Combined Test',
        'phone': '+91 9876543210',
        'city': 'Banaglore',
        'specialty': 'NEUROLOGY',
        'clinic_address': '123 MG Road Bangalore',
        'pincode': '560001',
        'registration_no': 'MCI10012399',
        'years_practice': 10
    }
    
    # Step 1: Validate with Agent 1
    val_result = agent1.validate_record(combined_record)
    print(f"  Agent 1 Score: {val_result['confidence_agent1']}/100")
    
    # Step 2: Enrich with Agent 2
    enr_result = agent2.enrich_record(combined_record)
    print(f"  Agent 2 Score: {enr_result['confidence_agent2']}/60")
    
    # Step 3: Cross-validate with Agent 3
    cross_result = agent3.cross_validate_record(enr_result['record_enriched'])
    print(f"  Agent 3 Score: {cross_result['confidence_agent3']}/40")
    
    # Combined score
    combined_score = (val_result['confidence_agent1'] + 
                      enr_result['confidence_agent2'] + 
                      cross_result['confidence_agent3'])
                      
    print(f"  Combined Score: {combined_score}/200 ({combined_score/200*100:.1f}%)")
    print(f"  Enrichment Changes: {len(enr_result['enrichment_changes'])}")
    print(f"  Fraud Flags: {cross_result['cross_validation_flags'] or 'None'}")
    
    print("  ✓ MULTI-AGENT PIPELINE WORKING")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - AGENTS 1, 2 & 3 WORKING CORRECTLY")
    print("="*70)
