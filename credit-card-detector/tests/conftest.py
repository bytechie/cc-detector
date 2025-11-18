"""
Pytest Configuration and Fixtures

This module provides comprehensive pytest configuration, fixtures, and utilities
for testing all aspects of the credit card detection system including:
- Resource-aware processing
- Adaptive skills
- Plugin system
- Configuration management
- Integration testing
- Performance testing
"""

import pytest
import asyncio
import tempfile
import shutil
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Generator, Optional
import json
import time
import logging
from unittest.mock import Mock, AsyncMock, patch
import multiprocessing

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from claude_subagent.adaptive_skills import AdaptiveSkillManager, GeneratedSkill
from claude_subagent.resource_management import (
    ResourceConstraints, ResourceMonitor, AdaptiveProcessingEngine
)
from claude_subagent.plugin_system import PluginManager, PluginMetadata, PluginType
from claude_subagent.config import ConfigManager, Environment


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def config_dir(temp_dir: Path) -> Path:
    """Create a config directory within temp directory."""
    config_path = temp_dir / "config"
    config_path.mkdir(exist_ok=True)
    return config_path


@pytest.fixture
def sample_texts() -> List[str]:
    """Sample texts containing credit card numbers for testing."""
    return [
        "Visa card: 4111111111111111",
        "MasterCard: 5500000000000004",
        "American Express: 378282246310005",
        "Discover: 6011111111111117",
        "Diners Club: 3056930009020004",
        "JCB: 3530111333300000",
        "No card number here",
        "Invalid: 1234567890123456",
        "Another card: 4242424242424242",
        "Card with spaces: 4111 1111 1111 1111",
        "Card with hyphens: 4111-1111-1111-1111",
        "International: 4111111111111111 (Valid Visa)",
        "Test data only: 4111111111111111"
    ]


@pytest.fixture
def sample_detections() -> List[Dict[str, Any]]:
    """Sample detection results for testing."""
    return [
        {
            "start": 0,
            "end": 16,
            "raw": "4111111111111111",
            "number": "4111111111111111",
            "valid": True,
            "confidence": 0.95
        },
        {
            "start": 0,
            "end": 16,
            "raw": "4242424242424242",
            "number": "4242424242424242",
            "valid": True,
            "confidence": 0.92
        },
        {
            "start": 10,
            "end": 26,
            "raw": "378282246310005",
            "number": "378282246310005",
            "valid": True,
            "confidence": 0.88
        }
    ]


@pytest.fixture
def adaptive_skill_manager(temp_dir: Path) -> AdaptiveSkillManager:
    """Create an AdaptiveSkillManager instance for testing."""
    manager = AdaptiveSkillManager(skills_dir=str(temp_dir / "skills"))
    return manager


@pytest.fixture
def mock_resource_constraints() -> ResourceConstraints:
    """Create mock resource constraints for testing."""
    return ResourceConstraints(
        max_cpu_percent=75.0,
        max_memory_percent=80.0,
        max_batch_size=100,
        max_concurrent_tasks=4
    )


@pytest.fixture
def mock_resource_monitor() -> Mock:
    """Create a mock resource monitor."""
    monitor = Mock()

    # Mock current metrics
    mock_metrics = Mock()
    mock_metrics.cpu_percent = 45.0
    mock_metrics.memory_percent = 60.0
    mock_metrics.memory_available_mb = 4096.0
    mock_metrics.memory_used_mb = 2048.0
    mock_metrics.active_threads = 8
    mock_metrics.active_processes = 100
    mock_metrics.disk_io_read_mb = 50.0
    mock_metrics.disk_io_write_mb = 25.0
    mock_metrics.network_io_sent_mb = 10.0
    mock_metrics.network_io_recv_mb = 15.0

    monitor.get_current_metrics.return_value = mock_metrics
    monitor.get_average_metrics.return_value = mock_metrics
    monitor.start_monitoring.return_value = None
    monitor.stop_monitoring.return_value = None

    return monitor


@pytest.fixture
def adaptive_processing_engine(mock_resource_constraints: ResourceConstraints) -> AdaptiveProcessingEngine:
    """Create an AdaptiveProcessingEngine instance for testing."""
    engine = AdaptiveProcessingEngine(constraints=mock_resource_constraints)
    yield engine
    # Cleanup
    engine.cleanup()


@pytest.fixture
def plugin_manager(temp_dir: Path) -> PluginManager:
    """Create a PluginManager instance for testing."""
    plugin_dir = temp_dir / "plugins"
    plugin_dir.mkdir(exist_ok=True)

    manager = PluginManager(plugin_dirs=[str(plugin_dir)])
    return manager


@pytest.fixture
def sample_plugin_metadata() -> PluginMetadata:
    """Sample plugin metadata for testing."""
    return PluginMetadata(
        name="test_detector",
        version="1.0.0",
        description="Test detector plugin",
        author="Test Author",
        plugin_type=PluginType.DETECTOR,
        dependencies=[],
        config_schema={
            "type": "object",
            "properties": {
                "confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.7
                }
            }
        }
    )


@pytest.fixture
def config_manager(config_dir: Path) -> ConfigManager:
    """Create a ConfigManager instance for testing."""
    # Create test config files
    test_config = {
        "app": {
            "name": "test_app",
            "debug": True
        },
        "detection": {
            "confidence_threshold": 0.8,
            "timeout": 15
        }
    }

    # YAML config
    with open(config_dir / "test.yaml", 'w') as f:
        import yaml
        yaml.dump(test_config, f)

    # JSON config
    with open(config_dir / "test.json", 'w') as f:
        json.dump(test_config, f)

    manager = ConfigManager(
        app_name="test_app",
        environment=Environment.TESTING,
        config_dir=str(config_dir)
    )

    return manager


@pytest.fixture
def performance_test_data() -> Dict[str, Any]:
    """Data for performance testing."""
    return {
        "small_dataset": ["test"] * 100,
        "medium_dataset": ["test"] * 1000,
        "large_dataset": ["test"] * 10000,
        "resource_constraints": [
            {"name": "low_resources", "max_cpu": 30, "max_memory": 30},
            {"name": "medium_resources", "max_cpu": 60, "max_memory": 60},
            {"name": "high_resources", "max_cpu": 80, "max_memory": 80}
        ]
    }


@pytest.fixture
def mock_skill() -> GeneratedSkill:
    """Create a mock skill for testing."""
    return GeneratedSkill(
        name="test_skill",
        code="""
def detect(text):
    import re
    pattern = r'\\b(?:\\d[ -]?){13,19}\\d\\b'
    matches = []
    for match in re.finditer(pattern, text):
        matches.append({
            "start": match.start(),
            "end": match.end(),
            "raw": match.group(0),
            "number": re.sub(r'\\D', '', match.group(0)),
            "valid": True,
            "confidence": 0.8
        })
    return matches
""",
        description="Test skill for credit card detection",
        dependencies=["re"],
        test_cases=[
            {"input": "Card: 4111111111111111", "expected_count": 1},
            {"input": "No card here", "expected_count": 0}
        ]
    )


@pytest.fixture
def integration_test_config() -> Dict[str, Any]:
    """Configuration for integration tests."""
    return {
        "presidio": {
            "analyzer_url": "http://localhost:3000",
            "anonymizer_url": "http://localhost:3001"
        },
        "n8n": {
            "webhook_url": "http://localhost:5678/webhook",
            "workflow_id": "test_workflow"
        },
        "database": {
            "url": "sqlite:///test.db",
            "test_mode": True
        }
    }


# Custom pytest markers
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: Mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "resource_intensive: Mark test as resource intensive"
    )


# Utility functions for tests
def create_test_plugin(plugin_dir: Path, metadata: PluginMetadata, code: str) -> None:
    """Create a test plugin directory and files."""
    plugin_path = plugin_dir / metadata.name
    plugin_path.mkdir(exist_ok=True)

    # Create plugin.yaml
    import yaml
    with open(plugin_path / "plugin.yaml", 'w') as f:
        yaml.dump(metadata.__dict__, f)

    # Create plugin.py
    with open(plugin_path / metadata.entry_point, 'w') as f:
        f.write(code)


def assert_detection_results(actual: List[Dict[str, Any]],
                           expected: List[Dict[str, Any]],
                           tolerance: float = 0.1) -> None:
    """Assert that detection results match expected values within tolerance."""
    assert len(actual) == len(expected), f"Expected {len(expected)} detections, got {len(actual)}"

    for i, (actual_item, expected_item) in enumerate(zip(actual, expected)):
        assert actual_item["start"] == expected_item["start"], f"Item {i}: start mismatch"
        assert actual_item["end"] == expected_item["end"], f"Item {i}: end mismatch"
        assert actual_item["raw"] == expected_item["raw"], f"Item {i}: raw mismatch"

        if "confidence" in expected_item:
            actual_confidence = actual_item.get("confidence", 0.0)
            expected_confidence = expected_item["confidence"]
            assert abs(actual_confidence - expected_confidence) <= tolerance, \
                f"Item {i}: confidence mismatch: {actual_confidence} vs {expected_confidence}"


def measure_performance(func, *args, **kwargs) -> Dict[str, Any]:
    """Measure performance of a function."""
    start_time = time.time()
    start_memory = get_memory_usage()

    result = func(*args, **kwargs)

    end_time = time.time()
    end_memory = get_memory_usage()

    return {
        "result": result,
        "execution_time": end_time - start_time,
        "memory_delta": end_memory - start_memory,
        "throughput": len(result) if isinstance(result, (list, tuple)) else 1
    }


def get_memory_usage() -> float:
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    except ImportError:
        return 0.0


def async_test(func):
    """Decorator for async test functions."""
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


# Test data generators
def generate_test_texts(count: int, include_cards: bool = True, card_ratio: float = 0.3) -> List[str]:
    """Generate test texts with optional credit card numbers."""
    texts = []
    cards = [
        "4111111111111111",
        "4242424242424242",
        "5500000000000004",
        "378282246310005",
        "6011111111111117"
    ]

    for i in range(count):
        if include_cards and random.random() < card_ratio:
            card = random.choice(cards)
            texts.append(f"Transaction: ${random.randint(10, 1000)} - Card: {card}")
        else:
            texts.append(f"Log entry {i}: Processing completed successfully")

    return texts


# Database fixtures for integration tests
@pytest.fixture(scope="session")
def test_database():
    """Create a test database for integration tests."""
    import sqlite3
    from contextlib import contextmanager

    db_path = Path(tempfile.mkdtemp()) / "test.db"

    @contextmanager
    def get_connection():
        conn = sqlite3.connect(str(db_path))
        try:
            yield conn
        finally:
            conn.close()

    # Initialize database
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                detection_result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                confidence REAL,
                skill_used TEXT
            )
        """)
        conn.commit()

    yield get_connection

    # Cleanup
    os.unlink(db_path)


# Mock external services
@pytest.fixture
def mock_presidio_services():
    """Mock Presidio services for testing."""
    with patch('requests.get') as mock_get:
        # Mock analyzer health check
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "healthy"}

        yield mock_get


@pytest.fixture
def mock_claude_api():
    """Mock Claude API for testing."""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "def detect(text): return []"}]
        }
        mock_post.return_value = mock_response

        yield mock_post


# Logging configuration for tests
@pytest.fixture(autouse=True)
def configure_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


# Skip conditions
def skip_if_no_internet():
    """Skip test if internet is not available."""
    try:
        import urllib.request
        urllib.request.urlopen('http://www.google.com', timeout=1)
        return False
    except:
        return True


def skip_if_no_docker():
    """Skip test if Docker is not available."""
    try:
        import subprocess
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
        return False
    except:
        return True


# Parallel test execution support
def get_worker_count() -> int:
    """Get number of workers for parallel test execution."""
    try:
        return min(multiprocessing.cpu_count(), 4)  # Max 4 workers
    except:
        return 1


# Custom assertions
def assert_resource_constraints_met(metrics: Dict[str, float],
                                  constraints: ResourceConstraints) -> None:
    """Assert that resource constraints are met."""
    if constraints.max_cpu_percent:
        assert metrics["cpu_percent"] <= constraints.max_cpu_percent, \
            f"CPU usage {metrics['cpu_percent']} exceeds limit {constraints.max_cpu_percent}"

    if constraints.max_memory_percent:
        assert metrics["memory_percent"] <= constraints.max_memory_percent, \
            f"Memory usage {metrics['memory_percent']} exceeds limit {constraints.max_memory_percent}"


def assert_plugin_compatibility(plugin_manager: PluginManager,
                             plugin_name: str) -> None:
    """Assert that a plugin is compatible and loaded correctly."""
    plugin_info = plugin_manager.plugins.get(plugin_name)
    assert plugin_info is not None, f"Plugin {plugin_name} not found"
    assert plugin_info.status.value == "active", f"Plugin {plugin_name} not active"
    assert plugin_info.instance is not None, f"Plugin {plugin_name} has no instance"