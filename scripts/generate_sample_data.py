"""
Generate sample provider dataset with intentional errors for testing
"""
import pandas as pd
import random
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from lookup_tables_extended import SPECIALTY_LIST, CITY_LIST

# Sample data configuration
NUM_RECORDS = 300
ERROR_RATE = 0.15  # 15% records with errors

# Sample names
DOCTOR_NAMES = [
    "Dr. Rajesh Sharma", "Dr. Priya Patel", "Dr. Amit Kumar",
    "Dr. Sneha Reddy", "Dr. Vikram Singh", "Dr. Anjali Nair",
    "Dr. Sanjay Gupta", "Dr. Kavita Joshi", "Dr. Arun Mehta",
    "Dr. Deepa Rao", "Dr. Manoj Verma", "Dr. Nisha Shah"
]

# Generate dataset
def generate_sample_dataset(num_records=300, error_rate=0.15):
    """Generate sample provider dataset"""
    records = []
    
    for i in range(1, num_records + 1):
        # Determine if this record should have errors
        has_error = random.random() < error_rate
        
        # Base valid record
        record = {
            'id': i,
            'name': random.choice(DOCTOR_NAMES),
            'phone': f"98765{random.randint(10000, 99999)}",
            'city': random.choice(CITY_LIST[:30]),
            'specialty': random.choice(SPECIALTY_LIST[:40]),
            'registration_no': f"MCI{random.randint(10000000, 99999999)}",
            'years_practice': random.randint(1, 30),
            'clinic_address': f"{random.randint(1, 999)} MG Road",
            'pincode': f"{random.randint(100000, 999999)}"
        }
        
        # Inject errors randomly
        if has_error:
            error_type = random.choice([
                'invalid_phone', 'invalid_pincode', 'typo_city',
                'invalid_specialty', 'duplicate_phone', 'invalid_reg'
            ])
            
            if error_type == 'invalid_phone':
                record['phone'] = f"{random.randint(1000, 9999)}"  # Too short
            elif error_type == 'invalid_pincode':
                record['pincode'] = f"{random.randint(100, 9999)}"  # Wrong length
            elif error_type == 'typo_city':
                record['city'] = "Banaglore"  # Typo
            elif error_type == 'invalid_specialty':
                record['specialty'] = "FakeSpecialty"
            elif error_type == 'duplicate_phone':
                if i > 1:
                    record['phone'] = records[i-2]['phone']  # Duplicate
            elif error_type == 'invalid_reg':
                record['registration_no'] = "INVALID123"
        
        records.append(record)
    
    return pd.DataFrame(records)


if __name__ == "__main__":
    print("Generating sample dataset...")
    df = generate_sample_dataset(NUM_RECORDS, ERROR_RATE)
    
    # Save to CSV
    output_path = Path(__file__).parent.parent / 'data' / 'sample_data.csv'
    df.to_csv(output_path, index=False)
    
    print(f"✅ Generated {len(df)} records")
    print(f"📁 Saved to: {output_path}")
    print(f"📊 Stats:")
    print(f"   - Total records: {len(df)}")
    print(f"   - Expected errors: ~{int(len(df) * ERROR_RATE)}")
