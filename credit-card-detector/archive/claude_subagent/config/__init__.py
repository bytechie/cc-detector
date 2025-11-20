"""
Advanced Configuration Management System

This module provides a comprehensive configuration management solution that supports:
- Multiple configuration formats (YAML, JSON, TOML, ENV)
- Environment-specific configurations
- Configuration validation and schema
- Hot-reloading capabilities
- Configuration encryption and security
- Remote configuration sources
"""

import os
import json
import yaml
import toml
from typing import Dict, List, Any, Optional, Union, Type, Callable
from pathlib import Path
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from enum import Enum
import logging
import threading
import time
from datetime import datetime
import hashlib
import secrets
from cryptography.fernet import Fernet
import jsonschema
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Supported configuration formats"""
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"
    ENV = "env"


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ConfigSource:
    """Configuration source definition"""
    name: str
    format: ConfigFormat
    path: Union[str, Path]
    required: bool = True
    encrypted: bool = False
    remote: bool = False
    priority: int = 0  # Higher priority overrides lower
    watch_changes: bool = True


class ConfigValidationError(Exception):
    """Configuration validation error"""
    pass


class ConfigEncryption:
    """Configuration encryption utilities"""

    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            key = self._generate_key()
        self.cipher = Fernet(key)
        self.key = key

    def _generate_key(self) -> bytes:
        """Generate encryption key"""
        return Fernet.generate_key()

    def encrypt(self, data: str) -> str:
        """Encrypt configuration data"""
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt configuration data"""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash a configuration key"""
        return hashlib.sha256(key.encode()).hexdigest()[:16]


class ConfigSchema:
    """Configuration schema validation"""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.validator = jsonschema.Draft7Validator(schema)

    def validate(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration against schema"""
        errors = []
        for error in self.validator.iter_errors(config):
            errors.append(f"{'.'.join(str(p) for p in error.path)}: {error.message}")
        return errors

    def get_default_values(self) -> Dict[str, Any]:
        """Get default values from schema"""
        def extract_defaults(schema_obj):
            defaults = {}
            if isinstance(schema_obj, dict):
                if 'default' in schema_obj:
                    return schema_obj['default']
                elif 'properties' in schema_obj:
                    for key, value in schema_obj['properties'].items():
                        default_value = extract_defaults(value)
                        if default_value is not None:
                            defaults[key] = default_value
            return defaults

        return extract_defaults(self.schema)


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration changes"""

    def __init__(self, config_manager: 'ConfigManager', source: ConfigSource):
        self.config_manager = config_manager
        self.source = source

    def on_modified(self, event):
        if not event.is_directory and event.src_path == str(self.source.path):
            logger.info(f"Configuration file changed: {self.source.path}")
            self.config_manager.reload_source(self.source.name)


class ConfigManager:
    """Advanced configuration management system"""

    def __init__(self,
                 app_name: str = "claude_subagent",
                 environment: Environment = Environment.DEVELOPMENT,
                 config_dir: Union[str, Path] = "config"):
        self.app_name = app_name
        self.environment = environment
        self.config_dir = Path(config_dir)
        self.sources: Dict[str, ConfigSource] = {}
        self.config: Dict[str, Any] = {}
        self.schemas: Dict[str, ConfigSchema] = {}
        self.encryption = ConfigEncryption()
        self._observers: List[Observer] = []
        self._lock = threading.RLock()
        self._change_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []

        # Initialize default configuration structure
        self._init_default_structure()

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _init_default_structure(self):
        """Initialize default configuration structure"""
        self.config = {
            "app": {
                "name": self.app_name,
                "environment": self.environment.value,
                "debug": self.environment == Environment.DEVELOPMENT,
                "version": "1.0.0"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 5000,
                "workers": 1
            },
            "detection": {
                "confidence_threshold": 0.7,
                "max_text_length": 1000000,
                "timeout": 30
            },
            "resources": {
                "max_cpu_percent": 80,
                "max_memory_percent": 80,
                "max_batch_size": 1000,
                "max_concurrent_tasks": 4
            },
            "adaptive_skills": {
                "enabled": True,
                "quality_threshold": 0.6,
                "auto_import": True
            },
            "skill_seekers": {
                "enabled": False,
                "api_key": None,
                "scan_interval_hours": 24
            },
            "plugins": {
                "enabled": True,
                "auto_load": True,
                "directories": ["plugins"]
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": None,
                "max_size": "10MB",
                "backup_count": 5
            },
            "security": {
                "enable_encryption": False,
                "api_key_required": False,
                "cors_origins": ["*"]
            },
            "monitoring": {
                "enable_metrics": True,
                "enable_tracing": False,
                "export_interval": 60
            },
            "database": {
                "url": None,
                "pool_size": 10,
                "max_overflow": 20
            }
        }

    def add_source(self, source: ConfigSource):
        """Add a configuration source"""
        with self._lock:
            self.sources[source.name] = source

            # Load the source
            self._load_source(source)

            # Setup file watching if enabled
            if source.watch_changes and not source.remote:
                self._setup_file_watcher(source)

    def remove_source(self, source_name: str):
        """Remove a configuration source"""
        with self._lock:
            if source_name in self.sources:
                source = self.sources[source_name]
                self._stop_file_watcher(source)
                del self.sources[source_name]

    def _load_source(self, source: ConfigSource):
        """Load configuration from a source"""
        try:
            if source.remote:
                config_data = self._load_remote_config(source)
            else:
                config_data = self._load_file_config(source)

            if config_data:
                # Decrypt if necessary
                if source.encrypted:
                    config_data = self._decrypt_config(config_data)

                # Validate against schema if available
                if source.name in self.schemas:
                    errors = self.schemas[source.name].validate(config_data)
                    if errors:
                        raise ConfigValidationError(f"Schema validation failed: {errors}")

                # Merge with existing configuration
                self._merge_config(config_data, source.priority)

                logger.info(f"Loaded configuration from {source.name}")

        except Exception as e:
            if source.required:
                raise ConfigValidationError(f"Failed to load required config source {source.name}: {e}")
            else:
                logger.warning(f"Failed to load optional config source {source.name}: {e}")

    def _load_file_config(self, source: ConfigSource) -> Optional[Dict[str, Any]]:
        """Load configuration from file"""
        config_path = Path(source.path)

        if not config_path.exists():
            if source.required:
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if source.format == ConfigFormat.YAML:
                    return yaml.safe_load(f)
                elif source.format == ConfigFormat.JSON:
                    return json.load(f)
                elif source.format == ConfigFormat.TOML:
                    return toml.load(f)
                elif source.format == ConfigFormat.ENV:
                    # Simple key=value format
                    config = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
                    return config

        except Exception as e:
            raise ConfigValidationError(f"Error parsing {config_path}: {e}")

        return None

    def _load_remote_config(self, source: ConfigSource) -> Optional[Dict[str, Any]]:
        """Load configuration from remote source (placeholder)"""
        # This would integrate with remote config services
        # like Consul, etcd, AWS Parameter Store, etc.
        logger.warning(f"Remote configuration loading not implemented for {source.name}")
        return None

    def _decrypt_config(self, encrypted_config: str) -> str:
        """Decrypt encrypted configuration"""
        try:
            return self.encryption.decrypt(encrypted_config)
        except Exception as e:
            raise ConfigValidationError(f"Failed to decrypt configuration: {e}")

    def _merge_config(self, new_config: Dict[str, Any], priority: int = 0):
        """Merge new configuration with existing"""
        def merge_dict(base: Dict, updates: Dict):
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value

        # Priority-based merging
        if priority > 0:
            # High priority overrides existing
            merge_dict(self.config, new_config)
        else:
            # Low priority gets overridden by existing
            merged = new_config.copy()
            merge_dict(merged, self.config)
            self.config = merged

    def _setup_file_watcher(self, source: ConfigSource):
        """Setup file system watcher for configuration changes"""
        if not source.watch_changes or source.remote:
            return

        try:
            event_handler = ConfigFileHandler(self, source)
            observer = Observer()
            observer.schedule(
                event_handler,
                str(Path(source.path).parent),
                recursive=False
            )
            observer.start()
            self._observers.append(observer)
            logger.info(f"Started watching configuration file: {source.path}")
        except Exception as e:
            logger.warning(f"Failed to setup file watcher for {source.path}: {e}")

    def _stop_file_watcher(self, source: ConfigSource):
        """Stop file system watcher for a source"""
        # Find and remove the observer for this source
        for i, observer in enumerate(self._observers):
            if hasattr(observer, 'event_handler') and observer.event_handler.source == source:
                observer.stop()
                observer.join()
                del self._observers[i]
                break

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def reload_source(self, source_name: str) -> bool:
        """Reload a specific configuration source"""
        with self._lock:
            if source_name not in self.sources:
                return False

            source = self.sources[source_name]
            return self._load_source(source)

    def reload_all(self) -> Dict[str, bool]:
        """Reload all configuration sources"""
        results = {}

        for source_name in self.sources:
            results[source_name] = self.reload_source(source_name)

        return results

    def add_schema(self, name: str, schema: Dict[str, Any]):
        """Add configuration schema for validation"""
        self.schemas[name] = ConfigSchema(schema)

    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all configuration sources"""
        errors = {}

        for source_name, schema in self.schemas.items():
            if source_name in self.sources:
                # Extract relevant config section for this schema
                config_section = self.get(source_name, {})
                validation_errors = schema.validate(config_section)
                if validation_errors:
                    errors[source_name] = validation_errors

        return errors

    def add_change_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Add callback for configuration changes"""
        self._change_callbacks.append(callback)

    def remove_change_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Remove configuration change callback"""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

    def _notify_changes(self, source_name: str, old_config: Dict[str, Any]):
        """Notify callbacks of configuration changes"""
        for callback in self._change_callbacks:
            try:
                callback(source_name, old_config)
            except Exception as e:
                logger.error(f"Error in config change callback: {e}")

    def save_to_file(self, file_path: Union[str, Path], format: ConfigFormat = ConfigFormat.YAML):
        """Save current configuration to file"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if format == ConfigFormat.YAML:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
                elif format == ConfigFormat.JSON:
                    json.dump(self.config, f, indent=2, default=str)
                elif format == ConfigFormat.TOML:
                    toml.dump(self.config, f)

            logger.info(f"Configuration saved to {file_path}")

        except Exception as e:
            raise ConfigValidationError(f"Failed to save configuration to {file_path}: {e}")

    def encrypt_sensitive_fields(self, sensitive_keys: List[str]):
        """Encrypt sensitive configuration fields"""
        for key in sensitive_keys:
            value = self.get(key)
            if value is not None:
                encrypted_value = self.encryption.encrypt(str(value))
                self.set(f"{key}_encrypted", encrypted_value)
                # Remove unencrypted value
                keys = key.split('.')
                config = self.config
                for k in keys[:-1]:
                    config = config[k]
                if keys[-1] in config:
                    del config[keys[-1]]

    def decrypt_sensitive_fields(self, sensitive_keys: List[str]):
        """Decrypt sensitive configuration fields"""
        for key in sensitive_keys:
            encrypted_value = self.get(f"{key}_encrypted")
            if encrypted_value is not None:
                decrypted_value = self.encryption.decrypt(encrypted_value)
                self.set(key, decrypted_value)

    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        env_config = self.get("environments", {}).get(self.environment.value, {})
        return env_config

    def apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""
        env_config = self.get_environment_config()
        if env_config:
            self._merge_config(env_config, priority=10)  # High priority

    def export_config(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Export configuration for inspection or backup"""
        config_copy = json.loads(json.dumps(self.config, default=str))

        if not include_sensitive:
            # Remove sensitive fields
            sensitive_patterns = ["password", "key", "secret", "token", "credential"]
            keys_to_remove = []

            def find_sensitive_keys(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        if any(pattern in key.lower() for pattern in sensitive_patterns):
                            keys_to_remove.append(full_key)
                        elif isinstance(value, (dict, list)):
                            find_sensitive_keys(value, full_key)

            find_sensitive_keys(config_copy)

            for key in keys_to_remove:
                keys = key.split('.')
                config = config_copy
                for k in keys[:-1]:
                    if k in config:
                        config = config[k]
                if keys[-1] in config:
                    config[keys[-1]] = "***REDACTED***"

        return config_copy

    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "environment": self.environment.value,
            "sources": len(self.sources),
            "schemas": len(self.schemas),
            "file_watchers": len(self._observers),
            "change_callbacks": len(self._change_callbacks),
            "config_keys": len(self._flatten_dict(self.config))
        }

    def _flatten_dict(self, d: Dict, prefix: str = "") -> int:
        """Count total keys in nested dictionary"""
        count = 0
        for key, value in d.items():
            count += 1
            if isinstance(value, dict):
                count += self._flatten_dict(value, f"{prefix}.{key}" if prefix else key)
        return count

    def cleanup(self):
        """Cleanup resources"""
        for observer in self._observers:
            observer.stop()
            observer.join()
        self._observers.clear()


# Global configuration manager instance
config_manager = ConfigManager()