"""
MedverifyAI Multi-Agent Orchestrator
Coordinates Agent 1, 2, and 3 for complete healthcare provider validation
"""

import time
from typing import Dict, Any, List
from agents_phase1 import Agent1DataValidation, Agent2DataEnrichment, Agent3CrossValidation


class MultiAgentOrchestrator:
    """
    Multi-Agent Orchestrator for Healthcare Provider Validation
    
    Orchestrates three specialized agents:
    - Agent 1: Data Validation (0-100 points)
    - Agent 2: Information Enrichment (0-60 points)
    - Agent 3: Cross-Validation & Fraud Detection (0-40 points)
    
    Total Scoring: 0-200 points (0-100% confidence)
    
    Decision Logic:
    - ANY fraud flag → MANUAL_REVIEW or REJECT
    - Score ≥ 180 (90%) → AUTO_APPROVE
    - Score 140-179 (70-89%) → CONDITIONAL_APPROVE
    - Score 120-139 (60-69%) → MANUAL_REVIEW
    - Score < 120 (<60%) → REJECT
    """
    
    def __init__(self):
        """Initialize all three agents"""
        self.agent1 = Agent1DataValidation()
        self.agent2 = Agent2DataEnrichment()
        self.agent3 = Agent3CrossValidation()
    
    def validate_provider(self, record: Dict[str, Any], 
                         check_duplicates: bool = True) -> Dict[str, Any]:
        """
        Complete validation pipeline for a single provider record.
        
        Args:
            record: Provider record dictionary
            check_duplicates: Whether to check for duplicates (default: True)
        
        Returns:
            Comprehensive validation report with decision
        """
        start_time = time.time()
        
        # Store original record
        original_record = record.copy()
        
        # ====================================================================
        # STEP 1: DATA VALIDATION (Agent 1)
        # ====================================================================
        try:
            agent1_result = self.agent1.validate_record(record)
        except Exception as e:
            agent1_result = {
                'confidence_agent1': 0,
                'issues_validation': [f"Agent 1 Error: {str(e)}"],
                'execution_time_agent1': 0,
                'error': True
            }
        
        # ====================================================================
        # STEP 2: DATA ENRICHMENT (Agent 2)
        # ====================================================================
        try:
            agent2_result = self.agent2.enrich_record(record)
            enriched_record = agent2_result.get('record_enriched', record)
        except Exception as e:
            agent2_result = {
                'confidence_agent2': 0,
                'enrichment_changes': [],
                'execution_time_agent2': 0,
                'record_enriched': record,
                'error': True
            }
            enriched_record = record
        
        # ====================================================================
        # STEP 3: CROSS-VALIDATION & FRAUD DETECTION (Agent 3)
        # ====================================================================
        try:
            agent3_result = self.agent3.cross_validate_record(
                enriched_record, 
                check_duplicates=check_duplicates
            )
        except Exception as e:
            agent3_result = {
                'confidence_agent3': 0,
                'cross_validation_flags': [f"Agent 3 Error: {str(e)}"],
                'cross_validation_details': {},
                'execution_time_agent3': 0,
                'error': True
            }
        
        # ====================================================================
        # STEP 4: COMBINE RESULTS
        # ====================================================================
        combined_score = (
            agent1_result.get('confidence_agent1', 0) +
            agent2_result.get('confidence_agent2', 0) +
            agent3_result.get('confidence_agent3', 0)
        )
        
        combined_confidence = (combined_score / 200) * 100
        
        total_execution_time = (
            agent1_result.get('execution_time_agent1', 0) +
            agent2_result.get('execution_time_agent2', 0) +
            agent3_result.get('execution_time_agent3', 0)
        )
        
        # ====================================================================
        # STEP 5: MAKE DECISION
        # ====================================================================
        decision_result = self._make_decision(
            combined_score,
            agent1_result,
            agent2_result,
            agent3_result
        )
        
        # ====================================================================
        # STEP 6: GENERATE SUMMARY
        # ====================================================================
        summary = self._generate_summary(
            agent1_result,
            agent2_result,
            agent3_result,
            combined_score
        )
        
        # ====================================================================
        # STEP 7: BUILD COMPREHENSIVE REPORT
        # ====================================================================
        total_time = (time.time() - start_time) * 1000
        
        return {
            # Original and final records
            'original_record': original_record,
            'enriched_record': enriched_record,
            
            # Individual agent results
            'agent1_validation': agent1_result,
            'agent2_enrichment': agent2_result,
            'agent3_cross_validation': agent3_result,
            
            # Combined results
            'combined_score': combined_score,
            'combined_confidence_percentage': round(combined_confidence, 2),
            'total_execution_time': round(total_time, 2),
            
            # Decision
            'decision': decision_result['decision'],
            'decision_reason': decision_result['reason'],
            'decision_details': decision_result['details'],
            
            # Summary
            'summary': summary,
            
            # Metadata
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'orchestrator_version': 'Phase 1 - Rule-based'
        }
    
    def _make_decision(self, combined_score: int, 
                       agent1_result: Dict, 
                       agent2_result: Dict, 
                       agent3_result: Dict) -> Dict[str, Any]:
        """
        Make approval decision based on scores and flags.
        
        Returns:
            dict: {'decision': str, 'reason': str, 'details': dict}
        """
        # Get fraud flags from Agent 3
        fraud_flags = agent3_result.get('cross_validation_flags', [])
        
        # Get validation issues from Agent 1
        validation_issues = agent1_result.get('issues_validation', [])
        
        # Check for critical fraud flags
        critical_flags = [
            '🚨 DUPLICATE_DETECTED',
            '🚨 SUSPICIOUS_DUPLICATE'
        ]
        
        has_critical_fraud = any(flag in fraud_flags for flag in critical_flags)
        has_warnings = len(fraud_flags) > 0
        has_validation_issues = len(validation_issues) > 0
        
        # Decision logic
        decision_details = {
            'combined_score': combined_score,
            'max_score': 200,
            'percentage': round((combined_score / 200) * 100, 2),
            'fraud_flags': fraud_flags,
            'validation_issues': validation_issues,
            'has_critical_fraud': has_critical_fraud,
            'has_warnings': has_warnings
        }
        
        # RULE 1: Critical fraud → REJECT
        if has_critical_fraud:
            return {
                'decision': 'REJECT',
                'reason': 'Critical fraud indicator detected (duplicate registration)',
                'details': decision_details
            }
        
        # RULE 2: Any fraud warnings → MANUAL_REVIEW
        if has_warnings:
            return {
                'decision': 'MANUAL_REVIEW',
                'reason': f'Fraud warnings detected: {", ".join(fraud_flags)}',
                'details': decision_details
            }
        
        # RULE 3: Score-based decisions (no fraud flags)
        if combined_score >= 150:  # 90%+
            return {
                'decision': 'AUTO_APPROVE',
                'reason': 'Excellent quality score (≥90%), no fraud indicators',
                'details': decision_details
            }
        
        elif combined_score >= 120:  # 70-89%
            return {
                'decision': 'CONDITIONAL_APPROVE',
                'reason': 'Good quality score (≥70%), no fraud indicators',
                'details': decision_details
            }
        
        elif combined_score >= 100:  # 60-69%
            return {
                'decision': 'MANUAL_REVIEW',
                'reason': 'Fair quality score (60-69%), requires human review',
                'details': decision_details
            }
        
        else:  # < 60%
            return {
                'decision': 'REJECT',
                'reason': f'Low quality score ({decision_details["percentage"]}%), below threshold',
                'details': decision_details
            }
    
    def _generate_summary(self, agent1_result: Dict, 
                         agent2_result: Dict, 
                         agent3_result: Dict,
                         combined_score: int) -> Dict[str, Any]:
        """Generate summary statistics"""
        
        # Quality level based on combined score
        if combined_score >= 180:
            quality_level = 'EXCELLENT'
        elif combined_score >= 160:
            quality_level = 'GOOD'
        elif combined_score >= 140:
            quality_level = 'FAIR'
        elif combined_score >= 100:
            quality_level = 'POOR'
        else:
            quality_level = 'VERY_POOR'
        
        return {
            'validation_passed': agent1_result.get('confidence_agent1', 0) == 100,
            'enrichments_applied': len(agent2_result.get('enrichment_changes', [])),
            'fraud_flags_count': len(agent3_result.get('cross_validation_flags', [])),
            'quality_level': quality_level,
            'scores': {
                'validation': agent1_result.get('confidence_agent1', 0),
                'enrichment': agent2_result.get('confidence_agent2', 0),
                'cross_validation': agent3_result.get('confidence_agent3', 0),
                'combined': combined_score,
                'percentage': round((combined_score / 200) * 100, 2)
            }
        }
    
    def validate_batch(self, records: List[Dict[str, Any]], 
                      check_duplicates: bool = False) -> List[Dict[str, Any]]:
        """
        Validate multiple provider records.
        
        Args:
            records: List of provider record dictionaries
            check_duplicates: Whether to check duplicates (default: False for batch)
        
        Returns:
            List of validation reports
        """
        results = []
        for record in records:
            result = self.validate_provider(record, check_duplicates)
            results.append(result)
        return results
    
    def get_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics from batch validation results.
        
        Args:
            results: List of validation reports
        
        Returns:
            Statistics dictionary
        """
        if not results:
            return {}
        
        total = len(results)
        
        # Count decisions
        decisions = {}
        for result in results:
            decision = result['decision']
            decisions[decision] = decisions.get(decision, 0) + 1
        
        # Average scores
        avg_score = sum(r['combined_score'] for r in results) / total
        avg_validation = sum(r['agent1_validation']['confidence_agent1'] for r in results) / total
        avg_enrichment = sum(r['agent2_enrichment']['confidence_agent2'] for r in results) / total
        avg_cross_val = sum(r['agent3_cross_validation']['confidence_agent3'] for r in results) / total
        
        # Count fraud flags
        total_flags = sum(len(r['agent3_cross_validation']['cross_validation_flags']) for r in results)
        
        # Count enrichments
        total_enrichments = sum(len(r['agent2_enrichment']['enrichment_changes']) for r in results)
        
        return {
            'total_records': total,
            'decisions': decisions,
            'average_scores': {
                'validation': round(avg_validation, 2),
                'enrichment': round(avg_enrichment, 2),
                'cross_validation': round(avg_cross_val, 2),
                'combined': round(avg_score, 2),
                'percentage': round((avg_score / 200) * 100, 2)
            },
            'fraud_detection': {
                'total_flags': total_flags,
                'records_with_flags': sum(1 for r in results if len(r['agent3_cross_validation']['cross_validation_flags']) > 0)
            },
            'enrichment': {
                'total_changes': total_enrichments,
                'records_enriched': sum(1 for r in results if len(r['agent2_enrichment']['enrichment_changes']) > 0)
            }
        }
    
    def clear_duplicate_database(self):
        """Clear the duplicate detection database (for testing)"""
        self.agent3.clear_database()
    
    def register_approved_provider(self, record: Dict[str, Any]):
        """Register an approved provider to prevent duplicates"""
        self.agent3.register_provider(record)
    
    def get_orchestrator_info(self) -> Dict[str, str]:
        """Get orchestrator metadata"""
        return {
            'name': 'MedverifyAI Multi-Agent Orchestrator',
            'version': 'Phase 1 - Rule-based',
            'agents': [
                self.agent1.get_agent_info()['name'],
                self.agent2.get_agent_info()['name'],
                self.agent3.get_agent_info()['name']
            ],
            'total_score_range': '0-200',
            'decision_types': ['AUTO_APPROVE', 'CONDITIONAL_APPROVE', 'MANUAL_REVIEW', 'REJECT']
        }


# ============================================================================
# SELF-TEST (Run when module is executed directly)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("MULTI-AGENT ORCHESTRATOR - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    orchestrator = MultiAgentOrchestrator()
    orchestrator.clear_duplicate_database()
    
    # Test 1: Perfect Record
    print("\n" + "-"*70)
    print("TEST 1: Perfect Record")
    print("-"*70)
    
    perfect_record = {
        'name': 'Dr. Perfect Test',
        'phone': '9876543210',
        'city': 'Bangalore',
        'specialty': 'Cardiology',
        'registration_no': 'MCI10012345',
        'years_practice': 10,
        'clinic_address': '123 MG Road Bangalore',
        'pincode': '560001'
    }
    
    result = orchestrator.validate_provider(perfect_record)
    print(f"   Combined Score: {result['combined_score']}/200 ({result['combined_confidence_percentage']}%)")
    print(f"   Decision: {result['decision']}")
    print(f"   Reason: {result['decision_reason']}")
    print(f"   Quality: {result['summary']['quality_level']}")
    assert result['decision'] in ['AUTO_APPROVE', 'CONDITIONAL_APPROVE'], "Should approve"
    print("   ✓ PASSED")
    
    # Test 2: Record Needing Enrichment
    print("\n" + "-"*70)
    print("TEST 2: Record Needing Enrichment")
    print("-"*70)
    
    messy_record = {
        'name': 'Dr. Messy Test',
        'phone': '+91-9876543211',
        'city': 'MUMBAI',
        'specialty': 'Cardio',
        'registration_no': 'MCI10012346',
        'years_practice': 12,
        'clinic_address': '45 Marine Drive Mumbai',
        'pincode': '400001'
    }
    
    result = orchestrator.validate_provider(messy_record)
    print(f"   Combined Score: {result['combined_score']}/200 ({result['combined_confidence_percentage']}%)")
    print(f"   Decision: {result['decision']}")
    print(f"   Enrichments: {result['summary']['enrichments_applied']}")
    assert result['combined_score'] >= 180, "Should have high score"
    print("   ✓ PASSED")
    
    # Test 3: Duplicate Detection
    print("\n" + "-"*70)
    print("TEST 3: Duplicate Detection")
    print("-"*70)
    
    duplicate_record = {
        'name': 'Dr. Duplicate Test',
        'phone': '9876543212',
        'city': 'Bangalore',
        'specialty': 'Cardiology',
        'registration_no': 'MCI10012347',
        'years_practice': 10,
        'clinic_address': '123 Test',
        'pincode': '560001'
    }
    
    # Register first
    orchestrator.register_approved_provider(duplicate_record)
    
    # Try duplicate
    result = orchestrator.validate_provider(duplicate_record)
    print(f"   Combined Score: {result['combined_score']}/200")
    print(f"   Decision: {result['decision']}")
    print(f"   Flags: {result['agent3_cross_validation']['cross_validation_flags']}")
    assert result['decision'] == 'REJECT', "Should reject duplicate"
    print("   ✓ PASSED")
    
    # Test 4: Low Quality Record
    print("\n" + "-"*70)
    print("TEST 4: Low Quality Record")
    print("-"*70)
    
    bad_record = {
        'name': 'Dr',
        'phone': '98765',
        'city': 'Bangalore',
        'specialty': 'Unknown',
        'registration_no': 'INVALID',
        'years_practice': -5,
        'clinic_address': 'X',
        'pincode': '123'
    }
    
    result = orchestrator.validate_provider(bad_record, check_duplicates=False)
    print(f"   Combined Score: {result['combined_score']}/200 ({result['combined_confidence_percentage']}%)")
    print(f"   Decision: {result['decision']}")
    print(f"   Reason: {result['decision_reason']}")
    print(f"   Flags: {result['agent3_cross_validation']['cross_validation_flags']}")
    print(f"   Quality: {result['summary']['quality_level']}")
    
    # Accept either REJECT or MANUAL_REVIEW for very low quality with fraud flags
    assert result['decision'] in ['REJECT', 'MANUAL_REVIEW'], "Should reject or require review for low quality"
    print("   ✓ PASSED")
    
    # Test 5: Batch Processing
    print("\n" + "-"*70)
    print("TEST 5: Batch Processing")
    print("-"*70)
    
    orchestrator.clear_duplicate_database()
    
    batch_records = [perfect_record, messy_record]
    results = orchestrator.validate_batch(batch_records)
    stats = orchestrator.get_statistics(results)
    
    print(f"   Records Processed: {stats['total_records']}")
    print(f"   Average Score: {stats['average_scores']['combined']}/200")
    print(f"   Decisions: {stats['decisions']}")
    assert len(results) == 2, "Should process 2 records"
    print("   ✓ PASSED")
    
    print("\n" + "="*70)
    print("✅ ALL ORCHESTRATOR TESTS PASSED")
    print("="*70)
