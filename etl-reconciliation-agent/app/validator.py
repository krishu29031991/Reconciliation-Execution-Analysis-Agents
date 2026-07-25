import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime

class Validator:
    """Executes validation scenarios against data sources."""
    
    def __init__(self, project_id: str = "", credentials_path: str = ""):
        self.project_id = project_id
        self.credentials_path = credentials_path
    
    def execute_scenario(self, scenario: Dict) -> Dict:
        """Execute a single validation scenario."""
        test_name = list(scenario.keys())[0]
        test_config = scenario[test_name]
        
        source_query = test_config.get('source', {}).get('query', '')
        target_query = test_config.get('target', {}).get('query', '')
        severity = test_config.get('severity', 'medium')
        
        # Simulate execution (replace with actual BigQuery calls)
        source_value = self._simulate_query(source_query)
        target_value = self._simulate_query(target_query)
        
        passed, message = self._evaluate_comparison(
            source_value, target_value,
            test_config.get('comparisons', {})
        )
        
        return {
            'test_name': test_name,
            'severity': severity,
            'source_value': source_value,
            'target_value': target_value,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def _simulate_query(self, query: str) -> float:
        """Simulate query execution for testing."""
        # In production, this would execute against BigQuery
        import random
        base_value = 1000
        if 'COUNT(*)' in query:
            return base_value + random.randint(-10, 10)
        elif 'SUM(' in query:
            return 50000 + random.randint(-1000, 1000)
        elif 'AVG(' in query:
            return 50 + random.randint(-5, 5)
        elif 'MIN(' in query:
            return 1 + random.randint(0, 5)
        elif 'MAX(' in query:
            return 100 + random.randint(-5, 5)
        elif 'DISTINCT' in query:
            return 100 + random.randint(-10, 10)
        return 0.0
    
    def _evaluate_comparison(self, source_val, target_val, comparisons: Dict) -> tuple:
        """Evaluate if source and target values match within tolerance."""
        if source_val is None and target_val is None:
            return True, "Both NULL"
        
        if source_val is None:
            return False, f"Source NULL, Target {target_val}"
        
        if target_val is None:
            return False, f"Target NULL, Source {source_val}"
        
        if source_val == target_val:
            return True, f"Exact match: {source_val}"
        
        threshold = comparisons.get('threshold', {})
        if threshold.get('value') == 'percentage':
            limit = threshold.get('limit', 5.0)
            diff_pct = abs(source_val - target_val) / abs(source_val) * 100
            if diff_pct <= limit:
                return True, f"Within {limit}% (diff: {diff_pct:.2f}%)"
            return False, f"Exceeds {limit}% (diff: {diff_pct:.2f}%)"
        
        return False, f"Mismatch: {source_val} vs {target_val}"
    
    def execute_suite(self, test_suite: List[Dict]) -> List[Dict]:
        """Execute a full test suite."""
        results = []
        for scenario in test_suite:
            result = self.execute_scenario(scenario)
            results.append(result)
        return results
    
    def get_summary(self, results: List[Dict]) -> Dict:
        """Get summary statistics from results."""
        total = len(results)
        passed = sum(1 for r in results if r.get('passed', False))
        failed = total - passed
        critical_failed = sum(1 for r in results 
                            if not r.get('passed', True) and r.get('severity') == 'critical')
        
        return {
            'total_scenarios': total,
            'passed': passed,
            'failed': failed,
            'critical_failures': critical_failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'status': 'FAIL' if critical_failed > 0 else ('WARN' if failed > 0 else 'PASS')
        }
