"""
Integration Tests for Multi-Agent Orchestrator
Tests complete validation pipeline with all three agents
"""

import pytest
import sys
sys.path.insert(0, 'src')

from orchestrator import MultiAgentOrchestrator


class TestOrchestratorInitialization:
    """Test orchestrator initialization"""
    
    def test_orchestrator_creation(self):
        """Test creating orchestrator instance"""
        orchestrator = MultiAgentOrchestrator()
        assert orchestrator is not None
        assert orchestrator.agent1 is not None
        assert orchestrator.agent2 is not None
        assert orchestrator.agent3 is not None
    
    def test_orchestrator_info(self):
        """Test getting orchestrator metadata"""
        orchestrator = MultiAgentOrchestrator()
        info = orchestrator.get_orchestrator_info()
        
        assert info['name'] == 'MedverifyAI Multi-Agent Orchestrator'
        assert info['version'] == 'Phase 1 - Rule-based'
        assert len(info['agents']) == 3
        assert info['total_score_range'] == '0-200'
        assert len(info['decision_types']) == 4


class TestOrchestratorDecisions:
    """Test orchestrator decision logic"""
    
    def setup_method(self):
        """Setup before each test"""
        self.orchestrator = MultiAgentOrchestrator()
        self.orchestrator.clear_duplicate_database()
    
    def test_auto_approve_decision(self):
        """Test AUTO_APPROVE decision (score >= 180)"""
        record = {
            'name': 'Dr. Excellent Test',
            'phone': '+91-9876543210',  # Needs normalization
            'city': 'BANGALORE',  # Needs case fix
            'specialty': 'Cardio',  # Needs expansion
            'registration_no': 'MCI10012345',
            'years_practice': 10,
            'clinic_address': '123 MG Road Bangalore',
            'pincode': '560001'
        }
        
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        
        assert result['combined_score'] >= 180
        assert result['decision'] == 'AUTO_APPROVE'
        assert 'fraud' not in result['decision_reason'].lower() or 'no fraud' in result['decision_reason'].lower()
    
    def test_conditional_approve_decision(self):
        """Test CONDITIONAL_APPROVE decision (140-179)"""
        record = {
            'name': 'Dr. Good Test',
            'phone': '9876543211',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012346',
            'years_practice': 12,
            'clinic_address': '123 Test Street',
            'pincode': '560001'
        }
        
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        
        assert 140 <= result['combined_score'] < 180
        assert result['decision'] == 'CONDITIONAL_APPROVE'
    
    def test_manual_review_decision_low_score(self):
        """Test MANUAL_REVIEW decision (120-139)"""
        record = {
            'name': 'Dr. Fair Test',
            'phone': '9876543',  # Invalid but some points
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012347',
            'years_practice': 10,
            'clinic_address': '123 Test',
            'pincode': '560001'
        }
        
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        
        # Should get MANUAL_REVIEW or REJECT
        assert result['decision'] in ['MANUAL_REVIEW', 'REJECT']
    
    def test_reject_decision_low_score(self):
        """Test REJECT decision (score < 120)"""
        record = {
            'name': 'Dr',
            'phone': '123',
            'city': 'X',
            'specialty': 'Unknown',
            'registration_no': 'INVALID',
            'years_practice': -5,
            'clinic_address': 'X',
            'pincode': '123'
        }
        
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        
        # Low score with fraud flags = MANUAL_REVIEW or REJECT
        assert result['decision'] in ['REJECT', 'MANUAL_REVIEW']
        assert result['combined_score'] < 120
    
    def test_reject_decision_duplicate(self):
        """Test REJECT decision on duplicate detection"""
        record = {
            'name': 'Dr. Duplicate Test',
            'phone': '9876543212',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012348',
            'years_practice': 10,
            'clinic_address': '123 Test',
            'pincode': '560001'
        }
        
        # Register first
        self.orchestrator.register_approved_provider(record)
        
        # Try duplicate
        result = self.orchestrator.validate_provider(record)
        
        assert result['decision'] == 'REJECT'
        assert '🚨 DUPLICATE_DETECTED' in result['agent3_cross_validation']['cross_validation_flags']
        assert 'duplicate' in result['decision_reason'].lower()
    
    def test_manual_review_fraud_warnings(self):
        """Test MANUAL_REVIEW on fraud warnings"""
        record = {
            'name': 'Dr. Warning Test',
            'phone': '9876543213',
            'city': 'Mumbai',
            'specialty': 'Cardiology',
            'registration_no': 'DMC10012349',  # Delhi council in Mumbai
            'years_practice': 10,
            'clinic_address': '123 Test',
            'pincode': '400001'
        }
        
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        
        # Should have fraud warning
        assert len(result['agent3_cross_validation']['cross_validation_flags']) > 0
        assert result['decision'] == 'MANUAL_REVIEW'


class TestOrchestratorPipeline:
    """Test complete orchestrator pipeline"""
    
    def setup_method(self):
        """Setup before each test"""
        self.orchestrator = MultiAgentOrchestrator()
        self.orchestrator.clear_duplicate_database()
    
    def test_complete_pipeline_perfect_record(self):
        """Test complete pipeline with perfect record"""
        record = {
            'name': 'Dr. Pipeline Perfect',
            'phone': '9876543214',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012350',
            'years_practice': 10,
            'clinic_address': '123 MG Road Bangalore',
            'pincode': '560001'
        }
        
        result = self.orchestrator.validate_provider(record)
        
        # Check structure
        assert 'original_record' in result
        assert 'enriched_record' in result
        assert 'agent1_validation' in result
        assert 'agent2_enrichment' in result
        assert 'agent3_cross_validation' in result
        assert 'combined_score' in result
        assert 'decision' in result
        assert 'summary' in result
        
        # Check scores
        assert result['agent1_validation']['confidence_agent1'] == 100
        assert result['combined_score'] >= 140
        
        # Check decision
        assert result['decision'] in ['AUTO_APPROVE', 'CONDITIONAL_APPROVE']
    
    def test_complete_pipeline_messy_record(self):
        """Test pipeline with record needing enrichment"""
        record = {
            'name': 'Dr. Pipeline Messy',
            'phone': '+91-9876543215',
            'city': 'CHENNAI',
            'specialty': 'Ortho',
            'registration_no': 'MCI10012351',
            'years_practice': 15,
            'clinic_address': '45 Anna Salai Chennai',
            'pincode': '600002'
        }
        
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        
        # Should have enrichments
        assert len(result['agent2_enrichment']['enrichment_changes']) >= 2
        
        # Should have high score after enrichment
        assert result['combined_score'] >= 180
        assert result['decision'] == 'AUTO_APPROVE'
    
    def test_pipeline_preserves_original_record(self):
        """Test that original record is preserved"""
        record = {
            'name': 'Dr. Original Test',
            'phone': '+91-9876543216',
            'city': 'PUNE',
            'specialty': 'Neuro',
            'registration_no': 'MCI10012352',
            'years_practice': 8,
            'clinic_address': '123 FC Road Pune',
            'pincode': '411004'
        }
        
        original_copy = record.copy()
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        
        # Original should be unchanged
        assert result['original_record'] == original_copy
        
        # Enriched should have changes
        assert result['enriched_record']['phone'] != original_copy['phone']  # Normalized
        assert result['enriched_record']['city'] != original_copy['city']  # Case corrected


class TestOrchestratorBatchProcessing:
    """Test batch processing capabilities"""
    
    def setup_method(self):
        """Setup before each test"""
        self.orchestrator = MultiAgentOrchestrator()
        self.orchestrator.clear_duplicate_database()
    
    def test_batch_validate_multiple_records(self):
        """Test batch validation of multiple records"""
        records = [
            {
                'name': 'Dr. Batch Test 1',
                'phone': '9876543217',
                'city': 'Bangalore',
                'specialty': 'Cardiology',
                'registration_no': 'MCI10012353',
                'years_practice': 10,
                'clinic_address': '123 Test',
                'pincode': '560001'
            },
            {
                'name': 'Dr. Batch Test 2',
                'phone': '9876543218',
                'city': 'Mumbai',
                'specialty': 'Dermatology',
                'registration_no': 'MCI10012354',
                'years_practice': 12,
                'clinic_address': '456 Test',
                'pincode': '400001'
            }
        ]
        
        results = self.orchestrator.validate_batch(records)
        
        assert len(results) == 2
        assert all('decision' in r for r in results)
        assert all('combined_score' in r for r in results)
    
    def test_batch_statistics(self):
        """Test getting statistics from batch results"""
        records = [
            {
                'name': f'Dr. Stats Test {i}',
                'phone': f'987654321{i}',
                'city': 'Bangalore',
                'specialty': 'Cardiology',
                'registration_no': f'MCI1001235{i}',
                'years_practice': 10 + i,
                'clinic_address': '123 Test',
                'pincode': '560001'
            }
            for i in range(5)
        ]
        
        results = self.orchestrator.validate_batch(records)
        stats = self.orchestrator.get_statistics(results)
        
        assert stats['total_records'] == 5
        assert 'decisions' in stats
        assert 'average_scores' in stats
        assert 'fraud_detection' in stats
        assert 'enrichment' in stats
        
        assert stats['average_scores']['combined'] >= 0
        assert stats['average_scores']['percentage'] >= 0


class TestOrchestratorReportGeneration:
    """Test report generation"""
    
    def setup_method(self):
        """Setup before each test"""
        self.orchestrator = MultiAgentOrchestrator()
        self.orchestrator.clear_duplicate_database()
    
    def test_report_structure(self):
        """Test validation report structure"""
        record = {
            'name': 'Dr. Report Test',
            'phone': '9876543220',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012356',
            'years_practice': 10,
            'clinic_address': '123 Test',
            'pincode': '560001'
        }
        
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        
        # Check all required fields
        required_fields = [
            'original_record',
            'enriched_record',
            'agent1_validation',
            'agent2_enrichment',
            'agent3_cross_validation',
            'combined_score',
            'combined_confidence_percentage',
            'total_execution_time',
            'decision',
            'decision_reason',
            'decision_details',
            'summary',
            'timestamp',
            'orchestrator_version'
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_summary_generation(self):
        """Test summary section generation"""
        record = {
            'name': 'Dr. Summary Test',
            'phone': '9876543221',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012357',
            'years_practice': 10,
            'clinic_address': '123 Test',
            'pincode': '560001'
        }
        
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        summary = result['summary']
        
        assert 'validation_passed' in summary
        assert 'enrichments_applied' in summary
        assert 'fraud_flags_count' in summary
        assert 'quality_level' in summary
        assert 'scores' in summary
        
        assert summary['quality_level'] in ['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'VERY_POOR']
    
    def test_decision_details(self):
        """Test decision details generation"""
        record = {
            'name': 'Dr. Decision Test',
            'phone': '9876543222',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012358',
            'years_practice': 10,
            'clinic_address': '123 Test',
            'pincode': '560001'
        }
        
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        details = result['decision_details']
        
        assert 'combined_score' in details
        assert 'max_score' in details
        assert 'percentage' in details
        assert 'fraud_flags' in details
        assert 'validation_issues' in details
        
        assert details['max_score'] == 200
        assert 0 <= details['percentage'] <= 100


class TestOrchestratorPerformance:
    """Test orchestrator performance"""
    
    def setup_method(self):
        """Setup before each test"""
        self.orchestrator = MultiAgentOrchestrator()
        self.orchestrator.clear_duplicate_database()
    
    def test_single_record_performance(self):
        """Test single record validation performance"""
        record = {
            'name': 'Dr. Performance Test',
            'phone': '9876543223',
            'city': 'Bangalore',
            'specialty': 'Cardiology',
            'registration_no': 'MCI10012359',
            'years_practice': 10,
            'clinic_address': '123 Test',
            'pincode': '560001'
        }
        
        result = self.orchestrator.validate_provider(record, check_duplicates=False)
        
        # Should complete in reasonable time
        assert result['total_execution_time'] < 100  # milliseconds
    
    def test_batch_performance(self):
        """Test batch processing performance"""
        import time
        
        records = [
            {
                'name': f'Dr. Batch Perf {i}',
                'phone': f'987654322{i}',
                'city': 'Bangalore',
                'specialty': 'Cardiology',
                'registration_no': f'MCI1001236{i}',
                'years_practice': 10,
                'clinic_address': '123 Test',
                'pincode': '560001'
            }
            for i in range(10)
        ]
        
        start = time.time()
        results = self.orchestrator.validate_batch(records)
        duration = (time.time() - start) * 1000
        
        assert len(results) == 10
        assert duration < 1000  # Should complete in < 1 second


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, '-v'])
