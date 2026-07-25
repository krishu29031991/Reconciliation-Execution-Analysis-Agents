from typing import Dict, List, Optional
from dataclasses import dataclass, field
import yaml
from datetime import datetime

@dataclass
class ValidationScenario:
    name: str
    severity: str  # critical, high, medium, low
    source_query: str
    target_query: str
    comparison_type: str  # exact_match, percentage_threshold, absolute_threshold
    threshold_limit: Optional[float] = None
    source_table: str = ""
    target_table: str = ""

class ScenarioBuilder:
    """Automatically builds validation scenarios from discovered tables."""
    
    def __init__(self, severity_levels: Dict[str, float] = None):
        self.severity_levels = severity_levels or {
            'critical': 0.0,
            'high': 1.0,
            'medium': 5.0,
            'low': 10.0
        }
        self.scenarios = []
    
    def build_row_count_scenario(self, table: str) -> ValidationScenario:
        return ValidationScenario(
            name=f"{table}_row_count",
            severity="critical",
            source_table=table,
            target_table=table,
            source_query=f"SELECT COUNT(*) as value FROM `source_{table}`",
            target_query=f"SELECT COUNT(*) as value FROM `target_{table}`",
            comparison_type="exact_match"
        )
    
    def build_sum_scenario(self, table: str, column: str) -> ValidationScenario:
        return ValidationScenario(
            name=f"{table}_{column}_sum",
            severity="high",
            source_table=table,
            target_table=table,
            source_query=f"SELECT SUM({column}) as value FROM `source_{table}`",
            target_query=f"SELECT SUM({column}) as value FROM `target_{table}`",
            comparison_type="percentage_threshold",
            threshold_limit=self.severity_levels.get('high', 1.0)
        )
    
    def build_avg_scenario(self, table: str, column: str) -> ValidationScenario:
        return ValidationScenario(
            name=f"{table}_{column}_avg",
            severity="medium",
            source_table=table,
            target_table=table,
            source_query=f"SELECT AVG({column}) as value FROM `source_{table}`",
            target_query=f"SELECT AVG({column}) as value FROM `target_{table}`",
            comparison_type="percentage_threshold",
            threshold_limit=self.severity_levels.get('medium', 5.0)
        )
    
    def build_count_distinct_scenario(self, table: str, column: str) -> ValidationScenario:
        return ValidationScenario(
            name=f"{table}_{column}_distinct",
            severity="medium",
            source_table=table,
            target_table=table,
            source_query=f"SELECT COUNT(DISTINCT {column}) as value FROM `source_{table}`",
            target_query=f"SELECT COUNT(DISTINCT {column}) as value FROM `target_{table}`",
            comparison_type="percentage_threshold",
            threshold_limit=self.severity_levels.get('medium', 5.0)
        )
    
    def build_min_max_scenario(self, table: str, column: str) -> List[ValidationScenario]:
        return [
            ValidationScenario(
                name=f"{table}_{column}_min",
                severity="low",
                source_table=table,
                target_table=table,
                source_query=f"SELECT MIN({column}) as value FROM `source_{table}`",
                target_query=f"SELECT MIN({column}) as value FROM `target_{table}`",
                comparison_type="exact_match"
            ),
            ValidationScenario(
                name=f"{table}_{column}_max",
                severity="low",
                source_table=table,
                target_table=table,
                source_query=f"SELECT MAX({column}) as value FROM `source_{table}`",
                target_query=f"SELECT MAX({column}) as value FROM `target_{table}`",
                comparison_type="exact_match"
            )
        ]
    
    def build_all_scenarios(self, tables: List[str], 
                           columns_by_table: Dict[str, List[str]] = None) -> List[ValidationScenario]:
        """Build all possible scenarios for discovered tables."""
        columns_by_table = columns_by_table or {}
        scenarios = []
        
        for table in tables:
            scenarios.append(self.build_row_count_scenario(table))
            
            columns = columns_by_table.get(table, [])
            for col in columns[:5]:  # Limit to first 5 numeric columns
                scenarios.append(self.build_sum_scenario(table, col))
                scenarios.append(self.build_avg_scenario(table, col))
                scenarios.append(self.build_count_distinct_scenario(table, col))
                scenarios.extend(self.build_min_max_scenario(table, col))
        
        self.scenarios = scenarios
        return scenarios
    
    def to_yaml(self, output_path: str) -> str:
        """Export scenarios to YAML format."""
        yaml_data = []
        for scenario in self.scenarios:
            entry = {
                scenario.name: {
                    'severity': scenario.severity,
                    'source': {'query': scenario.source_query},
                    'target': {'query': scenario.target_query},
                    'comparisons': {}
                }
            }
            
            if scenario.comparison_type == 'percentage_threshold':
                entry[scenario.name]['comparisons']['threshold'] = {
                    'value': 'percentage',
                    'limit': scenario.threshold_limit
                }
            
            yaml_data.append(entry)
        
        with open(output_path, 'w') as f:
            yaml.dump(yaml_data, f, default_flow_style=False)
        
        return output_path
