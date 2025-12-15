"""
Pytest configuration and fixtures for MediSure testing
"""
import pytest
import pandas as pd
from pathlib import Path


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


@pytest.fixture
def sample_invalid_record():
    """Invalid provider record for testing"""
    return {
        'id': 99,
        'name': 'Dr. Invalid',
        'phone': '12345',  # Too short
        'city': 'UnknownCity',
        'specialty': 'FakeSpecialty',
        'registration_no': 'INVALID',
        'years_practice': 100,  # Suspicious
        'clinic_address': 'Test',
        'pincode': '123'  # Invalid
    }


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame with 5 records"""
    data = [
        {
            'id': 1, 'name': 'Dr. A', 'phone': '9876543210',
            'city': 'Bangalore', 'specialty': 'Cardiology',
            'registration_no': 'MCI001', 'years_practice': 5,
            'clinic_address': 'Addr 1', 'pincode': '560001'
        },
        {
            'id': 2, 'name': 'Dr. B', 'phone': '9876543211',
            'city': 'Chennai', 'specialty': 'Neurology',
            'registration_no': 'MCI002', 'years_practice': 10,
            'clinic_address': 'Addr 2', 'pincode': '600018'
        },
        {
            'id': 3, 'name': 'Dr. C', 'phone': '9876543210',  # Duplicate phone
            'city': 'Mumbai', 'specialty': 'Orthopedics',
            'registration_no': 'MCI003', 'years_practice': 3,
            'clinic_address': 'Addr 3', 'pincode': '400001'
        },
        {
            'id': 4, 'name': 'Dr. D', 'phone': '98765',  # Invalid phone
            'city': 'Delhi', 'specialty': 'Pediatrics',
            'registration_no': 'MCI004', 'years_practice': 7,
            'clinic_address': 'Addr 4', 'pincode': '110001'
        },
        {
            'id': 5, 'name': 'Dr. E', 'phone': '9876543215',
            'city': 'Banaglore',  # Typo in city
            'specialty': 'Dermatology',
            'registration_no': 'MCI005', 'years_practice': 12,
            'clinic_address': 'Addr 5', 'pincode': '560002'
        }
    ]
    return pd.DataFrame(data)
