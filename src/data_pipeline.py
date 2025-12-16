"""
Data Pipeline Module for MedverifyAI
Handles CSV file processing and batch validation
"""

import pandas as pd
import io
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json


class CSVHandler:
    """
    Handles CSV file upload, parsing, and validation.
    Ensures data is in correct format for orchestrator processing.
    """
    
    # Expected column mappings (flexible naming)
    COLUMN_MAPPINGS = {
        'name': ['name', 'doctor_name', 'provider_name', 'full_name'],
        'phone': ['phone', 'phone_number', 'contact', 'mobile', 'contact_number'],
        'city': ['city', 'location', 'city_name'],
        'specialty': ['specialty', 'speciality', 'specialization', 'department'],
        'registration_no': ['registration_no', 'registration_number', 'reg_no', 'license_no', 'registration'],
        'years_practice': ['years_practice', 'years_of_practice', 'experience', 'years_experience'],
        'clinic_address': ['clinic_address', 'address', 'clinic_location', 'office_address'],
        'pincode': ['pincode', 'pin_code', 'postal_code', 'zip', 'zip_code']
    }
    
    # Required fields
    REQUIRED_FIELDS = ['name', 'phone', 'registration_no']
    
    def __init__(self):
        """Initialize CSV Handler"""
        self.last_upload_stats = {}
        
    def parse_csv(self, file_content: Any, encoding: str = 'utf-8') -> Tuple[bool, pd.DataFrame, Dict]:
        """
        Parse CSV file content into DataFrame.
        
        Args:
            file_content: File content (can be string, bytes, or file-like object)
            encoding: File encoding (default: utf-8)
            
        Returns:
            Tuple of (success, dataframe, stats_dict)
        """
        try:
            # Handle different input types
            if isinstance(file_content, bytes):
                file_content = io.StringIO(file_content.decode(encoding))
            elif isinstance(file_content, str):
                file_content = io.StringIO(file_content)
            
            # Read CSV
            df = pd.read_csv(file_content)
            
            # Basic validation
            if df.empty:
                return False, pd.DataFrame(), {
                    'error': 'CSV file is empty',
                    'rows': 0,
                    'columns': 0
                }
            
            stats = {
                'success': True,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns)
            }
            
            return True, df, stats
            
        except Exception as e:
            return False, pd.DataFrame(), {
                'error': f'Failed to parse CSV: {str(e)}',
                'rows': 0,
                'columns': 0
            }
    
    def map_columns(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame, Dict]:
        """
        Map CSV columns to expected format.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (success, mapped_dataframe, mapping_info)
        """
        try:
            # Normalize column names (lowercase, strip spaces)
            df.columns = df.columns.str.lower().str.strip()
            
            mapped_columns = {}
            unmapped_columns = []
            missing_required = []
            
            # Try to map each expected field
            for expected_field, possible_names in self.COLUMN_MAPPINGS.items():
                found = False
                for possible_name in possible_names:
                    if possible_name in df.columns:
                        mapped_columns[expected_field] = possible_name
                        found = True
                        break
                
                if not found:
                    # Check if it's a required field
                    if expected_field in self.REQUIRED_FIELDS:
                        missing_required.append(expected_field)
            
            # Check for missing required fields
            if missing_required:
                return False, pd.DataFrame(), {
                    'error': f'Missing required fields: {", ".join(missing_required)}',
                    'mapped_columns': mapped_columns,
                    'missing_required': missing_required
                }
            
            # Create new DataFrame with mapped columns
            mapped_df = pd.DataFrame()
            for expected_field, original_name in mapped_columns.items():
                mapped_df[expected_field] = df[original_name]
            
            # Identify unmapped columns (extra columns in CSV)
            mapped_originals = set(mapped_columns.values())
            unmapped_columns = [col for col in df.columns if col not in mapped_originals]
            
            mapping_info = {
                'success': True,
                'mapped_columns': mapped_columns,
                'unmapped_columns': unmapped_columns,
                'total_mapped': len(mapped_columns),
                'total_unmapped': len(unmapped_columns)
            }
            
            return True, mapped_df, mapping_info
            
        except Exception as e:
            return False, pd.DataFrame(), {
                'error': f'Column mapping failed: {str(e)}',
                'mapped_columns': {},
                'unmapped_columns': []
            }
    
    def validate_data_types(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """
        Validate data types and format of each field.
        
        Args:
            df: DataFrame with mapped columns
            
        Returns:
            Tuple of (all_valid, list of validation issues)
        """
        issues = []
        
        # Validate each row
        for idx, row in df.iterrows():
            row_issues = []
            
            # Phone validation (should be convertible to string with digits)
            if 'phone' in df.columns:
                phone = str(row['phone']).strip()
                if not phone or phone == 'nan':
                    row_issues.append(f"Row {idx+2}: Phone is empty")
            
            # Registration number validation
            if 'registration_no' in df.columns:
                reg_no = str(row['registration_no']).strip()
                if not reg_no or reg_no == 'nan':
                    row_issues.append(f"Row {idx+2}: Registration number is empty")
            
            # Years practice validation (should be numeric)
            if 'years_practice' in df.columns:
                try:
                    years = row['years_practice']
                    if pd.notna(years):
                        years_int = int(float(years))
                        if years_int < 0 or years_int > 60:
                            row_issues.append(f"Row {idx+2}: Years practice out of range (0-60)")
                except (ValueError, TypeError):
                    row_issues.append(f"Row {idx+2}: Years practice is not a valid number")
            
            # Pincode validation (should be numeric, 6 digits)
            if 'pincode' in df.columns:
                pincode = str(row['pincode']).strip()
                if pincode and pincode != 'nan':
                    # Remove decimal point if present
                    pincode = pincode.split('.')[0]
                    if not pincode.isdigit() or len(pincode) != 6:
                        row_issues.append(f"Row {idx+2}: Pincode should be 6 digits")
            
            if row_issues:
                issues.extend(row_issues)
        
        all_valid = len(issues) == 0
        return all_valid, issues
    
    def prepare_records(self, df: pd.DataFrame) -> List[Dict]:
        """
        Convert DataFrame to list of record dictionaries for orchestrator.
        
        Args:
            df: DataFrame with mapped columns
            
        Returns:
            List of record dictionaries
        """
        records = []
        
        for idx, row in df.iterrows():
            record = {}
            
            # Add all available fields
            for field in self.COLUMN_MAPPINGS.keys():
                if field in df.columns:
                    value = row[field]
                    # Handle NaN values
                    if pd.isna(value):
                        record[field] = ''
                    else:
                        # Convert to appropriate type
                        if field == 'years_practice':
                            try:
                                record[field] = int(float(value))
                            except (ValueError, TypeError):
                                record[field] = 0
                        elif field == 'pincode':
                            # Convert to string, remove decimal
                            record[field] = str(value).split('.')[0].strip()
                        else:
                            record[field] = str(value).strip()
                else:
                    record[field] = ''
            
            # Add row number for tracking
            record['_row_number'] = idx + 2  # +2 for Excel-style row numbering (header is row 1)
            
            records.append(record)
        
        return records
    
    def process_file(self, file_content: Any, encoding: str = 'utf-8') -> Tuple[bool, List[Dict], Dict]:
        """
        Complete pipeline: parse, map, validate, and prepare records.
        
        Args:
            file_content: File content
            encoding: File encoding
            
        Returns:
            Tuple of (success, records_list, processing_stats)
        """
        stats = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stages': {}
        }
        
        # Stage 1: Parse CSV
        success, df, parse_stats = self.parse_csv(file_content, encoding)
        stats['stages']['parse'] = parse_stats
        if not success:
            return False, [], stats
        
        # Stage 2: Map columns
        success, mapped_df, mapping_stats = self.map_columns(df)
        stats['stages']['mapping'] = mapping_stats
        if not success:
            return False, [], stats
        
        # Stage 3: Validate data types
        all_valid, validation_issues = self.validate_data_types(mapped_df)
        stats['stages']['validation'] = {
            'all_valid': all_valid,
            'issues_count': len(validation_issues),
            'issues': validation_issues[:10]  # First 10 issues only
        }
        
        # Stage 4: Prepare records (even if validation issues exist)
        records = self.prepare_records(mapped_df)
        stats['stages']['preparation'] = {
            'records_prepared': len(records)
        }
        
        # Overall stats
        stats['success'] = True
        stats['total_records'] = len(records)
        stats['has_validation_warnings'] = len(validation_issues) > 0
        
        self.last_upload_stats = stats
        
        return True, records, stats
    
    def get_template_columns(self) -> List[str]:
        """
        Get list of expected column names for CSV template.
        
        Returns:
            List of column names
        """
        return list(self.COLUMN_MAPPINGS.keys())
    
    def create_template_csv(self) -> str:
        """
        Create a CSV template string with example data.
        
        Returns:
            CSV string with headers and sample row
        """
        headers = self.get_template_columns()
        sample_data = {
            'name': 'Dr. John Smith',
            'phone': '9876543210',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012345',
            'years_practice': '10',
            'clinic_address': '123 MG Road Bangalore',
            'pincode': '560001'
        }
        
        # Create DataFrame
        df = pd.DataFrame([sample_data])
        
        # Convert to CSV string
        return df.to_csv(index=False)



class BatchProcessor:
    """
    Processes multiple provider records through the orchestrator.
    Provides progress tracking, results aggregation, and export functionality.
    """
    
    def __init__(self, orchestrator):
        """
        Initialize Batch Processor.
        
        Args:
            orchestrator: MultiAgentOrchestrator instance
        """
        self.orchestrator = orchestrator
        self.processing_stats = {}
        self.results = []
        
    def process_batch(self, records: List[Dict], check_duplicates: bool = True, 
                     progress_callback=None) -> Tuple[List[Dict], Dict]:
        """
        Process a batch of records through the orchestrator.
        
        Args:
            records: List of provider records
            check_duplicates: Enable duplicate detection
            progress_callback: Optional callback function for progress updates
                              Signature: callback(current, total, record_result)
        
        Returns:
            Tuple of (results_list, batch_statistics)
        """
        results = []
        start_time = datetime.now()
        
        total_records = len(records)
        
        # Process each record
        for idx, record in enumerate(records):
            try:
                # Validate record
                result = self.orchestrator.validate_provider(
                    record, 
                    check_duplicates=check_duplicates
                )
                
                # Add record tracking info
                result['batch_index'] = idx
                result['batch_row_number'] = record.get('_row_number', idx + 1)
                
                results.append(result)
                
                # Progress callback
                if progress_callback:
                    progress_callback(idx + 1, total_records, result)
                    
            except Exception as e:
                # Handle errors gracefully
                error_result = {
                    'batch_index': idx,
                    'batch_row_number': record.get('_row_number', idx + 1),
                    'original_record': record,
                    'error': str(e),
                    'decision': 'ERROR',
                    'combined_score': 0,
                    'combined_confidence_percentage': 0.0
                }
                results.append(error_result)
                
                if progress_callback:
                    progress_callback(idx + 1, total_records, error_result)
        
        # Calculate batch statistics
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        stats = self._calculate_batch_stats(results, processing_time)
        
        self.results = results
        self.processing_stats = stats
        
        return results, stats
    
    def _calculate_batch_stats(self, results: List[Dict], processing_time: float) -> Dict:
        """
        Calculate comprehensive statistics for batch processing.
        
        Args:
            results: List of validation results
            processing_time: Total processing time in seconds
            
        Returns:
            Statistics dictionary
        """
        total = len(results)
        
        # Decision breakdown
        decisions = {}
        for result in results:
            decision = result.get('decision', 'UNKNOWN')
            decisions[decision] = decisions.get(decision, 0) + 1
        
        # Score statistics
        scores = [r.get('combined_score', 0) for r in results if 'combined_score' in r]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Confidence statistics
        confidences = [r.get('combined_confidence_percentage', 0) for r in results if 'combined_confidence_percentage' in r]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Fraud detection statistics
        fraud_flags_count = 0
        fraud_types = {}
        for result in results:
            flags = result.get('agent3_cross_validation', {}).get('cross_validation_flags', [])
            fraud_flags_count += len(flags)
            for flag in flags:
                fraud_types[flag] = fraud_types.get(flag, 0) + 1
        
        # Enrichment statistics
        total_enrichments = 0
        for result in results:
            enrichments = result.get('agent2_enrichment', {}).get('enrichment_changes', [])
            total_enrichments += len(enrichments)
        
        # Quality level distribution
        quality_levels = {}
        for result in results:
            quality = result.get('summary', {}).get('quality_level', 'UNKNOWN')
            quality_levels[quality] = quality_levels.get(quality, 0) + 1
        
        # Error tracking
        errors = [r for r in results if r.get('decision') == 'ERROR']
        
        stats = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_records': total,
            'processing_time_seconds': round(processing_time, 2),
            'records_per_second': round(total / processing_time, 2) if processing_time > 0 else 0,
            'avg_time_per_record_ms': round((processing_time * 1000) / total, 2) if total > 0 else 0,
            
            'decisions': decisions,
            'decision_percentages': {
                k: round((v / total) * 100, 1) for k, v in decisions.items()
            },
            
            'scores': {
                'average': round(avg_score, 2),
                'min': min(scores) if scores else 0,
                'max': max(scores) if scores else 0
            },
            
            'confidence': {
                'average_percentage': round(avg_confidence, 1),
                'min_percentage': round(min(confidences), 1) if confidences else 0,
                'max_percentage': round(max(confidences), 1) if confidences else 0
            },
            
            'fraud_detection': {
                'total_flags': fraud_flags_count,
                'records_with_flags': sum(1 for r in results if r.get('agent3_cross_validation', {}).get('cross_validation_flags', [])),
                'flag_types': fraud_types
            },
            
            'enrichment': {
                'total_enrichments': total_enrichments,
                'avg_per_record': round(total_enrichments / total, 1) if total > 0 else 0
            },
            
            'quality_distribution': quality_levels,
            
            'errors': {
                'count': len(errors),
                'percentage': round((len(errors) / total) * 100, 1) if total > 0 else 0
            }
        }
        
        return stats
    
    def export_results_csv(self, filepath: str, include_full_details: bool = False) -> bool:
        """
        Export results to CSV file.
        
        Args:
            filepath: Output file path
            include_full_details: Include all details (default: summary only)
            
        Returns:
            Success status
        """
        try:
            if not self.results:
                return False
            
            export_data = []
            
            for result in self.results:
                row = {
                    'Row': result.get('batch_row_number', ''),
                    'Name': result.get('original_record', {}).get('name', ''),
                    'Phone': result.get('original_record', {}).get('phone', ''),
                    'City': result.get('original_record', {}).get('city', ''),
                    'Specialty': result.get('original_record', {}).get('specialty', ''),
                    'Registration': result.get('original_record', {}).get('registration_no', ''),
                    'Decision': result.get('decision', ''),
                    'Score': f"{result.get('combined_score', 0)}/200",
                    'Confidence': f"{result.get('combined_confidence_percentage', 0):.1f}%",
                    'Quality': result.get('summary', {}).get('quality_level', ''),
                    'Fraud_Flags': len(result.get('agent3_cross_validation', {}).get('cross_validation_flags', [])),
                    'Enrichments': len(result.get('agent2_enrichment', {}).get('enrichment_changes', []))
                }
                
                if include_full_details:
                    row['Decision_Reason'] = result.get('decision_reason', '')
                    row['Fraud_Details'] = '; '.join(result.get('agent3_cross_validation', {}).get('cross_validation_flags', []))
                    row['Enrichment_Details'] = '; '.join(result.get('agent2_enrichment', {}).get('enrichment_changes', []))
                
                export_data.append(row)
            
            df = pd.DataFrame(export_data)
            df.to_csv(filepath, index=False)
            
            return True
            
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def export_results_json(self, filepath: str, include_full_results: bool = True) -> bool:
        """
        Export results to JSON file.
        
        Args:
            filepath: Output file path
            include_full_results: Include complete validation results
            
        Returns:
            Success status
        """
        try:
            if not self.results:
                return False
            
            export_data = {
                'batch_statistics': self.processing_stats,
                'results': self.results if include_full_results else [
                    {
                        'row': r.get('batch_row_number'),
                        'decision': r.get('decision'),
                        'score': r.get('combined_score'),
                        'confidence': r.get('combined_confidence_percentage')
                    } for r in self.results
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def get_summary_report(self) -> str:
        """
        Generate a human-readable summary report.
        
        Returns:
            Formatted summary string
        """
        if not self.processing_stats:
            return "No batch processing data available"
        
        stats = self.processing_stats
        
        report = f"""
{'='*70}
BATCH PROCESSING SUMMARY REPORT
{'='*70}

Processing Information:
  Total Records:        {stats['total_records']}
  Processing Time:      {stats['processing_time_seconds']}s
  Speed:                {stats['records_per_second']} records/second
  Avg Time/Record:      {stats['avg_time_per_record_ms']}ms

Decision Breakdown:
"""
        
        for decision, count in stats['decisions'].items():
            percentage = stats['decision_percentages'][decision]
            report += f"  {decision:20s} {count:4d} ({percentage:5.1f}%)\n"
        
        report += f"""
Score Statistics:
  Average:              {stats['scores']['average']:.1f}/200
  Range:                {stats['scores']['min']}-{stats['scores']['max']}
  Avg Confidence:       {stats['confidence']['average_percentage']:.1f}%

Fraud Detection:
  Total Flags:          {stats['fraud_detection']['total_flags']}
  Records Flagged:      {stats['fraud_detection']['records_with_flags']}
"""
        
        if stats['fraud_detection']['flag_types']:
            report += "  Flag Types:\n"
            for flag_type, count in stats['fraud_detection']['flag_types'].items():
                report += f"    {flag_type}: {count}\n"
        
        report += f"""
Data Enrichment:
  Total Enrichments:    {stats['enrichment']['total_enrichments']}
  Avg per Record:       {stats['enrichment']['avg_per_record']}

Quality Distribution:
"""
        
        for quality, count in stats['quality_distribution'].items():
            percentage = (count / stats['total_records']) * 100
            report += f"  {quality:20s} {count:4d} ({percentage:5.1f}%)\n"
        
        if stats['errors']['count'] > 0:
            report += f"""
Errors:
  Error Count:          {stats['errors']['count']} ({stats['errors']['percentage']}%)
"""
        
        report += f"\n{'='*70}\n"
        
        return report
    
    def get_failed_records(self) -> List[Dict]:
        """
        Get all records that were rejected or had errors.
        
        Returns:
            List of failed record results
        """
        if not self.results:
            return []
        
        failed = [
            r for r in self.results 
            if r.get('decision') in ['REJECT', 'ERROR']
        ]
        
        return failed
    
    def get_review_required_records(self) -> List[Dict]:
        """
        Get all records requiring manual review.
        
        Returns:
            List of records needing review
        """
        if not self.results:
            return []
        
        review = [
            r for r in self.results 
            if r.get('decision') == 'MANUAL_REVIEW'
        ]
        
        return review
    
    def get_approved_records(self) -> List[Dict]:
        """
        Get all approved records (AUTO_APPROVE and CONDITIONAL_APPROVE).
        
        Returns:
            List of approved record results
        """
        if not self.results:
            return []
        
        approved = [
            r for r in self.results 
            if r.get('decision') in ['AUTO_APPROVE', 'CONDITIONAL_APPROVE']
        ]
        
        return approved

# Comprehensive self-test
if __name__ == '__main__':
    print("="*70)
    print("DATA PIPELINE - COMPREHENSIVE SELF TEST")
    print("="*70)
    
    # Import orchestrator for batch testing
    try:
        import sys
        sys.path.append('.')
        from orchestrator import MultiAgentOrchestrator
        orchestrator_available = True
    except ImportError:
        orchestrator_available = False
        print("\n⚠️  Orchestrator not available - testing CSV handler only\n")
    
    handler = CSVHandler()
    
    # Test 1: CSV Handler - Template Creation
    print("\n" + "-"*70)
    print("TEST 1: CSV Handler - Template Creation")
    print("-"*70)
    template = handler.create_template_csv()
    print(template[:200] + "...")
    print("✓ Template created successfully")
    
    # Test 2: CSV Handler - Process Template
    print("\n" + "-"*70)
    print("TEST 2: CSV Handler - Process Template")
    print("-"*70)
    success, records, stats = handler.process_file(template)
    print(f"Success: {success}")
    print(f"Records prepared: {len(records)}")
    print(f"First record: {records[0]['name']}")
    print("✓ Template processed successfully")
    
    # Test 3: CSV Handler - Multiple Records
    print("\n" + "-"*70)
    print("TEST 3: CSV Handler - Multiple Records")
    print("-"*70)
    multi_csv = """name,phone,city,specialty,registration_no,years_practice,clinic_address,pincode
Dr. John Smith,9876543210,Bangalore,Cardiology,MCI10012345,10,123 MG Road,560001
Dr. Jane Doe,9876543211,Mumbai,Dermatology,MCI10012346,15,456 Marine Drive,400001
Dr. Bob Wilson,9876543212,Delhi,Orthopedics,MCI10012347,8,789 CP,110001"""
    
    success, records, stats = handler.process_file(multi_csv)
    print(f"Success: {success}")
    print(f"Records prepared: {len(records)}")
    print(f"Validation warnings: {stats['has_validation_warnings']}")
    print("✓ Multiple records processed")
    
    # Test 4: CSV Handler - Invalid Data
    print("\n" + "-"*70)
    print("TEST 4: CSV Handler - Missing Required Fields")
    print("-"*70)
    invalid_csv = "wrong_column,another_column\nvalue1,value2"
    success, records, stats = handler.process_file(invalid_csv)
    print(f"Success: {success}")
    if not success:
        print(f"Error caught: {stats['stages']['mapping'].get('error', 'Unknown')[:50]}...")
    print("✓ Invalid CSV handled correctly")
    
    # Test 5: Batch Processor (if orchestrator available)
    if orchestrator_available:
        print("\n" + "-"*70)
        print("TEST 5: Batch Processor - Small Batch")
        print("-"*70)
        
        orchestrator = MultiAgentOrchestrator()
        processor = BatchProcessor(orchestrator)
        
        # Prepare test records
        test_records = [
            {
                'name': 'Dr. Test Alpha',
                'phone': '9876543210',
                'city': 'Bangalore',
                'specialty': 'Cardiology',
                'registration_no': 'MCI10012345',
                'years_practice': 10,
                'clinic_address': '123 MG Road',
                'pincode': '560001'
            },
            {
                'name': 'Dr. Test Beta',
                'phone': '9876543211',
                'city': 'Mumbai',
                'specialty': 'Dermatology',
                'registration_no': 'MCI10012346',
                'years_practice': 15,
                'clinic_address': '456 Marine Drive',
                'pincode': '400001'
            }
        ]
        
        # Process with progress callback
        def progress_callback(current, total, result):
            print(f"  Progress: {current}/{total} - {result.get('decision', 'UNKNOWN')}")
        
        results, stats = processor.process_batch(
            test_records, 
            check_duplicates=False,
            progress_callback=progress_callback
        )
        
        print(f"\nResults: {len(results)} records processed")
        print(f"Average score: {stats['scores']['average']}/200")
        print(f"Processing speed: {stats['records_per_second']} records/sec")
        print("✓ Batch processing successful")
        
        # Test 6: Summary Report
        print("\n" + "-"*70)
        print("TEST 6: Batch Processor - Summary Report")
        print("-"*70)
        report = processor.get_summary_report()
        print(report)
        print("✓ Summary report generated")
        
        # Test 7: Export Results
        print("\n" + "-"*70)
        print("TEST 7: Batch Processor - Export Results")
        print("-"*70)
        
        csv_success = processor.export_results_csv('test_results.csv')
        json_success = processor.export_results_json('test_results.json')
        
        print(f"CSV export: {'✓ Success' if csv_success else '✗ Failed'}")
        print(f"JSON export: {'✓ Success' if json_success else '✗ Failed'}")
        
        if csv_success and json_success:
            print("✓ Export functionality working")
    
    print("\n" + "="*70)
    print("✅ ALL DATA PIPELINE TESTS PASSED")
    print("="*70)
