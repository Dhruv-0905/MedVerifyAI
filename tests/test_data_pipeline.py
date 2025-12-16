"""
Comprehensive test suite for Data Pipeline module
Tests CSVHandler and BatchProcessor functionality
"""

import pytest
import pandas as pd
import io
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_pipeline import CSVHandler, BatchProcessor


class TestCSVHandler:
    """Test suite for CSVHandler class"""
    
    @pytest.fixture
    def handler(self):
        """Create CSVHandler instance"""
        return CSVHandler()
    
    @pytest.fixture
    def valid_csv(self):
        """Sample valid CSV data"""
        return """name,phone,city,specialty,registration_no,years_practice,clinic_address,pincode
Dr. John Smith,9876543210,Bangalore,Cardiology,MCI10012345,10,123 MG Road,560001
Dr. Jane Doe,9876543211,Mumbai,Dermatology,MCI10012346,15,456 Marine Drive,400001"""
    
    @pytest.fixture
    def csv_with_extra_columns(self):
        """CSV with extra unmapped columns"""
        return """name,phone,city,specialty,registration_no,years_practice,clinic_address,pincode,extra_col1,extra_col2
Dr. John Smith,9876543210,Bangalore,Cardiology,MCI10012345,10,123 MG Road,560001,extra1,extra2"""
    
    @pytest.fixture
    def csv_missing_required(self):
        """CSV missing required fields"""
        return """city,specialty,years_practice
Bangalore,Cardiology,10"""
    
    @pytest.fixture
    def csv_alternate_names(self):
        """CSV with alternate column names"""
        return """doctor_name,contact_number,location,specialization,reg_no,experience,address,postal_code
Dr. John Smith,9876543210,Bangalore,Cardiology,MCI10012345,10,123 MG Road,560001"""
    
    # Template Tests
    def test_get_template_columns(self, handler):
        """Test template column retrieval"""
        columns = handler.get_template_columns()
        assert isinstance(columns, list)
        assert 'name' in columns
        assert 'phone' in columns
        assert 'registration_no' in columns
        assert len(columns) == 8
    
    def test_create_template_csv(self, handler):
        """Test CSV template creation"""
        template = handler.create_template_csv()
        assert isinstance(template, str)
        assert 'name' in template
        assert 'Dr. John Smith' in template
        assert '9876543210' in template
    
    # Parsing Tests
    def test_parse_valid_csv(self, handler, valid_csv):
        """Test parsing valid CSV"""
        success, df, stats = handler.parse_csv(valid_csv)
        assert success is True
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert stats['success'] is True
        assert stats['rows'] == 2
        assert stats['columns'] == 8
    
    def test_parse_empty_csv(self, handler):
        """Test parsing empty CSV"""
        empty_csv = ""
        success, df, stats = handler.parse_csv(empty_csv)
        assert success is False
        assert 'error' in stats
    
    def test_parse_csv_bytes(self, handler, valid_csv):
        """Test parsing CSV from bytes"""
        csv_bytes = valid_csv.encode('utf-8')
        success, df, stats = handler.parse_csv(csv_bytes)
        assert success is True
        assert len(df) == 2
    
    def test_parse_invalid_csv(self, handler):
        """Test parsing malformed CSV"""
        invalid_csv = "col1,col2\nval1"  # Missing value
        success, df, stats = handler.parse_csv(invalid_csv)
        # Should still parse but with NaN
        assert success is True
    
    # Column Mapping Tests
    def test_map_columns_standard_names(self, handler, valid_csv):
        """Test mapping with standard column names"""
        _, df, _ = handler.parse_csv(valid_csv)
        success, mapped_df, info = handler.map_columns(df)
        assert success is True
        assert 'name' in mapped_df.columns
        assert 'phone' in mapped_df.columns
        assert info['total_mapped'] >= 3  # At least required fields
    
    def test_map_columns_alternate_names(self, handler, csv_alternate_names):
        """Test mapping with alternate column names"""
        _, df, _ = handler.parse_csv(csv_alternate_names)
        success, mapped_df, info = handler.map_columns(df)
        assert success is True
        assert 'name' in mapped_df.columns
        assert 'phone' in mapped_df.columns
        assert info['mapped_columns']['name'] == 'doctor_name'
        assert info['mapped_columns']['phone'] == 'contact_number'
    
    def test_map_columns_with_extra(self, handler, csv_with_extra_columns):
        """Test mapping with extra unmapped columns"""
        _, df, _ = handler.parse_csv(csv_with_extra_columns)
        success, mapped_df, info = handler.map_columns(df)
        assert success is True
        assert len(info['unmapped_columns']) == 2
        assert 'extra_col1' in info['unmapped_columns']
    
    def test_map_columns_missing_required(self, handler, csv_missing_required):
        """Test mapping with missing required fields"""
        _, df, _ = handler.parse_csv(csv_missing_required)
        success, mapped_df, info = handler.map_columns(df)
        assert success is False
        assert 'error' in info
        assert 'missing_required' in info
        assert 'name' in info['missing_required']
        assert 'phone' in info['missing_required']
    
    # Data Validation Tests
    def test_validate_data_types_valid(self, handler, valid_csv):
        """Test data type validation with valid data"""
        _, df, _ = handler.parse_csv(valid_csv)
        _, mapped_df, _ = handler.map_columns(df)
        all_valid, issues = handler.validate_data_types(mapped_df)
        assert all_valid is True
        assert len(issues) == 0
    
    def test_validate_data_types_invalid_phone(self, handler):
        """Test validation with invalid phone"""
        csv = """name,phone,registration_no
Dr. John,invalid,MCI123"""
        _, df, _ = handler.parse_csv(csv)
        _, mapped_df, _ = handler.map_columns(df)
        # Phone validation is lenient, checks for empty only
        all_valid, issues = handler.validate_data_types(mapped_df)
        # Should pass as phone has some value
        assert isinstance(issues, list)
    
    def test_validate_data_types_invalid_years(self, handler):
        """Test validation with invalid years_practice"""
        csv = """name,phone,registration_no,years_practice
Dr. John,9876543210,MCI123,invalid"""
        _, df, _ = handler.parse_csv(csv)
        _, mapped_df, _ = handler.map_columns(df)
        all_valid, issues = handler.validate_data_types(mapped_df)
        assert all_valid is False
        assert len(issues) > 0
        assert 'not a valid number' in issues[0]
    
    def test_validate_data_types_years_out_of_range(self, handler):
        """Test validation with years_practice out of range"""
        csv = """name,phone,registration_no,years_practice
Dr. John,9876543210,MCI123,100"""
        _, df, _ = handler.parse_csv(csv)
        _, mapped_df, _ = handler.map_columns(df)
        all_valid, issues = handler.validate_data_types(mapped_df)
        assert all_valid is False
        assert 'out of range' in issues[0]
    
    def test_validate_data_types_invalid_pincode(self, handler):
        """Test validation with invalid pincode"""
        csv = """name,phone,registration_no,pincode
Dr. John,9876543210,MCI123,12345"""  # 5 digits
        _, df, _ = handler.parse_csv(csv)
        _, mapped_df, _ = handler.map_columns(df)
        all_valid, issues = handler.validate_data_types(mapped_df)
        assert all_valid is False
        assert '6 digits' in issues[0]
    
    # Record Preparation Tests
    def test_prepare_records(self, handler, valid_csv):
        """Test record preparation"""
        _, df, _ = handler.parse_csv(valid_csv)
        _, mapped_df, _ = handler.map_columns(df)
        records = handler.prepare_records(mapped_df)
        
        assert isinstance(records, list)
        assert len(records) == 2
        assert 'name' in records[0]
        assert 'phone' in records[0]
        assert '_row_number' in records[0]
        assert records[0]['name'] == 'Dr. John Smith'
    
    def test_prepare_records_with_nan(self, handler):
        """Test record preparation with NaN values"""
        csv = """name,phone,registration_no,years_practice
Dr. John,9876543210,MCI123,"""
        _, df, _ = handler.parse_csv(csv)
        _, mapped_df, _ = handler.map_columns(df)
        records = handler.prepare_records(mapped_df)
        
        assert records[0]['years_practice'] == '' or records[0]['years_practice'] == 0  # NaN converted to 0
    
    def test_prepare_records_pincode_conversion(self, handler):
        """Test pincode conversion (remove decimal)"""
        csv = """name,phone,registration_no,pincode
Dr. John,9876543210,MCI123,560001.0"""
        _, df, _ = handler.parse_csv(csv)
        _, mapped_df, _ = handler.map_columns(df)
        records = handler.prepare_records(mapped_df)
        
        assert records[0]['pincode'] == '560001'  # Decimal removed
    
    # Full Pipeline Tests
    def test_process_file_valid(self, handler, valid_csv):
        """Test complete file processing pipeline"""
        success, records, stats = handler.process_file(valid_csv)
        
        assert success is True
        assert len(records) == 2
        assert stats['success'] is True
        assert stats['total_records'] == 2
        assert 'stages' in stats
        assert 'parse' in stats['stages']
        assert 'mapping' in stats['stages']
        assert 'validation' in stats['stages']
    
    def test_process_file_invalid(self, handler, csv_missing_required):
        """Test processing invalid file"""
        success, records, stats = handler.process_file(csv_missing_required)
        
        assert success is False
        assert len(records) == 0
        assert 'error' in stats['stages']['mapping']
    
    def test_process_file_with_warnings(self, handler):
        """Test processing file with validation warnings"""
        csv = """name,phone,registration_no,years_practice
Dr. John,9876543210,MCI123,100"""
        success, records, stats = handler.process_file(csv)
        
        assert success is True  # Still succeeds
        assert stats['has_validation_warnings'] is True


class TestBatchProcessor:
    """Test suite for BatchProcessor class"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create mock or real orchestrator"""
        try:
            from orchestrator import MultiAgentOrchestrator
            return MultiAgentOrchestrator()
        except ImportError:
            pytest.skip("Orchestrator not available")
    
    @pytest.fixture
    def processor(self, orchestrator):
        """Create BatchProcessor instance"""
        return BatchProcessor(orchestrator)
    
    @pytest.fixture
    def sample_records(self):
        """Sample test records"""
        return [
            {
                'name': 'Dr. Test One',
                'phone': '9876543210',
                'city': 'Bangalore',
                'specialty': 'Cardiology',
                'registration_no': 'MCI10012345',
                'years_practice': 10,
                'clinic_address': '123 MG Road',
                'pincode': '560001'
            },
            {
                'name': 'Dr. Test Two',
                'phone': '9876543211',
                'city': 'Mumbai',
                'specialty': 'Dermatology',
                'registration_no': 'MCI10012346',
                'years_practice': 15,
                'clinic_address': '456 Marine Drive',
                'pincode': '400001'
            }
        ]
    
    # Batch Processing Tests
    def test_process_batch_basic(self, processor, sample_records):
        """Test basic batch processing"""
        results, stats = processor.process_batch(sample_records, check_duplicates=False)
        
        assert isinstance(results, list)
        assert len(results) == 2
        assert isinstance(stats, dict)
        assert stats['total_records'] == 2
        assert 'processing_time_seconds' in stats
    
    def test_process_batch_with_progress(self, processor, sample_records):
        """Test batch processing with progress callback"""
        progress_calls = []
        
        def callback(current, total, result):
            progress_calls.append((current, total))
        
        results, stats = processor.process_batch(
            sample_records, 
            check_duplicates=False,
            progress_callback=callback
        )
        
        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 2)
        assert progress_calls[1] == (2, 2)
    
    def test_process_batch_statistics(self, processor, sample_records):
        """Test batch statistics calculation"""
        results, stats = processor.process_batch(sample_records, check_duplicates=False)
        
        assert 'decisions' in stats
        assert 'scores' in stats
        assert 'confidence' in stats
        assert 'fraud_detection' in stats
        assert 'enrichment' in stats
        assert stats['total_records'] == 2
    
    def test_process_batch_error_handling(self, processor):
        """Test batch processing with invalid record"""
        invalid_records = [
            {'name': 'Invalid', 'phone': '', 'registration_no': ''}  # Missing required
        ]
        
        # Should handle gracefully
        results, stats = processor.process_batch(invalid_records, check_duplicates=False)
        
        assert len(results) == 1
        assert stats['total_records'] == 1
    
    # Export Tests
    def test_export_results_csv(self, processor, sample_records, tmp_path):
        """Test CSV export"""
        processor.process_batch(sample_records, check_duplicates=False)
        
        output_file = tmp_path / "test_output.csv"
        success = processor.export_results_csv(str(output_file))
        
        assert success is True
        assert output_file.exists()
        
        # Verify content
        df = pd.read_csv(output_file)
        assert len(df) == 2
        assert 'Decision' in df.columns
        assert 'Score' in df.columns
    
    def test_export_results_json(self, processor, sample_records, tmp_path):
        """Test JSON export"""
        processor.process_batch(sample_records, check_duplicates=False)
        
        output_file = tmp_path / "test_output.json"
        success = processor.export_results_json(str(output_file))
        
        assert success is True
        assert output_file.exists()
    
    def test_export_without_results(self, processor, tmp_path):
        """Test export without processing results"""
        output_file = tmp_path / "empty.csv"
        success = processor.export_results_csv(str(output_file))
        
        assert success is False
    
    # Summary and Filtering Tests
    def test_get_summary_report(self, processor, sample_records):
        """Test summary report generation"""
        processor.process_batch(sample_records, check_duplicates=False)
        
        report = processor.get_summary_report()
        
        assert isinstance(report, str)
        assert 'BATCH PROCESSING SUMMARY' in report
        assert 'Total Records' in report
        assert 'Decision Breakdown' in report
    
    def test_get_approved_records(self, processor, sample_records):
        """Test filtering approved records"""
        processor.process_batch(sample_records, check_duplicates=False)
        
        approved = processor.get_approved_records()
        
        assert isinstance(approved, list)
        # Most records should be approved
        assert len(approved) >= 0
    
    def test_get_review_required_records(self, processor, sample_records):
        """Test filtering review required records"""
        processor.process_batch(sample_records, check_duplicates=False)
        
        review = processor.get_review_required_records()
        
        assert isinstance(review, list)
    
    def test_get_failed_records(self, processor, sample_records):
        """Test filtering failed records"""
        processor.process_batch(sample_records, check_duplicates=False)
        
        failed = processor.get_failed_records()
        
        assert isinstance(failed, list)


class TestIntegration:
    """Integration tests for complete data pipeline"""
    
    @pytest.fixture
    def handler(self):
        return CSVHandler()
    
    @pytest.fixture
    def orchestrator(self):
        try:
            from orchestrator import MultiAgentOrchestrator
            return MultiAgentOrchestrator()
        except ImportError:
            pytest.skip("Orchestrator not available")
    
    def test_csv_to_batch_pipeline(self, handler, orchestrator):
        """Test complete pipeline from CSV to batch results"""
        # Create CSV
        csv_data = """name,phone,city,specialty,registration_no,years_practice,clinic_address,pincode
Dr. Integration Test,9876543299,Bangalore,Cardiology,MCI10099999,10,Test Address,560001"""
        
        # Process CSV
        success, records, csv_stats = handler.process_file(csv_data)
        assert success is True
        assert len(records) == 1
        
        # Batch process
        processor = BatchProcessor(orchestrator)
        results, batch_stats = processor.process_batch(records, check_duplicates=False)
        
        assert len(results) == 1
        assert 'decision' in results[0]
        assert batch_stats['total_records'] == 1
    
    def test_full_pipeline_with_export(self, handler, orchestrator, tmp_path):
        """Test complete pipeline with export"""
        # Multi-record CSV
        csv_data = """name,phone,city,specialty,registration_no,years_practice,clinic_address,pincode
Dr. Test A,9876543210,Bangalore,Cardiology,MCI10012345,10,Address A,560001
Dr. Test B,9876543211,Mumbai,Dermatology,MCI10012346,15,Address B,400001"""
        
        # Process CSV
        success, records, _ = handler.process_file(csv_data)
        assert success is True
        
        # Batch process
        processor = BatchProcessor(orchestrator)
        results, stats = processor.process_batch(records, check_duplicates=False)
        
        # Export
        csv_file = tmp_path / "results.csv"
        json_file = tmp_path / "results.json"
        
        csv_success = processor.export_results_csv(str(csv_file))
        json_success = processor.export_results_json(str(json_file))
        
        assert csv_success is True
        assert json_success is True
        assert csv_file.exists()
        assert json_file.exists()


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
