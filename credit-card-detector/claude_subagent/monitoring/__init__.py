"""
Monitoring and Observability Stack

This module provides comprehensive monitoring and observability capabilities including:
- Metrics collection and export
- Distributed tracing
- Application performance monitoring (APM)
- Error tracking and alerting
- Log aggregation and analysis
- Health checks and status reporting
"""

import os
import time
import json
import logging
import traceback
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict, deque
import uuid
from contextlib import contextmanager

# Third-party monitoring libraries (optional)
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MetricEvent:
    """Metric event for tracking application performance"""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = None
    unit: str = ""
    description: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TraceEvent:
    """Trace event for distributed tracing"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    status: str
    tags: Dict[str, str] = None
    logs: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.logs is None:
            self.logs = []

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['duration_ms'] = (self.duration or 0) * 1000
        return result


@dataclass
class ErrorEvent:
    """Error event for tracking exceptions and failures"""
    error_id: str
    error_type: str
    message: str
    traceback_str: str
    timestamp: float
    context: Dict[str, Any] = None
    severity: str = "error"
    tags: Dict[str, str] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.tags is None:
            self.tags = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetricsCollector:
    """Collects and manages application metrics"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        if PROMETHEUS_AVAILABLE and enabled:
            self.registry = CollectorRegistry()
            self._init_prometheus_metrics()

    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prom_counters = {}
        self.prom_gauges = {}
        self.prom_histograms = {}

        # Default metrics
        self.prom_counters['requests_total'] = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )

        self.prom_histograms['request_duration'] = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )

        self.prom_gauges['active_connections'] = Gauge(
            'active_connections',
            'Number of active connections',
            registry=self.registry
        )

    def increment(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        if not self.enabled:
            return

        tag_key = self._make_tag_key(tags)
        key = f"{name}:{tag_key}"

        self.counters[key] += value

        event = MetricEvent(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            unit="count"
        )
        self.metrics[name].append(event)

        # Update Prometheus
        if PROMETHEUS_AVAILABLE and name in self.prom_counters:
            self.prom_counters[name].labels(**(tags or {})).inc(value)

    def gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric"""
        if not self.enabled:
            return

        tag_key = self._make_tag_key(tags)
        key = f"{name}:{tag_key}"

        self.gauges[key] = value

        event = MetricEvent(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            unit="value"
        )
        self.metrics[name].append(event)

        # Update Prometheus
        if PROMETHEUS_AVAILABLE and name in self.prom_gauges:
            self.prom_gauges[name].labels(**(tags or {})).set(value)

    def histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram metric"""
        if not self.enabled:
            return

        tag_key = self._make_tag_key(tags)
        key = f"{name}:{tag_key}"

        self.histograms[key].append(value)

        event = MetricEvent(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            unit="value"
        )
        self.metrics[name].append(event)

        # Update Prometheus
        if PROMETHEUS_AVAILABLE and name in self.prom_histograms:
            self.prom_histograms[name].labels(**(tags or {})).observe(value)

    def _make_tag_key(self, tags: Dict[str, str] = None) -> str:
        """Create a key from tags"""
        if not tags:
            return ""
        return ",".join(f"{k}={v}" for k, v in sorted(tags.items()))

    def get_metrics_summary(self, time_window: int = 300) -> Dict[str, Any]:
        """Get metrics summary for the last time_window seconds"""
        cutoff_time = time.time() - time_window
        summary = {}

        for name, events in self.metrics.items():
            recent_events = [e for e in events if e.timestamp >= cutoff_time]

            if recent_events:
                values = [e.value for e in recent_events]
                summary[name] = {
                    'count': len(values),
                    'sum': sum(values),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'latest': values[-1] if values else 0
                }

        return summary

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        if PROMETHEUS_AVAILABLE:
            return generate_latest(self.registry).decode('utf-8')
        return ""

    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()


class TracingManager:
    """Manages distributed tracing"""

    def __init__(self, enabled: bool = True, service_name: str = "credit-card-detector"):
        self.enabled = enabled
        self.service_name = service_name
        self.traces: Dict[str, TraceEvent] = {}
        self.active_spans: Dict[str, Any] = {}

        if OPENTELEMETRY_AVAILABLE and enabled:
            self._init_opentelemetry()

    def _init_opentelemetry(self):
        """Initialize OpenTelemetry"""
        # Set up tracing
        trace.set_tracer_provider(TracerProvider())
        self.tracer = trace.get_tracer(__name__)

        # Set up metrics
        self.meter = metrics.get_meter(__name__)

    @contextmanager
    def start_span(self, operation_name: str, tags: Dict[str, str] = None):
        """Start a new trace span"""
        if not self.enabled:
            yield None
            return

        span_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())

        # Create trace event
        trace_event = TraceEvent(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            operation_name=operation_name,
            start_time=time.time(),
            end_time=None,
            duration=None,
            status="started",
            tags=tags or {}
        )

        self.traces[span_id] = trace_event

        try:
            if OPENTELEMETRY_AVAILABLE:
                with self.tracer.start_as_current_span(operation_name) as span:
                    if tags:
                        for key, value in tags.items():
                            span.set_attribute(key, value)
                    yield span
            else:
                yield None

        except Exception as e:
            trace_event.status = "error"
            trace_event.logs.append(f"Error: {str(e)}")
            raise
        finally:
            trace_event.end_time = time.time()
            trace_event.duration = trace_event.end_time - trace_event.start_time
            trace_event.status = "completed"

    def add_span_log(self, span_id: str, message: str, level: str = "info"):
        """Add a log entry to a span"""
        if span_id in self.traces:
            self.traces[span_id].logs.append(f"[{level.upper()}] {message}")

    def get_trace_summary(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get trace summary for the last time_window seconds"""
        cutoff_time = time.time() - time_window
        recent_traces = {
            k: v for k, v in self.traces.items()
            if v.start_time >= cutoff_time
        }

        if not recent_traces:
            return {}

        durations = [t.duration for t in recent_traces.values() if t.duration]

        return {
            'total_traces': len(recent_traces),
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'min_duration': min(durations) if durations else 0,
            'operations': list(set(t.operation_name for t in recent_traces.values())),
            'status_counts': {
                status: sum(1 for t in recent_traces.values() if t.status == status)
                for status in set(t.status for t in recent_traces.values())
            }
        }


class ErrorTracker:
    """Tracks and manages errors and exceptions"""

    def __init__(self, enabled: bool = True, sentry_dsn: str = None):
        self.enabled = enabled
        self.errors: deque = deque(maxlen=1000)
        self.error_counts: Dict[str, int] = defaultdict(int)

        if SENTRY_AVAILABLE and enabled and sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=0.1,
                environment=os.getenv("ENVIRONMENT", "development")
            )

    def capture_exception(self, exception: Exception, context: Dict[str, Any] = None, tags: Dict[str, str] = None):
        """Capture and track an exception"""
        if not self.enabled:
            return

        error_id = str(uuid.uuid4())
        error_type = type(exception).__name__

        error_event = ErrorEvent(
            error_id=error_id,
            error_type=error_type,
            message=str(exception),
            traceback_str=traceback.format_exc(),
            timestamp=time.time(),
            context=context or {},
            tags=tags or {}
        )

        self.errors.append(error_event)
        self.error_counts[error_type] += 1

        # Send to Sentry if available
        if SENTRY_AVAILABLE:
            sentry_sdk.capture_exception(exception)

        logger.error(f"Exception captured: {error_type} - {str(exception)}")

    def capture_message(self, message: str, level: str = "info", context: Dict[str, Any] = None):
        """Capture a message as an error event"""
        if not self.enabled:
            return

        error_id = str(uuid.uuid4())

        error_event = ErrorEvent(
            error_id=error_id,
            error_type="message",
            message=message,
            traceback_str="",
            timestamp=time.time(),
            context=context or {},
            severity=level
        )

        if level in ["error", "critical", "warning"]:
            self.errors.append(error_event)
            self.error_counts["message"] += 1

        # Send to Sentry if available
        if SENTRY_AVAILABLE:
            if level == "critical":
                sentry_sdk.capture_message(message, level="error")
            elif level == "error":
                sentry_sdk.capture_message(message, level="error")

        getattr(logger, level)(f"Message captured: {message}")

    def get_error_summary(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get error summary for the last time_window seconds"""
        cutoff_time = time.time() - time_window
        recent_errors = [e for e in self.errors if e.timestamp >= cutoff_time]

        if not recent_errors:
            return {}

        error_types = defaultdict(int)
        severity_counts = defaultdict(int)

        for error in recent_errors:
            error_types[error.error_type] += 1
            severity_counts[error.severity] += 1

        return {
            'total_errors': len(recent_errors),
            'error_types': dict(error_types),
            'severity_counts': dict(severity_counts),
            'most_common_error': max(error_types.items(), key=lambda x: x[1])[0] if error_types else None,
            'recent_errors': [
                {
                    'type': e.error_type,
                    'message': e.message,
                    'timestamp': e.timestamp,
                    'severity': e.severity
                }
                for e in recent_errors[-10:]  # Last 10 errors
            ]
        }


class HealthChecker:
    """Health check manager"""

    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.last_results: Dict[str, Dict[str, Any]] = {}

    def register_check(self, name: str, check_func: Callable, timeout: float = 10.0):
        """Register a health check function"""
        self.checks[name] = {
            'func': check_func,
            'timeout': timeout
        }

    def run_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check"""
        if name not in self.checks:
            return {
                'name': name,
                'status': 'error',
                'message': f'Health check {name} not found',
                'timestamp': time.time()
            }

        check_info = self.checks[name]
        start_time = time.time()

        try:
            result = check_info['func']()
            duration = time.time() - start_time

            self.last_results[name] = {
                'name': name,
                'status': 'healthy' if result else 'unhealthy',
                'message': 'Health check passed' if result else 'Health check failed',
                'timestamp': time.time(),
                'duration': duration,
                'details': result
            }

        except Exception as e:
            duration = time.time() - start_time

            self.last_results[name] = {
                'name': name,
                'status': 'error',
                'message': str(e),
                'timestamp': time.time(),
                'duration': duration,
                'error': traceback.format_exc()
            }

        return self.last_results[name]

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {}
        overall_status = 'healthy'

        for name in self.checks:
            results[name] = self.run_check(name)

            if results[name]['status'] != 'healthy':
                overall_status = 'unhealthy'

        return {
            'status': overall_status,
            'timestamp': time.time(),
            'checks': results
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current health status (without re-running checks)"""
        if not self.last_results:
            return {'status': 'unknown', 'message': 'No health checks run yet'}

        overall_status = 'healthy'
        for result in self.last_results.values():
            if result['status'] != 'healthy':
                overall_status = 'unhealthy'
                break

        return {
            'status': overall_status,
            'timestamp': time.time(),
            'checks': self.last_results
        }


class MonitoringManager:
    """Main monitoring and observability manager"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

        # Initialize components
        self.metrics = MetricsCollector(
            enabled=self.config.get('metrics_enabled', True)
        )

        self.tracing = TracingManager(
            enabled=self.config.get('tracing_enabled', True),
            service_name=self.config.get('service_name', 'credit-card-detector')
        )

        self.errors = ErrorTracker(
            enabled=self.config.get('error_tracking_enabled', True),
            sentry_dsn=self.config.get('sentry_dsn')
        )

        self.health = HealthChecker()

        # Register default health checks
        self._register_default_health_checks()

    def _register_default_health_checks(self):
        """Register default health checks"""
        self.health.register_check('application', self._check_application_health)
        self.health.register_check('database', self._check_database_health)
        self.health.register_check('redis', self._check_redis_health)
        self.health.register_check('disk_space', self._check_disk_space)

    def _check_application_health(self) -> bool:
        """Check application health"""
        try:
            # Check if we can import and access key modules
            import claude_subagent
            return True
        except Exception:
            return False

    def _check_database_health(self) -> bool:
        """Check database connectivity"""
        try:
            # Add your database health check logic here
            return True
        except Exception:
            return False

    def _check_redis_health(self) -> bool:
        """Check Redis connectivity"""
        try:
            # Add your Redis health check logic here
            return True
        except Exception:
            return False

    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space"""
        import shutil
        total, used, free = shutil.disk_usage('/')

        return {
            'total_gb': total // (1024**3),
            'used_gb': used // (1024**3),
            'free_gb': free // (1024**3),
            'usage_percent': (used / total) * 100
        }

    def get_full_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status"""
        return {
            'timestamp': time.time(),
            'metrics': self.metrics.get_metrics_summary(),
            'tracing': self.tracing.get_trace_summary(),
            'errors': self.errors.get_error_summary(),
            'health': self.health.get_status(),
            'system': self._get_system_info()
        }

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        import psutil
        import platform

        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total // (1024**3),  # GB
            'disk_total': psutil.disk_usage('/').total // (1024**3),  # GB
            'uptime': time.time() - psutil.boot_time()
        }

    def create_decorators(self):
        """Create monitoring decorators"""

        def monitor_performance(operation_name: str = None):
            """Decorator to monitor function performance"""
            def decorator(func):
                name = operation_name or f"{func.__module__}.{func.__name__}"

                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    with self.metrics.histogram(f"{name}_duration", tags={'function': name}):
                        start_time = time.time()
                        try:
                            self.metrics.increment(f"{name}_calls", tags={'function': name})
                            result = func(*args, **kwargs)
                            self.metrics.increment(f"{name}_success", tags={'function': name})
                            return result
                        except Exception as e:
                            self.metrics.increment(f"{name}_errors", tags={'function': name})
                            self.errors.capture_exception(e, context={'function': name})
                            raise
                        finally:
                            duration = time.time() - start_time
                            self.metrics.histogram(f"{name}_duration", duration, tags={'function': name})

                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with self.metrics.histogram(f"{name}_duration", tags={'function': name}):
                        start_time = time.time()
                        try:
                            self.metrics.increment(f"{name}_calls", tags={'function': name})
                            result = await func(*args, **kwargs)
                            self.metrics.increment(f"{name}_success", tags={'function': name})
                            return result
                        except Exception as e:
                            self.metrics.increment(f"{name}_errors", tags={'function': name})
                            self.errors.capture_exception(e, context={'function': name})
                            raise
                        finally:
                            duration = time.time() - start_time
                            self.metrics.histogram(f"{name}_duration", duration, tags={'function': name})

                return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
            return decorator

        def trace_operation(operation_name: str = None):
            """Decorator to trace function execution"""
            def decorator(func):
                name = operation_name or f"{func.__module__}.{func.__name__}"

                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    with self.tracing.start_span(name, tags={'function': name}):
                        return func(*args, **kwargs)

                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with self.tracing.start_span(name, tags={'function': name}):
                        return await func(*args, **kwargs)

                return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
            return decorator

        return {
            'monitor_performance': monitor_performance,
            'trace_operation': trace_operation
        }


# Global monitoring manager instance
monitoring_manager = MonitoringManager()