"""
Pytest configuration and fixtures for MediSure tests
"""
import pytest
import pandas as pd


@pytest.fixture
def sample_record():
    """Fixture providing a perfect sample record"""
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


@pytest.fixture
def sample_dataframe():
    """
    Fixture providing a sample DataFrame with mixed quality records
    
    Records breakdown:
    - Record 1: VALID (all fields correct)
    - Record 2: Invalid phone (too short)
    - Record 3: Invalid pincode (5 digits instead of 6)
    - Record 4: Invalid specialty (not in list)
    - Record 5: Invalid registration (only 3 digits)
    """
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Dr. A', 'Dr. B', 'Dr. C', 'Dr. D', 'Dr. E'],
        'phone': ['9876543210', '12345', '9876543212', '9876543213', '9876543215'],  # B invalid
        'city': ['Bangalore', 'Mumbai', 'Delhi', 'Chennai', 'Bangalore'],  # E has typo below
        'specialty': ['Cardiology', 'Neurology', 'Orthopedics', 'InvalidSpec', 'Dermatology'],  # D invalid
        'registration_no': ['MCI10012345', 'MCI10012346', 'MCI10012347', 'MCI10012348', 'MCI005'],  # E invalid
        'years_practice': [5, 10, 3, 15, 12],
        'clinic_address': ['Addr 1', 'Addr 2', 'Addr 3', 'Addr 4', 'Addr 5'],
        'pincode': ['560001', '400001', '12345', '600001', '560002']  # C invalid (5 digits)
    }
    return pd.DataFrame(data)


@pytest.fixture
def invalid_record():
    """Fixture providing an invalid record (missing required fields)"""
    return {
        'id': 999,
        'name': 'Dr. Invalid',
        # Missing phone, city, specialty, registration_no, clinic_address, pincode
    }


@pytest.fixture
def batch_records():
    """Fixture providing a batch of mixed records"""
    return [
        {
            'id': 1, 'name': 'Dr. Perfect', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'registration_no': 'MCI10012345', 'clinic_address': 'Test 1',
            'pincode': '560001'
        },
        {
            'id': 2, 'name': 'Dr. BadPhone', 'phone': '123',
            'city': 'Mumbai', 'specialty': 'Neurology',
            'registration_no': 'MCI10012346', 'clinic_address': 'Test 2',
            'pincode': '400001'
        },
        {
            'id': 3, 'name': 'Dr. BadPincode', 'phone': '9876543212',
            'city': 'Delhi', 'specialty': 'Orthopedics',
            'registration_no': 'MCI10012347', 'clinic_address': 'Test 3',
            'pincode': '12345'
        }
    ]
