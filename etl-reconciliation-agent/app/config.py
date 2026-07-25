import os
import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration manager for the ETL Reconciliation Agent."""
    
    def __init__(self, config_path: str = "config/config.yml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    @property
    def gcp_project(self) -> str:
        return self.get('gcp.project_id', os.getenv('GCP_PROJECT_ID', ''))
    
    @property
    def gcp_location(self) -> str:
        return self.get('gcp.location', os.getenv('GCP_LOCATION', 'us-central1'))
    
    @property
    def source_root(self) -> str:
        return self.get('source_code.root_path', './sql')
    
    @property
    def output_dir(self) -> str:
        return self.get('output_dir', './output')

# Singleton instance
config = Config()
