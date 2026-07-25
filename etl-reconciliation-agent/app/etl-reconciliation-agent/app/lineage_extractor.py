import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

# Try to import sqlh, fallback to custom parser if not available
try:
    from sqlh import get_all_tables, get_all_root_tables
except ImportError:
    # Fallback implementation using regex
    def get_all_tables(sql: str) -> Set[str]:
        """Extract table names using regex pattern matching."""
        # Simple regex to find table names after FROM/JOIN
        patterns = [
            r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)',
            r'(?:FROM|JOIN)\s+`([^`]+)`',
            r'(?:FROM|JOIN)\s+"([^"]+)"'
        ]
        tables = set()
        for pattern in patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            for match in matches:
                tables.add(match)
        return tables
    
    def get_all_root_tables(sql: str) -> Set[str]:
        """Simple implementation - all tables are considered root."""
        return get_all_tables(sql)

@dataclass
class TableInfo:
    name: str
    is_root: bool = True
    upstream_tables: List[str] = field(default_factory=list)
    downstream_tables: List[str] = field(default_factory=list)
    files_containing: List[str] = field(default_factory=list)

class LineageExtractor:
    """Extracts table lineage from SQL files."""
    
    def __init__(self, root_path: str, exclude_folders: List[str] = None):
        self.root_path = Path(root_path)
        self.exclude_folders = exclude_folders or []
        self.sql_files = []
        self.all_tables = {}
    
    def discover_sql_files(self) -> List[Path]:
        """Recursively discover all SQL files."""
        if not self.root_path.exists():
            print(f"Warning: Path {self.root_path} does not exist")
            return []
        
        sql_files = []
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_folders]
            for file in files:
                if file.lower().endswith(('.sql', '.sql.j2')):
                    sql_files.append(Path(root) / file)
        
        self.sql_files = sql_files
        return sql_files
    
    def read_sql_content(self, file_path: Path) -> str:
        """Read SQL content from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    
    def extract_from_file(self, file_path: Path) -> Dict:
        """Extract lineage from a single SQL file."""
        content = self.read_sql_content(file_path)
        if not content:
            return {'file_path': str(file_path), 'error': 'Empty file'}
        
        try:
            all_tables = get_all_tables(content)
            root_tables = get_all_root_tables(content)
            
            return {
                'file_path': str(file_path),
                'all_tables': list(all_tables) if all_tables else [],
                'root_tables': list(root_tables) if root_tables else [],
                'is_complete': bool(all_tables)
            }
        except Exception as e:
            return {'file_path': str(file_path), 'error': str(e)}
    
    def extract_all_lineage(self) -> Dict[str, Dict]:
        """Extract lineage from all discovered SQL files."""
        if not self.sql_files:
            self.discover_sql_files()
        
        results = {}
        table_metadata = {}
        
        for sql_file in self.sql_files:
            result = self.extract_from_file(sql_file)
            results[str(sql_file)] = result
            
            for table in result.get('all_tables', []):
                if table not in table_metadata:
                    table_metadata[table] = TableInfo(
                        name=table,
                        is_root=table in result.get('root_tables', []),
                        files_containing=[]
                    )
                table_metadata[table].files_containing.append(str(sql_file))
        
        self.all_tables = table_metadata
        return results
    
    def get_source_tables(self) -> List[str]:
        return [t for t, info in self.all_tables.items() if info.is_root]
    
    def get_target_tables(self) -> List[str]:
        return [t for t, info in self.all_tables.items() 
                if info.files_containing and not info.is_root]
    
    def get_table_summary(self) -> Dict:
        return {
            'total_tables': len(self.all_tables),
            'source_tables': self.get_source_tables(),
            'target_tables': self.get_target_tables(),
            'all_tables': list(self.all_tables.keys())
        }
