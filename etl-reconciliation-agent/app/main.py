import sys
import yaml
from pathlib import Path

from .lineage_extractor import LineageExtractor
from .scenario_builder import ScenarioBuilder
from .validator import Validator
from .reporter import Reporter
from .config import config

def main():
    print("🔍 ETL Reconciliation Agent Started")
    
    # Step 1: Discover SQL files
    extractor = LineageExtractor(
        root_path=config.source_root,
        exclude_folders=['archive', 'deprecated', 'tests']
    )
    
    sql_files = extractor.discover_sql_files()
    print(f"📄 Found {len(sql_files)} SQL files")
    
    if not sql_files:
        print("⚠️ No SQL files found. Please check the source path.")
        return
    
    # Step 2: Extract lineage
    lineage_results = extractor.extract_all_lineage()
    summary = extractor.get_table_summary()
    
    print(f"📊 Discovered {summary['total_tables']} tables")
    print(f"  Source tables: {len(summary['source_tables'])}")
    print(f"  Target tables: {len(summary['target_tables'])}")
    
    # Step 3: Build scenarios
    scenario_builder = ScenarioBuilder()
    all_tables = summary['source_tables'] + summary['target_tables']
    
    # Auto-detect numeric columns (simplified)
    columns_by_table = {}
    for table in all_tables:
        columns_by_table[table] = ['id', 'amount', 'count', 'total', 'value']
    
    scenarios = scenario_builder.build_all_scenarios(all_tables, columns_by_table)
    print(f"🧪 Generated {len(scenarios)} validation scenarios")
    
    # Step 4: Export scenarios
    yaml_path = scenario_builder.to_yaml('config/test_suite.yml')
    print(f"📝 Scenarios exported to: {yaml_path}")
    
    # Step 5: Execute validation
    with open(yaml_path, 'r') as f:
        test_suite = yaml.safe_load(f)
    
    validator = Validator()
    results = validator.execute_suite(test_suite)
    
    # Step 6: Generate report
    reporter = Reporter()
    markdown = reporter.generate_markdown_report(results)
    json_path = reporter.generate_json_report(results)
    
    print(f"\n📄 Report saved to: {json_path}")
    print("\n" + "="*60)
    print(markdown)
    print("="*60)
    
    # Return exit code
    summary = validator.get_summary(results)
    if summary['status'] == 'FAIL':
        sys.exit(1)

if __name__ == "__main__":
    main()
