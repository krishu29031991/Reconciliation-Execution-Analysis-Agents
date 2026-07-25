import os
import json
from typing import List, Dict
from datetime import datetime
from pathlib import Path

class Reporter:
    """Generates comprehensive validation reports."""
    
    def __init__(self, output_dir: str = './output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_markdown_report(self, results: List[Dict]) -> str:
        """Generate a markdown report for PR comments."""
        summary = self._get_summary(results)
        
        lines = [
            "## 🤖 ETL Reconciliation Report",
            "",
            f"**Status:** {summary['status']}",
            f"**Total Scenarios:** {summary['total_scenarios']}",
            f"**Passed:** {summary['passed']} ({summary['pass_rate']:.1f}%)",
            f"**Failed:** {summary['failed']}",
            f"**Critical Failures:** {summary['critical_failures']}",
            "",
            "### Detailed Results",
            "| Test | Severity | Status | Source | Target | Message |",
            "|------|----------|--------|--------|--------|---------|"
        ]
        
        for r in results:
            status = "✅ PASS" if r.get('passed') else "❌ FAIL"
            lines.append(
                f"| {r.get('test_name', 'Unknown')} | {r.get('severity', 'medium')} | "
                f"{status} | {r.get('source_value', 'N/A')} | {r.get('target_value', 'N/A')} | "
                f"{r.get('message', '')[:30]}... |"
            )
        
        lines.append("")
        lines.append(f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*")
        
        return "\n".join(lines)
    
    def generate_json_report(self, results: List[Dict]) -> str:
        """Generate a JSON report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': self._get_summary(results),
            'results': results
        }
        
        output_path = self.output_dir / 'reconciliation_report.json'
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(output_path)
    
    def _get_summary(self, results: List[Dict]) -> Dict:
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
