"""
Plugin System for Extensible Detection

This module provides a comprehensive plugin architecture that allows
users to easily add new detection types, processors, and integrations
without modifying core code.

Key Features:
- Hot-loading of plugins
- Plugin lifecycle management
- Dependency resolution
- Configuration validation
- Performance monitoring
"""

import os
import sys
import importlib
import importlib.util
import inspect
import json
import yaml
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins supported by the system"""
    DETECTOR = "detector"
    PROCESSOR = "processor"
    OUTPUT = "output"
    INTEGRATION = "integration"
    VALIDATOR = "validator"
    TRANSFORMER = "transformer"


class PluginStatus(Enum):
    """Plugin lifecycle status"""
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNLOADING = "unloading"


@dataclass
class PluginMetadata:
    """Metadata for a plugin"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = field(default_factory=list)
    min_system_version: str = "1.0.0"
    max_system_version: str = "999.0.0"
    config_schema: Optional[Dict[str, Any]] = None
    entry_point: str = "plugin.py"
    enabled: bool = True
    priority: int = 50  # Higher priority loads first


@dataclass
class PluginInfo:
    """Runtime information about a loaded plugin"""
    metadata: PluginMetadata
    status: PluginStatus
    module: Optional[Any] = None
    instance: Optional[Any] = None
    error_message: Optional[str] = None
    load_time: Optional[float] = None
    last_used: Optional[float] = None
    usage_count: int = 0


class BasePlugin(ABC):
    """Base class for all plugins"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(f"plugin.{self.name}")

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        """Cleanup plugin resources. Return True if successful."""
        pass

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration. Override if needed."""
        return True

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.name,
            "class": self.__class__.__name__,
            "module": self.__class__.__module__,
            "config": self.config
        }


class DetectorPlugin(BasePlugin):
    """Base class for detector plugins"""

    @abstractmethod
    def detect(self, text: str) -> List[Dict[str, Any]]:
        """Detect patterns in text and return results."""
        pass

    @abstractmethod
    def get_supported_patterns(self) -> List[str]:
        """Return list of supported pattern types."""
        pass

    def get_confidence_threshold(self) -> float:
        """Get confidence threshold for detections."""
        return self.config.get("confidence_threshold", 0.7)


class ProcessorPlugin(BasePlugin):
    """Base class for processor plugins"""

    @abstractmethod
    def process(self, detections: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """Process detection results."""
        pass

    @abstractmethod
    def get_input_types(self) -> List[str]:
        """Return supported input types."""
        pass


class OutputPlugin(BasePlugin):
    """Base class for output plugins"""

    @abstractmethod
    def output(self, detections: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> bool:
        """Output detection results."""
        pass

    @abstractmethod
    def get_output_formats(self) -> List[str]:
        """Return supported output formats."""
        pass


class PluginManager:
    """Main plugin management system"""

    def __init__(self, plugin_dirs: List[str] = None):
        self.plugin_dirs = plugin_dirs or []
        self.plugins: Dict[str, PluginInfo] = {}
        self.plugin_registry: Dict[PluginType, List[str]] = {
            plugin_type: [] for plugin_type in PluginType
        }
        self.load_order: List[str] = []
        self._lock = threading.RLock()

        # Add default plugin directories
        self.plugin_dirs.extend([
            "plugins",
            "claude_subagent/plugins",
            os.path.expanduser("~/.claude_subagent/plugins"),
            "/etc/claude_subagent/plugins"
        ])

    def discover_plugins(self) -> List[PluginMetadata]:
        """Discover all available plugins in configured directories."""
        discovered_plugins = []

        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue

            for plugin_path in Path(plugin_dir).iterdir():
                if plugin_path.is_dir():
                    metadata_file = plugin_path / "plugin.yaml"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata_dict = yaml.safe_load(f)

                            metadata = PluginMetadata(**metadata_dict)
                            metadata.entry_point = str(plugin_path / metadata.entry_point)
                            discovered_plugins.append(metadata)

                        except Exception as e:
                            logger.error(f"Error loading plugin metadata from {metadata_file}: {e}")

        return discovered_plugins

    def load_plugin(self, metadata: PluginMetadata) -> bool:
        """Load a single plugin."""
        with self._lock:
            if metadata.name in self.plugins:
                logger.warning(f"Plugin {metadata.name} already loaded")
                return False

            plugin_info = PluginInfo(
                metadata=metadata,
                status=PluginStatus.LOADING
            )

            self.plugins[metadata.name] = plugin_info

            try:
                # Load the plugin module
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{metadata.name}",
                    metadata.entry_point
                )

                if spec is None or spec.loader is None:
                    raise ImportError(f"Could not load spec from {metadata.entry_point}")

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find the plugin class
                plugin_class = None
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BasePlugin) and obj != BasePlugin:
                        plugin_class = obj
                        break

                if plugin_class is None:
                    raise ValueError(f"No plugin class found in {metadata.entry_point}")

                # Create plugin instance
                plugin_instance = plugin_class(metadata.config)

                # Initialize plugin
                if not plugin_instance.initialize():
                    raise RuntimeError(f"Plugin {metadata.name} failed to initialize")

                # Update plugin info
                plugin_info.module = module
                plugin_info.instance = plugin_instance
                plugin_info.status = PluginStatus.ACTIVE
                plugin_info.load_time = datetime.now().timestamp()

                # Register in type registry
                self.plugin_registry[metadata.plugin_type].append(metadata.name)

                # Update load order
                self.load_order.append(metadata.name)

                logger.info(f"Successfully loaded plugin: {metadata.name} v{metadata.version}")
                return True

            except Exception as e:
                plugin_info.status = PluginStatus.ERROR
                plugin_info.error_message = str(e)
                logger.error(f"Failed to load plugin {metadata.name}: {e}")
                return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        with self._lock:
            if plugin_name not in self.plugins:
                logger.warning(f"Plugin {plugin_name} not found")
                return False

            plugin_info = self.plugins[plugin_name]

            try:
                plugin_info.status = PluginStatus.UNLOADING

                # Cleanup plugin
                if plugin_info.instance:
                    plugin_info.instance.cleanup()

                # Remove from registry
                if plugin_name in self.load_order:
                    self.load_order.remove(plugin_name)

                for plugin_type, plugins in self.plugin_registry.items():
                    if plugin_name in plugins:
                        plugins.remove(plugin_name)

                # Mark as inactive
                plugin_info.status = PluginStatus.INACTIVE
                plugin_info.instance = None
                plugin_info.module = None

                logger.info(f"Successfully unloaded plugin: {plugin_name}")
                return True

            except Exception as e:
                plugin_info.status = PluginStatus.ERROR
                plugin_info.error_message = str(e)
                logger.error(f"Failed to unload plugin {plugin_name}: {e}")
                return False

    def load_all_plugins(self) -> Dict[str, bool]:
        """Load all discovered plugins."""
        results = {}
        discovered_plugins = self.discover_plugins()

        # Sort by priority
        discovered_plugins.sort(key=lambda p: p.priority, reverse=True)

        for metadata in discovered_plugins:
            if metadata.enabled:
                results[metadata.name] = self.load_plugin(metadata)

        return results

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a loaded plugin instance."""
        with self._lock:
            if plugin_name not in self.plugins:
                return None

            plugin_info = self.plugins[plugin_name]
            if plugin_info.status != PluginStatus.ACTIVE:
                return None

            # Update usage stats
            plugin_info.last_used = datetime.now().timestamp()
            plugin_info.usage_count += 1

            return plugin_info.instance

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[BasePlugin]:
        """Get all loaded plugins of a specific type."""
        plugins = []

        for plugin_name in self.plugin_registry[plugin_type]:
            plugin = self.get_plugin(plugin_name)
            if plugin:
                plugins.append(plugin)

        return plugins

    def execute_detectors(self, text: str) -> List[Dict[str, Any]]:
        """Execute all detector plugins."""
        all_detections = []

        for detector in self.get_plugins_by_type(PluginType.DETECTOR):
            try:
                detections = detector.detect(text)
                if detections:
                    # Add metadata
                    for detection in detections:
                        detection["detector"] = detector.name
                        detection["confidence"] = detection.get("confidence", 0.8)
                    all_detections.extend(detections)
            except Exception as e:
                logger.error(f"Error in detector {detector.name}: {e}")

        return all_detections

    def execute_processors(self, detections: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """Execute all processor plugins."""
        processed_detections = detections

        for processor in self.get_plugins_by_type(PluginType.PROCESSOR):
            try:
                processed_detections = processor.process(processed_detections, text)
            except Exception as e:
                logger.error(f"Error in processor {processor.name}: {e}")

        return processed_detections

    def execute_outputs(self, detections: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> bool:
        """Execute all output plugins."""
        success = True

        for output_plugin in self.get_plugins_by_type(PluginType.OUTPUT):
            try:
                result = output_plugin.output(detections, metadata)
                if not result:
                    success = False
                    logger.warning(f"Output plugin {output_plugin.name} failed")
            except Exception as e:
                success = False
                logger.error(f"Error in output plugin {output_plugin.name}: {e}")

        return success

    def get_plugin_status(self) -> Dict[str, Any]:
        """Get status of all plugins."""
        status = {
            "total_plugins": len(self.plugins),
            "active_plugins": 0,
            "inactive_plugins": 0,
            "error_plugins": 0,
            "plugins_by_type": {},
            "plugins": {}
        }

        for plugin_type in PluginType:
            status["plugins_by_type"][plugin_type.value] = len(self.plugin_registry[plugin_type])

        for plugin_name, plugin_info in self.plugins.items():
            plugin_status = {
                "status": plugin_info.status.value,
                "version": plugin_info.metadata.version,
                "type": plugin_info.metadata.plugin_type.value,
                "load_time": plugin_info.load_time,
                "last_used": plugin_info.last_used,
                "usage_count": plugin_info.usage_count
            }

            if plugin_info.error_message:
                plugin_status["error"] = plugin_info.error_message

            status["plugins"][plugin_name] = plugin_status

            if plugin_info.status == PluginStatus.ACTIVE:
                status["active_plugins"] += 1
            elif plugin_info.status == PluginStatus.INACTIVE:
                status["inactive_plugins"] += 1
            elif plugin_info.status == PluginStatus.ERROR:
                status["error_plugins"] += 1

        return status

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin."""
        if plugin_name in self.plugins:
            metadata = self.plugins[plugin_name].metadata
            self.unload_plugin(plugin_name)
            return self.load_plugin(metadata)
        return False

    def validate_plugin_dependencies(self, metadata: PluginMetadata) -> List[str]:
        """Validate that all dependencies are available."""
        missing_deps = []

        for dep in metadata.dependencies:
            if dep not in self.plugins:
                missing_deps.append(dep)

        return missing_deps

    def get_load_order(self) -> List[str]:
        """Get the plugin load order."""
        return self.load_order.copy()


# Global plugin manager instance
plugin_manager = PluginManager()