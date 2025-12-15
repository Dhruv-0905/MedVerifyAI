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
    """
    Validate Indian phone number format.
    
    Args:
        phone: Phone number string
    
    Returns:
        dict: {'valid': bool, 'score': int, 'issue': str or None}
    """
    return _validate_phone(phone)


@tool("validate_pincode_tool")
def validate_pincode_tool(pincode: str) -> Dict[str, Any]:
    """
    Validate Indian 6-digit pincode.
    
    Args:
        pincode: Pincode string
    
    Returns:
        dict: {'valid': bool, 'score': int, 'issue': str or None}
    """
    return _validate_pincode(pincode)


@tool("validate_specialty_tool")
def validate_specialty_tool(specialty: str) -> Dict[str, Any]:
    """
    Validate specialty against approved list.
    
    Args:
        specialty: Medical specialty string
    
    Returns:
        dict: {'valid': bool, 'score': int, 'issue': str or None}
    """
    return _validate_specialty(specialty)


@tool("validate_registration_tool")
def validate_registration_tool(registration_no: str) -> Dict[str, Any]:
    """
    Validate registration number format.
    
    Args:
        registration_no: Registration number string
    
    Returns:
        dict: {'valid': bool, 'score': int, 'issue': str or None}
    """
    return _validate_registration(registration_no)


@tool("validate_required_fields_tool")
def validate_required_fields_tool(record: Dict) -> Dict[str, Any]:
    """
    Validate all required fields are present.
    
    Args:
        record: Provider record dictionary
    
    Returns:
        dict: {'valid': bool, 'score': int, 'issue': str or None}
    """
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
        result = _validate_required_fields(record)  # Call underlying function directly
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
        result = _validate_phone(phone)  # Call underlying function
        score += result['score']
        if result['issue']:
            issues.append(result['issue'])
        
        # ====================================================================
        # CHECK 3: PINCODE FORMAT (20 points)
        # ====================================================================
        pincode = record.get('pincode', '')
        result = _validate_pincode(pincode)  # Call underlying function
        score += result['score']
        if result['issue']:
            issues.append(result['issue'])
        
        # ====================================================================
        # CHECK 4: SPECIALTY IN APPROVED LIST (20 points)
        # ====================================================================
        specialty = record.get('specialty', '')
        result = _validate_specialty(specialty)  # Call underlying function
        score += result['score']
        if result['issue']:
            issues.append(result['issue'])
        
        # ====================================================================
        # CHECK 5: REGISTRATION NUMBER PATTERN (20 points)
        # ====================================================================
        registration_no = record.get('registration_no', '')
        result = _validate_registration(registration_no)  # Call underlying function
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
                **record,  # Original record
                **result   # Validation results
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
# SELF-TEST (Run when module is executed directly)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AGENT 1 - DATA VALIDATION ENGINE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Initialize agent
    agent = Agent1DataValidation()
    
    # Display agent info
    info = agent.get_agent_info()
    print(f"\n🤖 Agent Information:")
    print(f"   Name: {info['name']}")
    print(f"   Role: {info['role']}")
    print(f"   Tools: {', '.join(info['tools'])}")
    
    # Test Case 1: Perfect Record
    print("\n" + "-"*70)
    print("📋 TEST 1: Perfect Record (All fields valid)")
    print("-"*70)
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
    result = agent.validate_record(perfect_record)
    print(f"   Confidence: {result['confidence_agent1']}/100")
    print(f"   Issues: {result['issues_validation'] if result['issues_validation'] else 'None'}")
    print(f"   Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 100, "Perfect record should score 100"
    print("   ✓ PASSED")
    
    # Test Case 2: Invalid Phone
    print("\n" + "-"*70)
    print("📋 TEST 2: Invalid Phone Number")
    print("-"*70)
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
    result = agent.validate_record(invalid_phone_record)
    print(f"   Confidence: {result['confidence_agent1']}/100")
    print(f"   Issues: {result['issues_validation']}")
    print(f"   Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 80, "Should have 4 valid checks, 1 invalid"
    assert any('phone' in issue.lower() for issue in result['issues_validation']), "Should flag phone"
    print("   ✓ PASSED")
    
    # Test Case 3: Invalid Specialty
    print("\n" + "-"*70)
    print("📋 TEST 3: Invalid Specialty")
    print("-"*70)
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
    result = agent.validate_record(invalid_specialty_record)
    print(f"   Confidence: {result['confidence_agent1']}/100")
    print(f"   Issues: {result['issues_validation']}")
    print(f"   Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 80, "Should have 4 valid checks, 1 invalid"
    assert any('specialty' in issue.lower() for issue in result['issues_validation']), "Should flag specialty"
    print("   ✓ PASSED")
    
    # Test Case 4: Missing Required Fields
    print("\n" + "-"*70)
    print("📋 TEST 4: Missing Required Fields")
    print("-"*70)
    missing_fields_record = {
        'id': 99,
        'name': 'Dr. Unknown',
        # Missing phone, city, specialty, registration_no, clinic_address, pincode
    }
    result = agent.validate_record(missing_fields_record)
    print(f"   Confidence: {result['confidence_agent1']}/100")
    print(f"   Issues: {result['issues_validation']}")
    print(f"   Time: {result['execution_time_agent1']} ms")
    assert result['confidence_agent1'] == 0, "Should score 0 if required fields missing"
    assert any('missing' in issue.lower() for issue in result['issues_validation']), "Should flag missing fields"
    print("   ✓ PASSED")
    
    # Test Case 5: Batch Processing
    print("\n" + "-"*70)
    print("📋 TEST 5: Batch Processing (3 records)")
    print("-"*70)
    batch_records = [perfect_record, invalid_phone_record, invalid_specialty_record]
    batch_results = agent.validate_batch(batch_records)
    print(f"   Records processed: {len(batch_results)}")
    print(f"   Average confidence: {sum(r['confidence_agent1'] for r in batch_results) / len(batch_results):.1f}")
    print(f"   Average time: {sum(r['execution_time_agent1'] for r in batch_results) / len(batch_results):.2f} ms")
    assert len(batch_results) == 3, "Should process all 3 records"
    print("   ✓ PASSED")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - AGENT 1 VALIDATION ENGINE WORKING CORRECTLY")
    print("="*70)
