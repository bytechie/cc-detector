"""
Resource-Aware Adaptive Learning System

This module enables the AI agent to adapt to resource constraints by:
- Monitoring resource usage in real-time
- Optimizing processing strategies under constraints
- Learning the best approaches for different resource scenarios
- Dynamically adjusting algorithms and skill selection
- Implementing intelligent resource allocation and scheduling
"""

import os
import psutil
import time
import threading
import json
import asyncio
import statistics
import gc
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import pickle
import hashlib


class ResourceType(Enum):
    """Types of resources to monitor and manage"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    GPU = "gpu"
    PROCESSES = "processes"
    THREADS = "threads"


class ConstraintLevel(Enum):
    """Levels of resource constraints"""
    NONE = "none"          # No constraints
    LOW = "low"            # Mild constraints
    MEDIUM = "medium"       # Moderate constraints
    HIGH = "high"          # Severe constraints
    CRITICAL = "critical"   # Extremely constrained


class OptimizationStrategy(Enum):
    """Resource optimization strategies"""
    SEQUENTIAL = "sequential"           # Process one item at a time
    BATCH_OPTIMIZED = "batch_optimized" # Optimize batch sizes
    PARALLEL_LIMITED = "parallel_limited" # Limited parallelization
    SKILL_PRIORITY = "skill_priority"   # Prioritize high-impact skills
    ADAPTIVE_SAMPLING = "adaptive_sampling" # Sample data adaptively
    CACHING_AGGRESSIVE = "caching_aggressive" # Aggressive caching
    OFFLOAD_EXTERNAL = "offload_external"   # Offload to external services


@dataclass
class ResourceMetrics:
    """Current resource usage metrics"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float
    active_threads: int
    active_processes: int
    gpu_utilization: float = 0.0
    gpu_memory_mb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResourceConstraints:
    """Resource constraint configuration"""
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 80.0
    max_memory_mb: Optional[float] = None
    max_threads: Optional[int] = None
    max_processes: Optional[int] = None
    max_batch_size: int = 1000
    max_concurrent_tasks: int = 4
    disk_io_limit_mb_per_sec: Optional[float] = None
    network_io_limit_mb_per_sec: Optional[float] = None
    enable_gpu: bool = False
    enable_offloading: bool = False

    def get_constraint_level(self, current_metrics: ResourceMetrics) -> ConstraintLevel:
        """Determine current constraint level"""
        cpu_ratio = current_metrics.cpu_percent / self.max_cpu_percent if self.max_cpu_percent else 0
        memory_ratio = current_metrics.memory_percent / self.max_memory_percent if self.max_memory_percent else 0

        max_ratio = max(cpu_ratio, memory_ratio)

        if max_ratio < 0.5:
            return ConstraintLevel.NONE
        elif max_ratio < 0.7:
            return ConstraintLevel.LOW
        elif max_ratio < 0.9:
            return ConstraintLevel.MEDIUM
        elif max_ratio < 1.1:
            return ConstraintLevel.HIGH
        else:
            return ConstraintLevel.CRITICAL


@dataclass
class ProcessingTask:
    """Represents a data processing task"""
    task_id: str
    data: Any
    priority: int = 0
    estimated_cpu_cost: float = 1.0
    estimated_memory_cost: float = 1.0
    skills_required: List[str] = field(default_factory=list)
    deadline: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)

    def __lt__(self, other):
        # For priority queue ordering (lower priority number = higher priority)
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.created_at < other.created_at


@dataclass
class OptimizationResult:
    """Result of resource optimization"""
    strategy: OptimizationStrategy
    original_processing_time: float
    optimized_processing_time: float
    resource_savings: Dict[str, float]
    accuracy_impact: float
    success_rate: float
    recommendation: str


class ResourceMonitor:
    """Real-time resource monitoring system"""

    def __init__(self, sampling_interval: float = 1.0):
        self.sampling_interval = sampling_interval
        self.metrics_history: deque = deque(maxlen=1000)  # Keep last 1000 samples
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable[[ResourceMetrics], None]] = []

    def start_monitoring(self):
        """Start background resource monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)

                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        callback(metrics)
                    except Exception:
                        pass  # Don't let callback errors stop monitoring

                time.sleep(self.sampling_interval)
            except Exception as e:
                print(f"Resource monitoring error: {e}")
                time.sleep(self.sampling_interval)

    def _collect_metrics(self) -> ResourceMetrics:
        """Collect current system metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=None)

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_mb = memory.available / (1024 * 1024)
        memory_used_mb = memory.used / (1024 * 1024)

        # Disk I/O metrics
        disk_io = psutil.disk_io_counters()
        disk_io_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0.0
        disk_io_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0.0

        # Network I/O metrics
        net_io = psutil.net_io_counters()
        network_io_sent_mb = net_io.bytes_sent / (1024 * 1024) if net_io else 0.0
        network_io_recv_mb = net_io.bytes_recv / (1024 * 1024) if net_io else 0.0

        # Process and thread counts
        active_processes = len(psutil.pids())
        active_threads = threading.active_count()

        # GPU metrics (if available)
        gpu_utilization = 0.0
        gpu_memory_mb = 0.0
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Use first GPU
                gpu_utilization = gpu.load * 100
                gpu_memory_mb = gpu.memoryUsed
        except ImportError:
            pass  # GPU monitoring not available

        return ResourceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_mb=memory_available_mb,
            memory_used_mb=memory_used_mb,
            disk_io_read_mb=disk_io_read_mb,
            disk_io_write_mb=disk_io_write_mb,
            network_io_sent_mb=network_io_sent_mb,
            network_io_recv_mb=network_io_recv_mb,
            active_threads=active_threads,
            active_processes=active_processes,
            gpu_utilization=gpu_utilization,
            gpu_memory_mb=gpu_memory_mb
        )

    def get_current_metrics(self) -> Optional[ResourceMetrics]:
        """Get the most recent metrics"""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_average_metrics(self, duration_minutes: float = 5.0) -> Optional[ResourceMetrics]:
        """Get average metrics over specified duration"""
        if not self.metrics_history:
            return None

        cutoff_time = time.time() - (duration_minutes * 60)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]

        if not recent_metrics:
            return None

        # Calculate averages
        avg_cpu = statistics.mean(m.cpu_percent for m in recent_metrics)
        avg_memory = statistics.mean(m.memory_percent for m in recent_metrics)
        avg_threads = statistics.mean(m.active_threads for m in recent_metrics)

        # Use latest values for non-averaged metrics
        latest = recent_metrics[-1]

        return ResourceMetrics(
            timestamp=latest.timestamp,
            cpu_percent=avg_cpu,
            memory_percent=avg_memory,
            memory_available_mb=latest.memory_available_mb,
            memory_used_mb=latest.memory_used_mb,
            disk_io_read_mb=latest.disk_io_read_mb,
            disk_io_write_mb=latest.disk_io_write_mb,
            network_io_sent_mb=latest.network_io_sent_mb,
            network_io_recv_mb=latest.network_io_recv_mb,
            active_threads=int(avg_threads),
            active_processes=latest.active_processes,
            gpu_utilization=latest.gpu_utilization,
            gpu_memory_mb=latest.gpu_memory_mb
        )

    def add_callback(self, callback: Callable[[ResourceMetrics], None]):
        """Add a callback to be called when metrics are collected"""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[ResourceMetrics], None]):
        """Remove a callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)


class ResourceOptimizer:
    """Intelligent resource optimization engine"""

    def __init__(self, constraints: ResourceConstraints):
        self.constraints = constraints
        self.performance_history: Dict[str, List[OptimizationResult]] = {}
        self.strategy_performance: Dict[OptimizationStrategy, float] = {
            strategy: 0.5 for strategy in OptimizationStrategy
        }
        self.learning_rate = 0.1

    def select_optimal_strategy(self,
                              current_metrics: ResourceMetrics,
                              task_count: int,
                              estimated_complexity: float = 1.0) -> OptimizationStrategy:
        """Select the best optimization strategy based on current conditions"""
        constraint_level = self.constraints.get_constraint_level(current_metrics)

        # Base strategy selection on constraint level
        if constraint_level == ConstraintLevel.NONE:
            # No constraints - can use parallel processing
            if task_count > 10:
                return OptimizationStrategy.PARALLEL_LIMITED
            else:
                return OptimizationStrategy.BATCH_OPTIMIZED

        elif constraint_level == ConstraintLevel.LOW:
            # Low constraints - moderate optimization
            return OptimizationStrategy.BATCH_OPTIMIZED

        elif constraint_level == ConstraintLevel.MEDIUM:
            # Medium constraints - prioritize important tasks
            return OptimizationStrategy.SKILL_PRIORITY

        elif constraint_level == ConstraintLevel.HIGH:
            # High constraints - aggressive caching and sampling
            if task_count > 100:
                return OptimizationStrategy.ADAPTIVE_SAMPLING
            else:
                return OptimizationStrategy.CACHING_AGGRESSIVE

        else:  # CRITICAL
            # Critical constraints - minimal processing
            return OptimizationStrategy.SEQUENTIAL

    def optimize_batch_size(self,
                          current_metrics: ResourceMetrics,
                          base_batch_size: int) -> int:
        """Dynamically adjust batch size based on resources"""
        constraint_level = self.constraints.get_constraint_level(current_metrics)

        if constraint_level == ConstraintLevel.NONE:
            return min(base_batch_size * 2, self.constraints.max_batch_size)
        elif constraint_level == ConstraintLevel.LOW:
            return min(base_batch_size * 1.5, self.constraints.max_batch_size)
        elif constraint_level == ConstraintLevel.MEDIUM:
            return base_batch_size
        elif constraint_level == ConstraintLevel.HIGH:
            return max(base_batch_size // 2, 10)
        else:  # CRITICAL
            return max(base_batch_size // 4, 1)

    def optimize_concurrency(self,
                           current_metrics: ResourceMetrics,
                           task_count: int) -> int:
        """Optimize number of concurrent tasks based on resources"""
        constraint_level = self.constraints.get_constraint_level(current_metrics)

        # Base concurrency on CPU cores and current load
        cpu_cores = mp.cpu_count()
        cpu_load_factor = max(0.1, 1.0 - (current_metrics.cpu_percent / 100.0))
        memory_load_factor = max(0.1, 1.0 - (current_metrics.memory_percent / 100.0))

        base_concurrency = max(1, int(cpu_cores * cpu_load_factor * memory_load_factor))

        if constraint_level == ConstraintLevel.NONE:
            return min(base_concurrency * 2, self.constraints.max_concurrent_tasks, task_count)
        elif constraint_level == ConstraintLevel.LOW:
            return min(base_concurrency, self.constraints.max_concurrent_tasks, task_count)
        elif constraint_level == ConstraintLevel.MEDIUM:
            return max(1, min(base_concurrency // 2, task_count))
        elif constraint_level == ConstraintLevel.HIGH:
            return max(1, min(base_concurrency // 4, task_count))
        else:  # CRITICAL
            return 1

    def update_strategy_performance(self,
                                  strategy: OptimizationStrategy,
                                  result: OptimizationResult):
        """Update strategy performance based on results"""
        if strategy not in self.performance_history:
            self.performance_history[strategy] = []

        self.performance_history[strategy].append(result)

        # Update running average performance
        recent_results = self.performance_history[strategy][-10:]  # Last 10 results
        if recent_results:
            avg_efficiency = statistics.mean([
                r.optimized_processing_time / r.original_processing_time
                for r in recent_results
            ])

            # Apply learning rate
            self.strategy_performance[strategy] = (
                (1 - self.learning_rate) * self.strategy_performance[strategy] +
                self.learning_rate * avg_efficiency
            )

    def get_optimization_recommendations(self,
                                       current_metrics: ResourceMetrics) -> List[str]:
        """Get recommendations for optimization based on current state"""
        recommendations = []
        constraint_level = self.constraints.get_constraint_level(current_metrics)

        if current_metrics.memory_percent > 80:
            recommendations.append("High memory usage detected - enable aggressive garbage collection")
            recommendations.append("Consider processing data in smaller chunks")

        if current_metrics.cpu_percent > 80:
            recommendations.append("High CPU usage detected - reduce parallel processing")
            recommendations.append("Consider offloading to external services")

        if current_metrics.active_threads > 50:
            recommendations.append("High thread count detected - implement thread pooling")

        if constraint_level in [ConstraintLevel.HIGH, ConstraintLevel.CRITICAL]:
            recommendations.append("System under high constraints - enable adaptive sampling")
            recommendations.append("Prioritize high-impact tasks only")

        return recommendations


class AdaptiveProcessingEngine:
    """Main adaptive processing engine that coordinates everything"""

    def __init__(self,
                 constraints: Optional[ResourceConstraints] = None,
                 adaptive_manager=None):
        self.constraints = constraints or ResourceConstraints()
        self.adaptive_manager = adaptive_manager

        # Core components
        self.resource_monitor = ResourceMonitor()
        self.resource_optimizer = ResourceOptimizer(self.constraints)

        # Task management
        self.task_queue = asyncio.PriorityQueue()
        self.processing_tasks: Dict[str, ProcessingTask] = {}
        self.completed_tasks: List[ProcessingTask] = []

        # Execution state
        self.is_processing = False
        self.current_strategy = OptimizationStrategy.SEQUENTIAL
        self.executor: Optional[ThreadPoolExecutor] = None

        # Performance tracking
        self.processing_history: List[Dict[str, Any]] = []
        self.performance_cache: Dict[str, Any] = {}

        # Start monitoring
        self.resource_monitor.start_monitoring()
        self.resource_monitor.add_callback(self._on_resource_update)

    def _on_resource_update(self, metrics: ResourceMetrics):
        """Handle resource metric updates"""
        # Check if we need to adapt our strategy
        if self.is_processing:
            new_strategy = self.resource_optimizer.select_optimal_strategy(
                metrics,
                len(self.processing_tasks)
            )

            if new_strategy != self.current_strategy:
                print(f"Adapting strategy: {self.current_strategy.value} -> {new_strategy.value}")
                self.current_strategy = new_strategy

    async def submit_tasks(self, tasks: List[ProcessingTask]) -> List[str]:
        """Submit multiple tasks for processing"""
        task_ids = []

        for task in tasks:
            self.processing_tasks[task.task_id] = task
            await self.task_queue.put((task.priority, task.created_at, task))
            task_ids.append(task.task_id)

        return task_ids

    async def process_with_constraints(self,
                                     data_items: List[Any],
                                     processing_func: Callable,
                                     **kwargs) -> Tuple[List[Any], Dict[str, Any]]:
        """Process data items with resource constraint awareness"""
        start_time = time.time()

        current_metrics = self.resource_monitor.get_current_metrics()
        if not current_metrics:
            current_metrics = self.resource_monitor._collect_metrics()

        # Select optimal strategy
        strategy = self.resource_optimizer.select_optimal_strategy(
            current_metrics,
            len(data_items)
        )
        self.current_strategy = strategy

        # Optimize processing parameters
        batch_size = self.resource_optimizer.optimize_batch_size(
            current_metrics,
            min(100, len(data_items))
        )

        concurrency = self.resource_optimizer.optimize_concurrency(
            current_metrics,
            len(data_items)
        )

        # Process based on strategy
        if strategy == OptimizationStrategy.SEQUENTIAL:
            results = await self._process_sequential(data_items, processing_func, **kwargs)
        elif strategy == OptimizationStrategy.BATCH_OPTIMIZED:
            results = await self._process_batch_optimized(data_items, processing_func, batch_size, **kwargs)
        elif strategy == OptimizationStrategy.PARALLEL_LIMITED:
            results = await self._process_parallel_limited(data_items, processing_func, concurrency, **kwargs)
        elif strategy == OptimizationStrategy.SKILL_PRIORITY:
            results = await self._process_skill_priority(data_items, processing_func, **kwargs)
        elif strategy == OptimizationStrategy.ADAPTIVE_SAMPLING:
            results = await self._process_adaptive_sampling(data_items, processing_func, **kwargs)
        elif strategy == OptimizationStrategy.CACHING_AGGRESSIVE:
            results = await self._process_caching_aggressive(data_items, processing_func, **kwargs)
        elif strategy == OptimizationStrategy.OFFLOAD_EXTERNAL:
            results = await self._process_offload_external(data_items, processing_func, **kwargs)
        else:
            results = await self._process_sequential(data_items, processing_func, **kwargs)

        # Record performance
        processing_time = time.time() - start_time
        performance_info = {
            "strategy": strategy.value,
            "data_count": len(data_items),
            "processing_time": processing_time,
            "throughput": len(data_items) / processing_time,
            "batch_size": batch_size,
            "concurrency": concurrency,
            "resource_metrics": current_metrics.to_dict(),
            "timestamp": time.time()
        }

        self.processing_history.append(performance_info)

        return results, performance_info

    async def _process_sequential(self,
                                data_items: List[Any],
                                processing_func: Callable,
                                **kwargs) -> List[Any]:
        """Process items sequentially (lowest resource usage)"""
        results = []

        for item in data_items:
            try:
                result = await self._execute_with_resource_management(
                    processing_func, item, **kwargs
                )
                results.append(result)
            except Exception as e:
                print(f"Sequential processing error: {e}")
                results.append(None)

        return results

    async def _process_batch_optimized(self,
                                     data_items: List[Any],
                                     processing_func: Callable,
                                     batch_size: int,
                                     **kwargs) -> List[Any]:
        """Process items in optimized batches"""
        results = []

        for i in range(0, len(data_items), batch_size):
            batch = data_items[i:i + batch_size]

            try:
                batch_results = await self._execute_with_resource_management(
                    processing_func, batch, **kwargs
                )
                results.extend(batch_results if isinstance(batch_results, list) else [batch_results])
            except Exception as e:
                print(f"Batch processing error: {e}")
                results.extend([None] * len(batch))

        return results

    async def _process_parallel_limited(self,
                                      data_items: List[Any],
                                      processing_func: Callable,
                                      concurrency: int,
                                      **kwargs) -> List[Any]:
        """Process items with limited parallelization"""
        if not self.executor or self.executor._max_workers != concurrency:
            if self.executor:
                self.executor.shutdown(wait=False)
            self.executor = ThreadPoolExecutor(max_workers=concurrency)

        loop = asyncio.get_event_loop()

        # Create tasks for parallel processing
        tasks = []
        for item in data_items:
            task = loop.run_in_executor(
                self.executor,
                lambda x=item: asyncio.run(self._execute_with_resource_management(
                    processing_func, x, **kwargs
                ))
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Parallel processing error: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)

        return processed_results

    async def _process_skill_priority(self,
                                    data_items: List[Any],
                                    processing_func: Callable,
                                    **kwargs) -> List[Any]:
        """Process items using skill priority (adaptive skills integration)"""
        if not self.adaptive_manager:
            return await self._process_sequential(data_items, processing_func, **kwargs)

        results = []

        for item in data_items:
            try:
                # Check which skills are most effective for this type of data
                item_str = str(item) if isinstance(item, (str, dict)) else ""
                best_skills = self._get_best_skills_for_item(item_str)

                # Use only the best skills to conserve resources
                modified_kwargs = kwargs.copy()
                modified_kwargs['preferred_skills'] = best_skills

                result = await self._execute_with_resource_management(
                    processing_func, item, **modified_kwargs
                )
                results.append(result)

            except Exception as e:
                print(f"Skill priority processing error: {e}")
                results.append(None)

        return results

    async def _process_adaptive_sampling(self,
                                       data_items: List[Any],
                                       processing_func: Callable,
                                       **kwargs) -> List[Any]:
        """Process using adaptive sampling for large datasets"""
        total_items = len(data_items)

        # Determine sample size based on resources
        current_metrics = self.resource_monitor.get_current_metrics()
        constraint_level = self.constraints.get_constraint_level(current_metrics)

        if constraint_level == ConstraintLevel.CRITICAL:
            sample_ratio = 0.1  # Process only 10%
        elif constraint_level == ConstraintLevel.HIGH:
            sample_ratio = 0.25  # Process 25%
        else:
            sample_ratio = 0.5   # Process 50%

        sample_size = max(1, min(total_items, int(total_items * sample_ratio)))

        # Sample items strategically (first + random + last)
        if total_items <= sample_size:
            sampled_items = data_items
        else:
            # Take first 20%, middle random, and last 20%
            first_end = max(1, sample_size // 5)
            last_start = max(first_end, total_items - sample_size // 5)
            middle_sample = sample_size - first_end - (total_items - last_start)

            sampled_items = (
                data_items[:first_end] +
                data_items[first_end:last_start][::max(1, (last_start - first_end) // max(1, middle_sample))] +
                data_items[last_start:]
            )

        # Process the sample
        sampled_results = await self._process_sequential(
            sampled_items, processing_func, **kwargs
        )

        # Extrapolate results for full dataset
        return self._extrapolate_results(sampled_items, sampled_results, data_items)

    async def _process_caching_aggressive(self,
                                        data_items: List[Any],
                                        processing_func: Callable,
                                        **kwargs) -> List[Any]:
        """Process with aggressive caching to minimize redundant work"""
        results = []

        for item in data_items:
            # Create cache key for this item
            cache_key = self._create_cache_key(item, processing_func.__name__)

            # Check cache first
            if cache_key in self.performance_cache:
                cached_result = self.performance_cache[cache_key]
                results.append(cached_result)
                continue

            # Process and cache result
            try:
                result = await self._execute_with_resource_management(
                    processing_func, item, **kwargs
                )

                # Cache the result (with size limit)
                if len(self.performance_cache) < 1000:  # Limit cache size
                    self.performance_cache[cache_key] = result

                results.append(result)

            except Exception as e:
                print(f"Caching processing error: {e}")
                results.append(None)

        return results

    async def _process_offload_external(self,
                                      data_items: List[Any],
                                      processing_func: Callable,
                                      **kwargs) -> List[Any]:
        """Process by offloading to external services (if available)"""
        # This is a placeholder for external service integration
        # In a real implementation, this could offload to cloud services

        # For now, fall back to sequential processing
        print("External offloading not available, using sequential processing")
        return await self._process_sequential(data_items, processing_func, **kwargs)

    async def _execute_with_resource_management(self,
                                             processing_func: Callable,
                                             *args, **kwargs) -> Any:
        """Execute function with resource monitoring and management"""
        # Check resources before execution
        current_metrics = self.resource_monitor.get_current_metrics()
        if current_metrics:
            constraint_level = self.constraints.get_constraint_level(current_metrics)

            # If under critical constraints, wait for resources to free up
            if constraint_level == ConstraintLevel.CRITICAL:
                await self._wait_for_resources()

            # Force garbage collection if memory is high
            if current_metrics.memory_percent > 85:
                gc.collect()

        # Execute the function
        try:
            if asyncio.iscoroutinefunction(processing_func):
                return await processing_func(*args, **kwargs)
            else:
                return processing_func(*args, **kwargs)
        except Exception as e:
            print(f"Execution error: {e}")
            raise

    async def _wait_for_resources(self, timeout_seconds: float = 30.0) -> bool:
        """Wait for resources to become available"""
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            current_metrics = self.resource_monitor.get_current_metrics()
            if current_metrics:
                constraint_level = self.constraints.get_constraint_level(current_metrics)
                if constraint_level != ConstraintLevel.CRITICAL:
                    return True

            await asyncio.sleep(1.0)

        return False

    def _get_best_skills_for_item(self, item_text: str) -> List[str]:
        """Get the most effective skills for a specific item"""
        if not self.adaptive_manager:
            return []

        # Simple heuristic: return top performing skills
        best_skills = []
        for skill_name, perf in self.adaptive_manager.performance_metrics.items():
            if perf.f1_score > 0.7:  # Only high-performing skills
                best_skills.append(skill_name)

        return best_skills[:3]  # Return top 3 skills

    def _create_cache_key(self, item: Any, func_name: str) -> str:
        """Create a cache key for an item and function"""
        item_str = str(item) if isinstance(item, (str, dict, int, float)) else pickle.dumps(item)
        combined = f"{func_name}:{item_str}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _extrapolate_results(self,
                           sampled_items: List[Any],
                           sampled_results: List[Any],
                           all_items: List[Any]) -> List[Any]:
        """Extrapolate sampled results to full dataset"""
        # Simple extrapolation - in practice, this could be more sophisticated
        if len(sampled_items) == len(all_items):
            return sampled_results

        # For detection tasks, we might want to be conservative and assume no detections
        # for non-sampled items to avoid false positives
        extrapolated_results = []
        sample_index = 0

        for i, item in enumerate(all_items):
            if sample_index < len(sampled_items) and item == sampled_items[sample_index]:
                extrapolated_results.append(sampled_results[sample_index])
                sample_index += 1
            else:
                # For non-sampled items, return a conservative result
                extrapolated_results.append([] if isinstance(sampled_results[0] if sampled_results else None, list) else None)

        return extrapolated_results

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        if not self.processing_history:
            return {}

        # Calculate statistics
        processing_times = [h['processing_time'] for h in self.processing_history]
        throughputs = [h['throughput'] for h in self.processing_history]

        strategy_counts = defaultdict(int)
        for h in self.processing_history:
            strategy_counts[h['strategy']] += 1

        return {
            "total_processed": sum(h['data_count'] for h in self.processing_history),
            "avg_processing_time": statistics.mean(processing_times),
            "avg_throughput": statistics.mean(throughputs),
            "peak_throughput": max(throughputs),
            "total_strategies_used": len(strategy_counts),
            "strategy_distribution": dict(strategy_counts),
            "cache_hit_rate": len(self.performance_cache) / max(1, sum(h['data_count'] for h in self.processing_history)),
            "current_strategy": self.current_strategy.value,
            "resource_constraints": self.constraints.__dict__
        }

    def cleanup(self):
        """Clean up resources"""
        self.resource_monitor.stop_monitoring()
        if self.executor:
            self.executor.shutdown(wait=True)
        gc.collect()