import json
import redis
from typing import Dict, Any, Optional

class RedisService:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)

    def save_session(self, session_id: str, session_data: Dict[str, Any], ttl: int = 86400) -> None:
        """Save session data to Redis with TTL"""
        try:
            self.redis_client.setex(
                f"session:{session_id}", 
                ttl, 
                json.dumps(session_data)
            )
        except Exception as e:
            print(f"Error saving session to Redis: {e}")

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Redis"""
        try:
            data = self.redis_client.get(f"session:{session_id}")
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Error getting session from Redis: {e}")
            return None

    def delete_session(self, session_id: str) -> None:
        """Delete session from Redis"""
        try:
            self.redis_client.delete(f"session:{session_id}")
        except Exception as e:
            print(f"Error deleting session from Redis: {e}")

    def save_job_status(self, job_id: str, status_data: Dict[str, Any], ttl: int = 3600) -> None:
        """Save job status to Redis"""
        try:
            self.redis_client.setex(
                f"job:{job_id}", 
                ttl, 
                json.dumps(status_data)
            )
        except Exception as e:
            print(f"Error saving job status to Redis: {e}")

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status from Redis"""
        try:
            data = self.redis_client.get(f"job:{job_id}")
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Error getting job status from Redis: {e}")
            return None

    def delete_job_status(self, job_id: str) -> None:
        """Delete job status from Redis"""
        try:
            self.redis_client.delete(f"job:{job_id}")
        except Exception as e:
            print(f"Error deleting job status from Redis: {e}")

    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            print(f"Redis ping failed: {e}")
            return False 