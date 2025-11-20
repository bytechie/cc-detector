"""
Data Persistence and State Management

This module provides comprehensive data persistence and state management capabilities:
- Multiple database backends (SQLAlchemy, MongoDB, Redis)
- State management for adaptive skills
- Audit logging and history tracking
- Configuration persistence
- Session management
- Data migration and versioning
"""

import json
import time
import pickle
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Type, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging
from pathlib import Path
import hashlib
import secrets

logger = logging.getLogger(__name__)

# Database imports (with graceful fallbacks)
try:
    from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.pool import StaticPool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    import redis
    from redis import Redis as RedisClient
    from redis.exceptions import ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class StorageBackend(Enum):
    """Available storage backends"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    MEMORY = "memory"
    FILE = "file"


class StateType(Enum):
    """Types of state to persist"""
    SKILL_PERFORMANCE = "skill_performance"
    USER_PREFERENCES = "user_preferences"
    SYSTEM_CONFIG = "system_config"
    AUDIT_LOGS = "audit_logs"
    PROCESSING_HISTORY = "processing_history"
    RESOURCE_METRICS = "resource_metrics"
    PLUGIN_REGISTRY = "plugin_registry"
    MODEL_CACHE = "model_cache"


@dataclass
class StateRecord:
    """Generic state record"""
    id: str
    state_type: StateType
    key: str
    value: Any
    metadata: Dict[str, Any]
    created_at: float
    updated_at: float
    expires_at: Optional[float] = None
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        result = asdict(self)
        result['state_type'] = self.state_type.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateRecord':
        """Create from dictionary"""
        if isinstance(data.get('state_type'), str):
            data['state_type'] = StateType(data['state_type'])
        return cls(**data)


class PersistenceBackend(ABC):
    """Abstract base class for persistence backends"""

    @abstractmethod
    def save_state(self, record: StateRecord) -> bool:
        """Save a state record"""
        pass

    @abstractmethod
    def load_state(self, state_type: StateType, key: str) -> Optional[StateRecord]:
        """Load a state record"""
        pass

    @abstractmethod
    def delete_state(self, state_type: StateType, key: str) -> bool:
        """Delete a state record"""
        pass

    @abstractmethod
    def list_states(self, state_type: StateType, prefix: str = "") -> List[StateRecord]:
        """List all states of a type (optionally filtered by prefix)"""
        pass

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Clean up expired records"""
        pass

    @abstractmethod
    def close(self):
        """Close connections and cleanup"""
        pass


class MemoryPersistence(PersistenceBackend):
    """In-memory persistence backend"""

    def __init__(self):
        self._storage: Dict[str, StateRecord] = {}
        self._lock = threading.RLock()

    def _make_key(self, state_type: StateType, key: str) -> str:
        return f"{state_type.value}:{key}"

    def save_state(self, record: StateRecord) -> bool:
        with self._lock:
            try:
                key = self._make_key(record.state_type, record.key)
                record.updated_at = time.time()
                self._storage[key] = record
                return True
            except Exception as e:
                logger.error(f"Failed to save state: {e}")
                return False

    def load_state(self, state_type: StateType, key: str) -> Optional[StateRecord]:
        with self._lock:
            try:
                key = self._make_key(state_type, key)
                record = self._storage.get(key)

                if record and record.expires_at and record.expires_at < time.time():
                    del self._storage[key]
                    return None

                return record
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                return None

    def delete_state(self, state_type: StateType, key: str) -> bool:
        with self._lock:
            try:
                key = self._make_key(state_type, key)
                if key in self._storage:
                    del self._storage[key]
                return True
            except Exception as e:
                logger.error(f"Failed to delete state: {e}")
                return False

    def list_states(self, state_type: StateType, prefix: str = "") -> List[StateRecord]:
        with self._lock:
            try:
                key_prefix = f"{state_type.value}:{prefix}"
                records = []

                for key, record in self._storage.items():
                    if key.startswith(key_prefix):
                        if record.expires_at is None or record.expires_at > time.time():
                            records.append(record)

                return records
            except Exception as e:
                logger.error(f"Failed to list states: {e}")
                return []

    def cleanup_expired(self) -> int:
        with self._lock:
            try:
                expired_keys = []
                now = time.time()

                for key, record in self._storage.items():
                    if record.expires_at and record.expires_at < now:
                        expired_keys.append(key)

                for key in expired_keys:
                    del self._storage[key]

                return len(expired_keys)
            except Exception as e:
                logger.error(f"Failed to cleanup expired states: {e}")
                return 0

    def close(self):
        with self._lock:
            self._storage.clear()


class FilePersistence(PersistenceBackend):
    """File-based persistence backend"""

    def __init__(self, base_path: Union[str, Path], file_format: str = "json"):
        self.base_path = Path(base_path)
        self.file_format = file_format.lower()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _get_file_path(self, state_type: StateType, key: str) -> Path:
        """Get file path for a state record"""
        # Create a safe filename
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.base_path / state_type.value / f"{safe_key}.{self.file_format}"

    def save_state(self, record: StateRecord) -> bool:
        with self._lock:
            try:
                record.updated_at = time.time()
                file_path = self._get_file_path(record.state_type, record.key)
                file_path.parent.mkdir(parents=True, exist_ok=True)

                if self.file_format == "json":
                    with open(file_path, 'w') as f:
                        json.dump(record.to_dict(), f, indent=2, default=str)
                elif self.file_format == "pickle":
                    with open(file_path, 'wb') as f:
                        pickle.dump(record, f)
                else:
                    logger.error(f"Unsupported file format: {self.file_format}")
                    return False

                return True
            except Exception as e:
                logger.error(f"Failed to save state to file: {e}")
                return False

    def load_state(self, state_type: StateType, key: str) -> Optional[StateRecord]:
        with self._lock:
            try:
                file_path = self._get_file_path(state_type, key)

                if not file_path.exists():
                    return None

                if self.file_format == "json":
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        record = StateRecord.from_dict(data)
                elif self.file_format == "pickle":
                    with open(file_path, 'rb') as f:
                        record = pickle.load(f)
                else:
                    logger.error(f"Unsupported file format: {self.file_format}")
                    return None

                # Check expiration
                if record.expires_at and record.expires_at < time.time():
                    file_path.unlink(missing_ok=True)
                    return None

                return record
            except Exception as e:
                logger.error(f"Failed to load state from file: {e}")
                return None

    def delete_state(self, state_type: StateType, key: str) -> bool:
        with self._lock:
            try:
                file_path = self._get_file_path(state_type, key)
                file_path.unlink(missing_ok=True)
                return True
            except Exception as e:
                logger.error(f"Failed to delete state file: {e}")
                return False

    def list_states(self, state_type: StateType, prefix: str = "") -> List[StateRecord]:
        with self._lock:
            try:
                records = []
                state_dir = self.base_path / state_type.value

                if not state_dir.exists():
                    return []

                for file_path in state_dir.glob(f"*.{self.file_format}"):
                    try:
                        if self.file_format == "json":
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                record = StateRecord.from_dict(data)
                        elif self.file_format == "pickle":
                            with open(file_path, 'rb') as f:
                                record = pickle.load(f)
                        else:
                            continue

                        # Check expiration
                        if record.expires_at and record.expires_at < time.time():
                            file_path.unlink(missing_ok=True)
                            continue

                        # Check prefix match if specified
                        if prefix and not record.key.startswith(prefix):
                            continue

                        records.append(record)
                    except Exception as e:
                        logger.warning(f"Failed to load state from {file_path}: {e}")
                        continue

                return records
            except Exception as e:
                logger.error(f"Failed to list states: {e}")
                return []

    def cleanup_expired(self) -> int:
        with self._lock:
            try:
                cleaned_count = 0
                now = time.time()

                for state_dir in self.base_path.iterdir():
                    if not state_dir.is_dir():
                        continue

                    for file_path in state_dir.glob(f"*.{self.file_format}"):
                        try:
                            if self.file_format == "json":
                                with open(file_path, 'r') as f:
                                    data = json.load(f)
                                    expires_at = data.get('expires_at')
                            elif self.file_format == "pickle":
                                with open(file_path, 'rb') as f:
                                    record = pickle.load(f)
                                    expires_at = record.expires_at
                            else:
                                continue

                            if expires_at and expires_at < now:
                                file_path.unlink(missing_ok=True)
                                cleaned_count += 1
                        except Exception:
                            continue

                return cleaned_count
            except Exception as e:
                logger.error(f"Failed to cleanup expired states: {e}")
                return 0

    def close(self):
        with self._lock:
            pass  # No cleanup needed for file backend


class RedisPersistence(PersistenceBackend):
    """Redis-based persistence backend"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0,
                 password: str = None, prefix: str = "ccd"):
        if not REDIS_AVAILABLE:
            raise ImportError("redis package is required for RedisPersistence")

        self.client = RedisClient(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
        self.prefix = prefix
        self._test_connection()

    def _test_connection(self):
        """Test Redis connection"""
        try:
            self.client.ping()
        except RedisConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def _make_key(self, state_type: StateType, key: str) -> str:
        return f"{self.prefix}:{state_type.value}:{key}"

    def save_state(self, record: StateRecord) -> bool:
        try:
            key = self._make_key(record.state_type, record.key)
            record.updated_at = time.time()

            data = json.dumps(record.to_dict(), default=str)

            pipe = self.client.pipeline()
            pipe.set(key, data)

            if record.expires_at:
                ttl = int(record.expires_at - time.time())
                if ttl > 0:
                    pipe.expire(key, ttl)

            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Failed to save state to Redis: {e}")
            return False

    def load_state(self, state_type: StateType, key: str) -> Optional[StateRecord]:
        try:
            key = self._make_key(state_type, key)
            data = self.client.get(key)

            if not data:
                return None

            record_dict = json.loads(data)
            record = StateRecord.from_dict(record_dict)

            # Check expiration
            if record.expires_at and record.expires_at < time.time():
                self.client.delete(key)
                return None

            return record
        except Exception as e:
            logger.error(f"Failed to load state from Redis: {e}")
            return None

    def delete_state(self, state_type: StateType, key: str) -> bool:
        try:
            key = self._make_key(state_type, key)
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete state from Redis: {e}")
            return False

    def list_states(self, state_type: StateType, prefix: str = "") -> List[StateRecord]:
        try:
            key_pattern = f"{self.prefix}:{state_type.value}:{prefix}*"
            keys = self.client.keys(key_pattern)

            records = []
            now = time.time()

            for key in keys:
                try:
                    data = self.client.get(key)
                    if data:
                        record_dict = json.loads(data)
                        record = StateRecord.from_dict(record_dict)

                        # Check expiration
                        if record.expires_at and record.expires_at < now:
                            self.client.delete(key)
                            continue

                        records.append(record)
                except Exception as e:
                    logger.warning(f"Failed to load state from Redis key {key}: {e}")
                    continue

            return records
        except Exception as e:
            logger.error(f"Failed to list states from Redis: {e}")
            return []

    def cleanup_expired(self) -> int:
        # Redis handles expiration automatically
        return 0

    def close(self):
        self.client.close()


class StateManager:
    """Main state management system"""

    def __init__(self, backend: PersistenceBackend = None, auto_cleanup: bool = True,
                 cleanup_interval: int = 3600):
        self.backend = backend or MemoryPersistence()
        self.auto_cleanup = auto_cleanup
        self.cleanup_interval = cleanup_interval
        self._cleanup_thread = None
        self._running = False

        # Cache for frequently accessed states
        self._cache: Dict[str, StateRecord] = {}
        self._cache_ttl = 300  # 5 minutes
        self._cache_timestamps: Dict[str, float] = {}

        if self.auto_cleanup:
            self.start_auto_cleanup()

    def set_state(self, state_type: StateType, key: str, value: Any,
                  expires_at: Optional[float] = None, metadata: Dict[str, Any] = None):
        """Set a state value"""
        record = StateRecord(
            id=str(uuid.uuid4()),
            state_type=state_type,
            key=key,
            value=value,
            metadata=metadata or {},
            created_at=time.time(),
            updated_at=time.time(),
            expires_at=expires_at,
            version=1
        )

        self.backend.save_state(record)

        # Update cache
        cache_key = f"{state_type.value}:{key}"
        self._cache[cache_key] = record
        self._cache_timestamps[cache_key] = time.time()

    def get_state(self, state_type: StateType, key: str, default: Any = None,
                  use_cache: bool = True) -> Any:
        """Get a state value"""
        cache_key = f"{state_type.value}:{key}"

        # Check cache first
        if use_cache and cache_key in self._cache:
            cached_record = self._cache[cache_key]
            if self._is_cache_valid(cache_key):
                return cached_record.value
            else:
                del self._cache[cache_key]
                del self._cache_timestamps[cache_key]

        # Load from backend
        record = self.backend.load_state(state_type, key)
        if record:
            # Update cache
            self._cache[cache_key] = record
            self._cache_timestamps[cache_key] = time.time()
            return record.value

        return default

    def update_state(self, state_type: StateType, key: str,
                     update_func: Callable[[Any], Any], default: Any = None) -> Any:
        """Update a state value using a function"""
        current_value = self.get_state(state_type, key, default)
        new_value = update_func(current_value)
        self.set_state(state_type, key, new_value)
        return new_value

    def delete_state(self, state_type: StateType, key: str):
        """Delete a state value"""
        self.backend.delete_state(state_type, key)

        # Remove from cache
        cache_key = f"{state_type.value}:{key}"
        if cache_key in self._cache:
            del self._cache[cache_key]
        if cache_key in self._cache_timestamps:
            del self._cache_timestamps[cache_key]

    def list_states(self, state_type: StateType, prefix: str = "") -> List[Dict[str, Any]]:
        """List all states of a type"""
        records = self.backend.list_states(state_type, prefix)
        return [record.to_dict() for record in records]

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached record is still valid"""
        if cache_key not in self._cache_timestamps:
            return False

        return (time.time() - self._cache_timestamps[cache_key]) < self._cache_ttl

    def start_auto_cleanup(self):
        """Start automatic cleanup thread"""
        if self._running:
            return

        self._running = True
        self._cleanup_thread = threading.Thread(target=self._auto_cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def stop_auto_cleanup(self):
        """Stop automatic cleanup thread"""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=10)

    def _auto_cleanup_loop(self):
        """Automatic cleanup loop"""
        while self._running:
            try:
                time.sleep(self.cleanup_interval)
                cleaned = self.backend.cleanup_expired()

                if cleaned > 0:
                    logger.info(f"Cleaned up {cleaned} expired state records")

            except Exception as e:
                logger.error(f"Auto cleanup error: {e}")

    def cleanup_expired(self):
        """Manually cleanup expired records"""
        cleaned = self.backend.cleanup_expired()

        # Clean up cache
        current_time = time.time()
        expired_cache_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if (current_time - timestamp) > self._cache_ttl
        ]

        for key in expired_cache_keys:
            if key in self._cache:
                del self._cache[key]
            del self._cache_timestamps[key]

        return cleaned + len(expired_cache_keys)

    def clear_cache(self):
        """Clear the state cache"""
        self._cache.clear()
        self._cache_timestamps.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self._cache),
            "ttl_seconds": self._cache_ttl,
            "auto_cleanup": self.auto_cleanup,
            "cleanup_interval": self.cleanup_interval
        }

    def close(self):
        """Close the state manager"""
        self.stop_auto_cleanup()
        self.clear_cache()
        self.backend.close()


class AuditLogger:
    """Audit logging for tracking system changes and user actions"""

    def __init__(self, backend: PersistenceBackend = None):
        self.backend = backend or MemoryPersistence()
        self.current_user = None

    def set_user(self, user_id: str, user_info: Dict[str, Any] = None):
        """Set the current user context"""
        self.current_user = user_id

    def log_action(self, action: str, resource: str, details: Dict[str, Any] = None,
                   severity: str = "info"):
        """Log an action"""
        log_entry = {
            "timestamp": time.time(),
            "user_id": self.current_user,
            "action": action,
            "resource": resource,
            "details": details or {},
            "severity": severity,
            "ip_address": self._get_client_ip(),
            "user_agent": self._get_user_agent()
        }

        record = StateRecord(
            id=str(uuid.uuid4()),
            state_type=StateType.AUDIT_LOGS,
            key=str(uuid.uuid4()),  # Use UUID as key for uniqueness
            value=log_entry,
            metadata={"severity": severity},
            created_at=time.time(),
            updated_at=time.time()
        )

        self.backend.save_state(record)

    def _get_client_ip(self) -> str:
        """Get client IP address"""
        try:
            # This would typically come from request context
            import flask
            if hasattr(flask, 'request'):
                return flask.request.remote_addr
        except ImportError:
            pass
        return "unknown"

    def _get_user_agent(self) -> str:
        """Get user agent string"""
        try:
            import flask
            if hasattr(flask, 'request'):
                return flask.request.headers.get('User-Agent', 'unknown')
        except ImportError:
            pass
        return "unknown"

    def get_audit_logs(self, limit: int = 100, user_id: str = None) -> List[Dict[str, Any]]:
        """Get recent audit logs"""
        prefix = f"user:{user_id}:" if user_id else ""
        records = self.backend.list_states(StateType.AUDIT_LOGS, prefix)

        # Sort by timestamp and limit
        records.sort(key=lambda r: r.created_at, reverse=True)
        records = records[:limit]

        return [record.to_dict() for record in records]


# Global instances
state_manager = StateManager()
audit_logger = AuditLogger()