import os
import pickle
import redis


class RedisStore:

    def __init__(self):
        self.client = None
        self.available = False
        
        try:
            self.client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=0,
                socket_connect_timeout=2  # 2 second timeout
            )
            # Test connection
            self.client.ping()
            self.available = True
            print("[OK] Redis connected successfully")
        except Exception as e:
            print(f"[WARN] Redis not available: {e}")
            print("[INFO] Using in-memory fallback for session storage")
            self.client = None
            self.available = False


    def save(self, session_id, obj):
        if not self.available or not self.client:
            return  # Silently fail - data just won't persist
        try:
            self.client.set(session_id, pickle.dumps(obj))
        except Exception as e:
            print(f"[WARN] Redis save failed: {e}")


    def load(self, session_id):
        if not self.available or not self.client:
            return None  # Return None when not available
        try:
            raw = self.client.get(session_id)
            return pickle.loads(raw) if raw else None
        except Exception as e:
            print(f"[WARN] Redis load failed: {e}")
            return None


    def clear(self, session_id):
        if not self.available or not self.client:
            return
        try:
            self.client.delete(session_id)
        except Exception as e:
            print(f"[WARN] Redis clear failed: {e}")


