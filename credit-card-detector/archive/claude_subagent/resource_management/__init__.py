"""
Resource Management System

Provides intelligent resource allocation, monitoring, and optimization
for the Credit Card Detector project.
"""

import os
import yaml
import psutil
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
import time

logger = logging.getLogger(__name__)


class ResourceLevel(Enum):
    """Resource level enumeration for different deployment sizes"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"


class OptimizationStrategy(Enum):
    """Resource optimization strategies"""
    SEQUENTIAL = "sequential"
    SKILL_PRIORITY = "skill_priority"
    BATCH_OPTIMIZED = "batch_optimized"
    PARALLEL_LIMITED = "parallel_limited"


@dataclass
class ResourceLimits:
    """Resource limits configuration"""
    cpu_cores: int
    memory_mb: int
    storage_gb: int
    network_mbps: int
    max_concurrent_requests: int
    batch_size: int
    plugin_limit: int


@dataclass
class ResourceMetrics:
    """Current resource usage metrics"""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_percent: float
    active_threads: int
    network_io: Dict[str, float]
    timestamp: float


class ResourceManager:
    """
    Intelligent resource management system that adapts to system constraints
    and optimizes performance based on available resources.
    """

    def __init__(self, profile: Optional[str] = None):
        """
        Initialize the resource manager.

        Args:
            profile: Resource profile to use (development, production, enterprise)
                    If None, will auto-detect based on available resources
        """
        self._profile = profile
        self._config = self._load_resource_config()
        self._current_profile = self._determine_profile(profile)
        self._limits = self._get_resource_limits()
        self._strategy = self._select_initial_strategy()
        self._monitoring = False
        self._monitor_thread = None
        self._last_metrics = None
        self._callbacks = []

        logger.info(f"Resource manager initialized with profile: {self._current_profile}")
        logger.info(f"Resource limits: CPU={self._limits.cpu_cores} cores, "
                   f"Memory={self._limits.memory_mb}MB, "
                   f"Max concurrent={self._limits.max_concurrent_requests}")

    def _load_resource_config(self) -> Dict[str, Any]:
        """Load resource configuration from file"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '../../config/resource-profiles.yaml'
        )

        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Resource config not found at {config_path}, using defaults")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading resource config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default resource configuration"""
        return {
            'profiles': {
                'development': {
                    'resources': {
                        'cpu': {'cores': 2, 'max_percent': 80},
                        'memory': {'total_mb': 4096, 'max_percent': 75}
                    },
                    'limits': {
                        'max_concurrent_requests': 5,
                        'batch_size': 50,
                        'plugin_limit': 3
                    }
                }
            },
            'strategies': {
                'sequential': {'cpu_threshold': 85, 'memory_threshold': 90}
            }
        }

    def _determine_profile(self, profile: Optional[str]) -> str:
        """Determine the appropriate resource profile"""
        if profile and profile in self._config['profiles']:
            return profile

        # Auto-detect based on available resources
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)

        if cpu_count >= 8 and memory_gb >= 16:
            return 'enterprise'
        elif cpu_count >= 4 and memory_gb >= 8:
            return 'production'
        else:
            return 'development'

    def _get_resource_limits(self) -> ResourceLimits:
        """Get resource limits for the current profile"""
        profile_config = self._config['profiles'][self._current_profile]
        resources = profile_config['resources']
        limits = profile_config['limits']

        return ResourceLimits(
            cpu_cores=resources['cpu']['cores'],
            memory_mb=resources['memory']['total_mb'],
            storage_gb=resources['storage']['total_gb'],
            network_mbps=resources['network']['bandwidth_mbps'],
            max_concurrent_requests=limits['max_concurrent_requests'],
            batch_size=limits['batch_size'],
            plugin_limit=limits['plugin_limit']
        )

    def _select_initial_strategy(self) -> OptimizationStrategy:
        """Select initial optimization strategy"""
        profile_config = self._config['profiles'][self._current_profile]
        strategy_name = profile_config['resources']['cpu'].get('strategy', 'sequential')

        return OptimizationStrategy(strategy_name)

    def get_current_metrics(self) -> ResourceMetrics:
        """Get current system resource metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        network_io = psutil.net_io_counters()._asdict()

        metrics = ResourceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available_mb=memory.available / (1024**2),
            disk_percent=disk.percent,
            active_threads=threading.active_count(),
            network_io=network_io,
            timestamp=time.time()
        )

        self._last_metrics = metrics
        return metrics

    def should_optimize(self, metrics: Optional[ResourceMetrics] = None) -> bool:
        """
        Check if resource optimization is needed based on current metrics.

        Args:
            metrics: Current resource metrics. If None, will fetch current metrics.

        Returns:
            True if optimization is needed, False otherwise
        """
        if metrics is None:
            metrics = self.get_current_metrics()

        current_strategy = self._config['strategies'][self._strategy.value]

        return (metrics.cpu_percent > current_strategy['cpu_threshold'] or
                metrics.memory_percent > current_strategy['memory_threshold'])

    def get_profile_summary(self) -> Dict[str, Any]:
        """Get a summary of the current resource profile and usage"""
        metrics = self.get_current_metrics()

        return {
            'profile': self._current_profile,
            'strategy': self._strategy.value,
            'limits': {
                'cpu_cores': self._limits.cpu_cores,
                'memory_mb': self._limits.memory_mb,
                'max_concurrent': self._limits.max_concurrent_requests,
                'batch_size': self._limits.batch_size,
                'plugin_limit': self._limits.plugin_limit
            },
            'current_usage': {
                'cpu_percent': metrics.cpu_percent,
                'memory_percent': metrics.memory_percent,
                'memory_available_mb': metrics.memory_available_mb,
                'disk_percent': metrics.disk_percent,
                'active_threads': metrics.active_threads
            },
            'optimization_needed': self.should_optimize(metrics)
        }


# Global resource manager instance
_resource_manager: Optional[ResourceManager] = None


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


def initialize_resource_manager(profile: Optional[str] = None) -> ResourceManager:
    """
    Initialize the global resource manager with a specific profile.

    Args:
        profile: Resource profile to use

    Returns:
        The initialized resource manager
    """
    global _resource_manager
    _resource_manager = ResourceManager(profile)
    return _resource_manager
