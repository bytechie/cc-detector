"""
Performance Prediction and Optimization Module

This module provides machine learning-based performance prediction
and intelligent optimization recommendations for resource-constrained processing.
"""

import time
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import pickle
import os
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import threading

from . import ResourceMetrics, ResourceConstraints, OptimizationStrategy


@dataclass
class PerformanceRecord:
    """Historical performance record for ML training"""
    timestamp: float
    data_size: int
    cpu_usage: float
    memory_usage: float
    thread_count: int
    strategy: str
    processing_time: float
    throughput: float
    success_rate: float
    batch_size: int
    concurrency: int
    skill_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_features(self) -> List[float]:
        """Convert to feature vector for ML models"""
        return [
            self.data_size,
            self.cpu_usage,
            self.memory_usage,
            self.thread_count,
            self.batch_size,
            self.concurrency,
            self.skill_count,
            # Encode strategy as one-hot
            1.0 if self.strategy == "sequential" else 0.0,
            1.0 if self.strategy == "batch_optimized" else 0.0,
            1.0 if self.strategy == "parallel_limited" else 0.0,
            1.0 if self.strategy == "skill_priority" else 0.0,
            1.0 if self.strategy == "adaptive_sampling" else 0.0,
            1.0 if self.strategy == "caching_aggressive" else 0.0,
            1.0 if self.strategy == "offload_external" else 0.0,
        ]


@dataclass
class PerformancePrediction:
    """Performance prediction result"""
    predicted_processing_time: float
    predicted_throughput: float
    predicted_resource_usage: Dict[str, float]
    recommended_strategy: str
    confidence_score: float
    alternative_strategies: List[Dict[str, Any]]
    optimization_suggestions: List[str]


class PerformancePredictor:
    """Machine learning-based performance prediction system"""

    def __init__(self, model_path: str = "performance_models"):
        self.model_path = model_path
        self.records: deque = deque(maxlen=10000)  # Keep last 10k records
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.feature_names = [
            "data_size", "cpu_usage", "memory_usage", "thread_count",
            "batch_size", "concurrency", "skill_count",
            "strategy_sequential", "strategy_batch", "strategy_parallel",
            "strategy_priority", "strategy_sampling", "strategy_caching", "strategy_offload"
        ]

        # Ensure model directory exists
        os.makedirs(model_path, exist_ok=True)

        # Load existing models if available
        self._load_models()

        # Training lock for thread safety
        self._training_lock = threading.Lock()

    def add_record(self, record: PerformanceRecord):
        """Add a new performance record"""
        self.records.append(record)

        # Periodically retrain models
        if len(self.records) % 100 == 0 and len(self.records) >= 50:
            self._retrain_models_async()

    def predict_performance(self,
                          data_size: int,
                          current_metrics: ResourceMetrics,
                          constraints: ResourceConstraints,
                          available_strategies: List[str] = None) -> PerformancePrediction:
        """Predict performance for different strategies"""
        if available_strategies is None:
            available_strategies = [s.value for s in OptimizationStrategy]

        # Create feature vector for current situation
        base_features = [
            data_size,
            current_metrics.cpu_percent,
            current_metrics.memory_percent,
            current_metrics.active_threads,
            # Will be updated for each strategy
            0,  # batch_size
            0,  # concurrency
            len([]),  # skill_count (placeholder)
            0, 0, 0, 0, 0, 0, 0  # strategy encodings
        ]

        predictions = []

        for strategy in available_strategies:
            # Create strategy-specific features
            strategy_features = base_features.copy()

            # Estimate optimal parameters for this strategy
            batch_size, concurrency = self._estimate_strategy_parameters(
                strategy, data_size, constraints, current_metrics
            )

            strategy_features[4] = batch_size  # batch_size
            strategy_features[5] = concurrency  # concurrency
            strategy_features[6] = 10  # estimated skill_count (average)

            # Set strategy encoding
            strategy_encodings = {
                "sequential": [1, 0, 0, 0, 0, 0, 0],
                "batch_optimized": [0, 1, 0, 0, 0, 0, 0],
                "parallel_limited": [0, 0, 1, 0, 0, 0, 0],
                "skill_priority": [0, 0, 0, 1, 0, 0, 0],
                "adaptive_sampling": [0, 0, 0, 0, 1, 0, 0],
                "caching_aggressive": [0, 0, 0, 0, 0, 1, 0],
                "offload_external": [0, 0, 0, 0, 0, 0, 1]
            }

            strategy_features[7:14] = strategy_encodings.get(strategy, [0, 0, 0, 0, 0, 0, 0])

            # Predict performance
            predicted_time, predicted_throughput = self._predict_with_models(strategy_features)

            predictions.append({
                "strategy": strategy,
                "predicted_time": predicted_time,
                "predicted_throughput": predicted_throughput,
                "batch_size": batch_size,
                "concurrency": concurrency,
                "confidence": self._calculate_confidence(strategy_features)
            })

        # Find best strategy
        if predictions:
            best_prediction = max(predictions, key=lambda x: x["predicted_throughput"] * x["confidence"])
            recommended_strategy = best_prediction["strategy"]
            confidence_score = best_prediction["confidence"]

            # Sort alternatives by throughput
            alternatives = sorted(
                [p for p in predictions if p["strategy"] != recommended_strategy],
                key=lambda x: x["predicted_throughput"] * x["confidence"],
                reverse=True
            )[:3]  # Top 3 alternatives
        else:
            # Fallback predictions
            best_prediction = self._fallback_prediction(data_size, current_metrics, constraints)
            recommended_strategy = "sequential"
            confidence_score = 0.3
            alternatives = []

        # Generate optimization suggestions
        suggestions = self._generate_optimization_suggestions(
            predictions, current_metrics, constraints
        )

        return PerformancePrediction(
            predicted_processing_time=best_prediction["predicted_time"],
            predicted_throughput=best_prediction["predicted_throughput"],
            predicted_resource_usage=self._predict_resource_usage(best_prediction, data_size),
            recommended_strategy=recommended_strategy,
            confidence_score=confidence_score,
            alternative_strategies=alternatives,
            optimization_suggestions=suggestions
        )

    def _estimate_strategy_parameters(self,
                                    strategy: str,
                                    data_size: int,
                                    constraints: ResourceConstraints,
                                    current_metrics: ResourceMetrics) -> Tuple[int, int]:
        """Estimate optimal batch size and concurrency for a strategy"""
        if strategy == "sequential":
            return 1, 1

        elif strategy == "batch_optimized":
            # Optimize batch size based on memory and data size
            memory_factor = max(0.1, 1.0 - current_metrics.memory_percent / 100.0)
            optimal_batch = min(constraints.max_batch_size,
                              max(10, int(data_size * 0.1 * memory_factor)))
            return optimal_batch, 1

        elif strategy == "parallel_limited":
            # Optimize concurrency based on CPU and threads
            cpu_factor = max(0.1, 1.0 - current_metrics.cpu_percent / 100.0)
            cpu_cores = 4  # Assume 4 cores
            optimal_concurrency = max(1, min(constraints.max_concurrent_tasks,
                                           int(cpu_cores * cpu_factor)))
            return min(100, data_size), optimal_concurrency

        elif strategy == "skill_priority":
            # Smaller batches for skill-specific processing
            return max(10, min(50, data_size // 4)), 1

        elif strategy == "adaptive_sampling":
            # Sample size based on resource constraints
            constraint_level = constraints.get_constraint_level(current_metrics)
            if constraint_level.value == "critical":
                sample_ratio = 0.1
            elif constraint_level.value == "high":
                sample_ratio = 0.25
            else:
                sample_ratio = 0.5

            return max(1, int(data_size * sample_ratio)), 1

        elif strategy == "caching_aggressive":
            # Process individually for better cache hits
            return 1, 1

        else:  # offload_external or fallback
            return min(100, data_size), 1

    def _predict_with_models(self, features: List[float]) -> Tuple[float, float]:
        """Predict processing time and throughput using trained models"""
        try:
            # Prepare features
            X = np.array(features).reshape(1, -1)

            # Use the best available model
            if "processing_time_model" in self.models and self.scalers.get("time_scaler"):
                scaler = self.scalers["time_scaler"]
                X_scaled = scaler.transform(X)

                model = self.models["processing_time_model"]
                predicted_time = max(0.1, model.predict(X_scaled)[0])
                predicted_throughput = max(0.1, features[0] / predicted_time)
            else:
                # Fallback to simple heuristics
                predicted_time, predicted_throughput = self._heuristic_prediction(features)

        except Exception as e:
            print(f"Prediction error: {e}")
            predicted_time, predicted_throughput = self._heuristic_prediction(features)

        return predicted_time, predicted_throughput

    def _heuristic_prediction(self, features: List[float]) -> Tuple[float, float]:
        """Fallback heuristic prediction when ML models aren't available"""
        data_size = features[0]
        cpu_usage = features[1]
        memory_usage = features[2]

        # Base processing time (empirically derived)
        base_time = data_size * 0.001  # 1ms per item base

        # Adjust for resource constraints
        cpu_factor = 1.0 + max(0, (cpu_usage - 50) / 50)  # Penalty for high CPU
        memory_factor = 1.0 + max(0, (memory_usage - 70) / 30)  # Penalty for high memory

        # Strategy-specific adjustments
        strategy_idx = np.argmax(features[7:14])
        strategy_multipliers = [1.0, 0.7, 0.4, 0.8, 0.3, 0.6, 0.5]  # Based on strategy efficiency

        predicted_time = base_time * cpu_factor * memory_factor * strategy_multipliers[strategy_idx]
        predicted_throughput = max(0.1, data_size / predicted_time)

        return predicted_time, predicted_throughput

    def _fallback_prediction(self,
                           data_size: int,
                           current_metrics: ResourceMetrics,
                           constraints: ResourceConstraints) -> Dict[str, Any]:
        """Fallback prediction when no models are available"""
        constraint_level = constraints.get_constraint_level(current_metrics)

        # Conservative estimates based on constraint level
        if constraint_level.value == "none":
            time_per_item = 0.001  # 1ms per item
        elif constraint_level.value == "low":
            time_per_item = 0.002  # 2ms per item
        elif constraint_level.value == "medium":
            time_per_item = 0.005  # 5ms per item
        elif constraint_level.value == "high":
            time_per_item = 0.010  # 10ms per item
        else:  # critical
            time_per_item = 0.020  # 20ms per item

        predicted_time = data_size * time_per_item
        predicted_throughput = max(0.1, data_size / predicted_time)

        return {
            "predicted_time": predicted_time,
            "predicted_throughput": predicted_throughput,
            "batch_size": max(1, min(100, data_size // 10)),
            "concurrency": 1,
            "confidence": 0.3
        }

    def _calculate_confidence(self, features: List[float]) -> float:
        """Calculate confidence score for prediction"""
        # Base confidence on amount of training data and feature similarity
        if len(self.records) < 50:
            return 0.3  # Low confidence with little data

        # Check feature similarity to historical data
        similarities = []
        for record in self.records[-100:]:  # Check last 100 records
            record_features = record.to_features()
            similarity = self._calculate_feature_similarity(features, record_features)
            similarities.append(similarity)

        if similarities:
            max_similarity = max(similarities)
            # Higher similarity = higher confidence
            confidence = min(0.9, 0.4 + max_similarity * 0.5)
        else:
            confidence = 0.5

        return confidence

    def _calculate_feature_similarity(self, features1: List[float], features2: List[float]) -> float:
        """Calculate similarity between two feature vectors"""
        if len(features1) != len(features2):
            return 0.0

        # Normalize features to 0-1 range
        max_vals = [max(f1, f2) for f1, f2 in zip(features1, features2)]
        normalized1 = [f1 / (f if f > 0 else 1) for f1, f in zip(features1, max_vals)]
        normalized2 = [f2 / (f if f > 0 else 1) for f2, f in zip(features2, max_vals)]

        # Calculate cosine similarity
        dot_product = sum(n1 * n2 for n1, n2 in zip(normalized1, normalized2))
        norm1 = sum(n1 ** 2 for n1 in normalized1) ** 0.5
        norm2 = sum(n2 ** 2 for n2 in normalized2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _predict_resource_usage(self,
                               prediction: Dict[str, Any],
                               data_size: int) -> Dict[str, float]:
        """Predict resource usage for a given strategy prediction"""
        strategy = prediction["strategy"]
        batch_size = prediction["batch_size"]
        concurrency = prediction["concurrency"]
        estimated_time = prediction["predicted_time"]

        # Base resource estimates
        cpu_estimate = 25.0  # Base CPU usage
        memory_estimate = 20.0  # Base memory usage

        # Strategy-specific adjustments
        if strategy == "parallel_limited":
            cpu_estimate = min(80.0, cpu_estimate * concurrency)
            memory_estimate = min(70.0, memory_estimate * concurrency * 0.5)
        elif strategy == "batch_optimized":
            cpu_estimate = min(60.0, cpu_estimate + batch_size * 0.01)
            memory_estimate = min(80.0, memory_estimate + batch_size * 0.02)
        elif strategy == "caching_aggressive":
            memory_estimate = min(85.0, memory_estimate + 30.0)
        elif strategy == "adaptive_sampling":
            # Using less data means less resources
            sample_ratio = 0.5  # Assume 50% sampling
            cpu_estimate *= sample_ratio
            memory_estimate *= sample_ratio

        # Adjust for data size
        if data_size > 1000:
            cpu_estimate = min(95.0, cpu_estimate * 1.5)
            memory_estimate = min(90.0, memory_estimate * 1.3)

        return {
            "cpu_percent": round(cpu_estimate, 1),
            "memory_percent": round(memory_estimate, 1),
            "estimated_threads": concurrency,
            "estimated_processing_time": estimated_time
        }

    def _generate_optimization_suggestions(self,
                                         predictions: List[Dict[str, Any]],
                                         current_metrics: ResourceMetrics,
                                         constraints: ResourceConstraints) -> List[str]:
        """Generate optimization suggestions based on predictions"""
        suggestions = []

        if not predictions:
            return ["Enable performance tracking to get optimization suggestions"]

        # Find best and worst strategies
        best_strategy = max(predictions, key=lambda x: x["predicted_throughput"] * x["confidence"])
        worst_strategy = min(predictions, key=lambda x: x["predicted_throughput"] * x["confidence"])

        # Compare best vs worst
        improvement_factor = best_strategy["predicted_throughput"] / max(0.1, worst_strategy["predicted_throughput"])
        if improvement_factor > 2.0:
            suggestions.append(
                f"Significant improvement potential: {best_strategy['strategy']} performs "
                f"{improvement_factor:.1f}x better than {worst_strategy['strategy']}"
            )

        # Resource-specific suggestions
        if current_metrics.cpu_percent > 80:
            suggestions.append("High CPU usage detected - consider sequential or batch_optimized strategies")

        if current_metrics.memory_percent > 80:
            suggestions.append("High memory usage detected - enable adaptive_sampling or reduce batch sizes")

        if current_metrics.active_threads > 50:
            suggestions.append("High thread count - consider reducing parallel_limited concurrency")

        # Constraint-specific suggestions
        constraint_level = constraints.get_constraint_level(current_metrics)
        if constraint_level.value in ["high", "critical"]:
            suggestions.append("System under constraints - prioritize skill_priority or adaptive_sampling strategies")

        # Confidence-based suggestions
        low_confidence_strategies = [p for p in predictions if p["confidence"] < 0.5]
        if low_confidence_strategies:
            suggestions.append(
                f"Low confidence predictions for {len(low_confidence_strategies)} strategies - "
                "collect more performance data"
            )

        return suggestions[:5]  # Return top 5 suggestions

    def _retrain_models_async(self):
        """Retrain ML models asynchronously"""
        def train():
            with self._training_lock:
                self._train_models()

        thread = threading.Thread(target=train, daemon=True)
        thread.start()

    def _train_models(self):
        """Train ML models with collected data"""
        if len(self.records) < 20:
            return  # Not enough data

        try:
            # Prepare training data
            X = []
            y_time = []
            y_throughput = []

            for record in self.records:
                features = record.to_features()
                X.append(features)
                y_time.append(record.processing_time)
                y_throughput.append(record.throughput)

            X = np.array(X)
            y_time = np.array(y_time)
            y_throughput = np.array(y_throughput)

            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Train processing time model
            time_model = RandomForestRegressor(
                n_estimators=50,
                max_depth=10,
                random_state=42
            )
            time_model.fit(X_scaled, y_time)

            # Store models and scalers
            self.models["processing_time_model"] = time_model
            self.scalers["time_scaler"] = scaler

            # Save models
            self._save_models()

            print(f"Models retrained with {len(X)} samples")

        except Exception as e:
            print(f"Model training failed: {e}")

    def _save_models(self):
        """Save trained models to disk"""
        try:
            # Save models
            for name, model in self.models.items():
                model_path = os.path.join(self.model_path, f"{name}.pkl")
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)

            # Save scalers
            for name, scaler in self.scalers.items():
                scaler_path = os.path.join(self.model_path, f"{name}.pkl")
                with open(scaler_path, 'wb') as f:
                    pickle.dump(scaler, f)

            # Save records
            records_path = os.path.join(self.model_path, "records.json")
            records_data = [record.to_dict() for record in self.records]
            with open(records_path, 'w') as f:
                json.dump(records_data, f, indent=2)

        except Exception as e:
            print(f"Error saving models: {e}")

    def _load_models(self):
        """Load trained models from disk"""
        try:
            # Load records
            records_path = os.path.join(self.model_path, "records.json")
            if os.path.exists(records_path):
                with open(records_path, 'r') as f:
                    records_data = json.load(f)
                    for record_dict in records_data:
                        record = PerformanceRecord(**record_dict)
                        self.records.append(record)

            # Load models
            model_files = [f for f in os.listdir(self.model_path) if f.endswith('_model.pkl')]
            for model_file in model_files:
                model_path = os.path.join(self.model_path, model_file)
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                    model_name = model_file.replace('.pkl', '')
                    self.models[model_name] = model

            # Load scalers
            scaler_files = [f for f in os.listdir(self.model_path) if f.endswith('_scaler.pkl')]
            for scaler_file in scaler_files:
                scaler_path = os.path.join(self.model_path, scaler_file)
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
                    scaler_name = scaler_file.replace('.pkl', '')
                    self.scalers[scaler_name] = scaler

            print(f"Loaded {len(self.models)} models and {len(self.records)} records")

        except Exception as e:
            print(f"Error loading models: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about trained models"""
        return {
            "total_records": len(self.records),
            "models_trained": list(self.models.keys()),
            "scalers_loaded": list(self.scalers.keys()),
            "model_path": self.model_path,
            "feature_count": len(self.feature_names),
            "last_training_time": max([r.timestamp for r in self.records]) if self.records else None
        }