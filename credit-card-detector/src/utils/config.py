"""
Configuration Management Utilities

Clean, simple configuration loading with environment overrides.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """
    Configuration manager with YAML files and environment variable support.
    """

    def __init__(self, config_file: Optional[str] = None, environment: str = "default"):
        """
        Initialize configuration.

        Args:
            config_file: Path to config file (optional)
            environment: Environment name (default, development, production)
        """
        self.environment = environment
        self.config = {}
        self._load_config(config_file)

    def _load_config(self, config_file: Optional[str] = None):
        """Load configuration from YAML files and environment variables."""
        # Get config directory
        config_dir = Path(__file__).parent.parent.parent / "config"

        # Load default config
        default_config_path = config_dir / "default.yaml"
        if default_config_path.exists():
            with open(default_config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}

        # Load environment-specific config
        if self.environment != "default":
            env_config_path = config_dir / f"{self.environment}.yaml"
            if env_config_path.exists():
                with open(env_config_path, 'r') as f:
                    env_config = yaml.safe_load(f) or {}
                    self._merge_config(self.config, env_config)

        # Load custom config file if provided
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                custom_config = yaml.safe_load(f) or {}
                self._merge_config(self.config, custom_config)

        # Apply environment variable overrides
        self._apply_env_overrides()

    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]):
        """Recursively merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        # Map environment variables to config keys
        env_mappings = {
            'PORT': 'app.port',
            'HOST': 'app.host',
            'DEBUG': 'app.debug',
            'LOG_LEVEL': 'monitoring.logging_level',
            'RATE_LIMIT': 'api.rate_limit.requests_per_minute',
            'API_KEY': 'security.authentication.api_key'
        }

        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(config_key, self._convert_env_value(env_value))

    def _set_nested_value(self, key_path: str, value: Any):
        """Set nested config value using dot notation."""
        keys = key_path.split('.')
        current = self.config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key_path: Configuration key (e.g., 'app.port')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        current = self.config

        for key in keys:
            if key in current:
                current = current[key]
            else:
                return default

        return current

    def get_app_config(self) -> Dict[str, Any]:
        """Get app configuration."""
        return self.get('app', {})

    def get_detection_config(self) -> Dict[str, Any]:
        """Get detection configuration."""
        return self.get('detection', {})

    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return self.get('api', {})

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self.get('monitoring', {})

    def is_monitoring_enabled(self) -> bool:
        """Check if monitoring is enabled."""
        return self.get('monitoring.enabled', False)

    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get('app.debug', False)


def load_config(config_file: Optional[str] = None, environment: str = "default") -> Config:
    """
    Load configuration from files and environment.

    Args:
        config_file: Optional custom config file path
        environment: Environment name

    Returns:
        Config object
    """
    return Config(config_file, environment)


# Default configuration instance
default_config = load_config()