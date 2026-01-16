"""
Results Storage Service
=======================

Stores research results so they can be retrieved later via task_id.

Storage options:
1. In-memory dict (simple, lost on restart)
2. Redis (persistent, production-ready)
3. PostgreSQL (full persistence with history)

This implementation uses Redis if available, falls back to in-memory.
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

# Try to import Redis, fall back to dict if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class TaskStatus(str, Enum):
    """Task execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ResultsStore:
    """
    Stores and retrieves research results.

    Uses Redis if available (persistent), otherwise in-memory dict.
    """

    def __init__(self):
        self.use_redis = False

        # Try Redis if available and configured
        if REDIS_AVAILABLE and os.getenv("REDIS_URL"):
            try:
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
                test_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                test_client.ping()
                self.client = test_client
                self.use_redis = True
                print("[ResultsStore] Using Redis for result storage")
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                print(f"[ResultsStore] Redis connection failed: {e}")
                print("[ResultsStore] Falling back to in-memory storage")
                self.client = {}  # In-memory fallback
        else:
            self.client = {}  # In-memory fallback
            print("[ResultsStore] Using in-memory storage (results lost on restart)")

    def store_result(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store a research result.

        Args:
            task_id: Unique task identifier
            status: Current task status
            result: Final report (markdown text)
            error: Error message if failed
            metadata: Additional info (ticker, criteria, etc.)
        """
        data = {
            "task_id": task_id,
            "status": status,
            "result": result,
            "error": error,
            "metadata": metadata or {},
            "updated_at": datetime.now().isoformat(),
            "created_at": metadata.get("created_at") if metadata else datetime.now().isoformat()
        }

        if self.use_redis:
            # Store in Redis with 7-day expiration
            key = f"research:task:{task_id}"
            self.client.setex(
                key,
                timedelta(days=7),
                json.dumps(data)
            )
        else:
            # Store in memory
            self.client[task_id] = data

        print(f"[ResultsStore] Stored result for task {task_id} (status: {status})")

    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a research result.

        Args:
            task_id: Task identifier

        Returns:
            Dict with status, result, error, metadata
            None if not found
        """
        if self.use_redis:
            key = f"research:task:{task_id}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
        else:
            return self.client.get(task_id)

        return None

    def update_status(self, task_id: str, status: TaskStatus):
        """Update just the status of a task"""
        existing = self.get_result(task_id)
        if existing:
            existing["status"] = status
            existing["updated_at"] = datetime.now().isoformat()

            if self.use_redis:
                key = f"research:task:{task_id}"
                self.client.setex(
                    key,
                    timedelta(days=7),
                    json.dumps(existing)
                )
            else:
                self.client[task_id] = existing

    def list_recent_tasks(self, limit: int = 10) -> list[Dict[str, Any]]:
        """
        List recent tasks (Redis only).

        Returns list of task data, most recent first.
        """
        if not self.use_redis:
            # In-memory: return all tasks
            return list(self.client.values())[:limit]

        # Redis: scan for all task keys
        tasks = []
        for key in self.client.scan_iter("research:task:*"):
            data = self.client.get(key)
            if data:
                tasks.append(json.loads(data))

        # Sort by created_at descending
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return tasks[:limit]

# Global singleton instance
_results_store = None

def get_results_store() -> ResultsStore:
    """Get or create the global results store instance"""
    global _results_store
    if _results_store is None:
        _results_store = ResultsStore()
    return _results_store
