"""
Execution Limits - Safety limits for agent execution

Provides:
- Timeout handling
- Max turns per request
- Memory limits
- Rate limiting
"""

from typing import Optional
from datetime import datetime, timedelta, timezone
from functools import wraps
import asyncio


class ExecutionLimits:
    """
    Configuration for execution limits.
    """
    
    # Timeout limits
    DEFAULT_TIMEOUT_SECONDS = 60  # 1 minute default
    MAX_TIMEOUT_SECONDS = 300  # 5 minutes max
    
    # Turn limits
    MAX_TURNS_PER_REQUEST = 10
    
    # Memory limits
    MAX_MEMORY_MB = 100  # Max memory per session
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_REQUESTS_PER_HOUR = 1000


class ExecutionTimer:
    """
    Timer for tracking execution time and enforcing timeouts.
    """
    
    def __init__(self, timeout_seconds: Optional[int] = None):
        """
        Initialize execution timer.
        
        Args:
            timeout_seconds: Timeout in seconds (default: 60)
        """
        self.timeout_seconds = timeout_seconds or ExecutionLimits.DEFAULT_TIMEOUT_SECONDS
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def start(self):
        """Start the timer"""
        self.start_time = datetime.now(timezone.utc)
    
    def stop(self):
        """Stop the timer"""
        self.end_time = datetime.now(timezone.utc)
    
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds"""
        if not self.start_time:
            return 0.0
        
        end = self.end_time or datetime.now(timezone.utc)
        delta = end - self.start_time
        return delta.total_seconds()
    
    def is_timeout(self) -> bool:
        """Check if execution has timed out"""
        return self.elapsed_seconds() > self.timeout_seconds
    
    def remaining_seconds(self) -> float:
        """Get remaining time before timeout"""
        return max(0, self.timeout_seconds - self.elapsed_seconds())


def with_timeout(timeout_seconds: Optional[int] = None):
    """
    Decorator to add timeout to async functions.
    
    Args:
        timeout_seconds: Timeout in seconds
        
    Usage:
        @with_timeout(30)
        async def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            timeout = timeout_seconds or ExecutionLimits.DEFAULT_TIMEOUT_SECONDS
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                raise TimeoutError(
                    f"Execution timed out after {timeout} seconds"
                )
        return wrapper
    return decorator


class TurnCounter:
    """
    Counter for tracking turns in a conversation.
    """
    
    def __init__(self, max_turns: Optional[int] = None):
        """
        Initialize turn counter.
        
        Args:
            max_turns: Maximum turns allowed
        """
        self.max_turns = max_turns or ExecutionLimits.MAX_TURNS_PER_REQUEST
        self.current_turn = 0
    
    def increment(self):
        """Increment turn counter"""
        self.current_turn += 1
    
    def is_limit_reached(self) -> bool:
        """Check if turn limit is reached"""
        return self.current_turn >= self.max_turns
    
    def remaining_turns(self) -> int:
        """Get remaining turns"""
        return max(0, self.max_turns - self.current_turn)


class MemoryTracker:
    """
    Tracker for monitoring memory usage.
    """
    
    def __init__(self, max_memory_mb: Optional[int] = None):
        """
        Initialize memory tracker.
        
        Args:
            max_memory_mb: Maximum memory in MB
        """
        self.max_memory_mb = max_memory_mb or ExecutionLimits.MAX_MEMORY_MB
        self.current_memory_mb = 0
    
    def add_memory(self, size_mb: float):
        """Add memory usage"""
        self.current_memory_mb += size_mb
    
    def is_limit_reached(self) -> bool:
        """Check if memory limit is reached"""
        return self.current_memory_mb >= self.max_memory_mb
    
    def remaining_memory_mb(self) -> float:
        """Get remaining memory"""
        return max(0, self.max_memory_mb - self.current_memory_mb)
    
    def reset(self):
        """Reset memory counter"""
        self.current_memory_mb = 0


class RateLimiter:
    """
    Simple rate limiter for API requests.
    """
    
    def __init__(self):
        """Initialize rate limiter"""
        self.requests_per_minute: Dict[str, list] = {}
        self.requests_per_hour: Dict[str, list] = {}
    
    def check_rate_limit(self, user_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if user has exceeded rate limits.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        now = datetime.now(timezone.utc)
        
        # Clean old requests
        self._clean_old_requests(user_id, now)
        
        # Check per-minute limit
        minute_requests = self.requests_per_minute.get(user_id, [])
        if len(minute_requests) >= ExecutionLimits.MAX_REQUESTS_PER_MINUTE:
            return False, "Rate limit exceeded: too many requests per minute"
        
        # Check per-hour limit
        hour_requests = self.requests_per_hour.get(user_id, [])
        if len(hour_requests) >= ExecutionLimits.MAX_REQUESTS_PER_HOUR:
            return False, "Rate limit exceeded: too many requests per hour"
        
        # Record request
        self._record_request(user_id, now)
        
        return True, None
    
    def _clean_old_requests(self, user_id: str, now: datetime):
        """Remove requests older than time windows"""
        # Clean minute window
        if user_id in self.requests_per_minute:
            self.requests_per_minute[user_id] = [
                req_time for req_time in self.requests_per_minute[user_id]
                if now - req_time < timedelta(minutes=1)
            ]
        
        # Clean hour window
        if user_id in self.requests_per_hour:
            self.requests_per_hour[user_id] = [
                req_time for req_time in self.requests_per_hour[user_id]
                if now - req_time < timedelta(hours=1)
            ]
    
    def _record_request(self, user_id: str, now: datetime):
        """Record a new request"""
        if user_id not in self.requests_per_minute:
            self.requests_per_minute[user_id] = []
        if user_id not in self.requests_per_hour:
            self.requests_per_hour[user_id] = []
        
        self.requests_per_minute[user_id].append(now)
        self.requests_per_hour[user_id].append(now)


# Global rate limiter instance
rate_limiter = RateLimiter()
