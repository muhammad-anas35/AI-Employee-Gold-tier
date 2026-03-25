#!/usr/bin/env python3
"""
Rate Limiter for AI Employee
Prevents excessive API calls and actions
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import deque
from threading import Lock

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter with sliding window algorithm.

    Tracks actions and enforces limits per time window.
    """

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize rate limiter.

        Args:
            config_file: Path to rate limit configuration file
        """
        self.config_file = config_file or Path(__file__).parent / "rate_limits.json"
        self.limits = self._load_limits()
        self.history: Dict[str, deque] = {}
        self.lock = Lock()

    def _load_limits(self) -> Dict:
        """Load rate limit configuration"""
        default_limits = {
            "email_send": {
                "max_per_hour": 10,
                "max_per_day": 50,
                "window_seconds": 3600
            },
            "linkedin_post": {
                "max_per_hour": 3,
                "max_per_day": 10,
                "window_seconds": 3600
            },
            "payment": {
                "max_per_hour": 3,
                "max_per_day": 10,
                "window_seconds": 3600
            },
            "api_call": {
                "max_per_minute": 60,
                "max_per_hour": 1000,
                "window_seconds": 60
            },
            "whatsapp_send": {
                "max_per_hour": 20,
                "max_per_day": 100,
                "window_seconds": 3600
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    default_limits.update(loaded)
            except Exception as e:
                logger.warning(f"Could not load rate limits: {e}, using defaults")

        return default_limits

    def _save_limits(self):
        """Save rate limit configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.limits, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save rate limits: {e}")

    def _cleanup_old_entries(self, action_type: str, window_seconds: int):
        """Remove entries older than the window"""
        if action_type not in self.history:
            self.history[action_type] = deque()
            return

        cutoff_time = time.time() - window_seconds

        # Remove old entries from the left
        while self.history[action_type] and self.history[action_type][0] < cutoff_time:
            self.history[action_type].popleft()

    def check_limit(self, action_type: str, window: str = "hour") -> bool:
        """
        Check if action is within rate limit.

        Args:
            action_type: Type of action (e.g., "email_send")
            window: Time window to check ("minute", "hour", "day")

        Returns:
            True if within limit, False if limit exceeded
        """
        with self.lock:
            if action_type not in self.limits:
                logger.warning(f"No rate limit configured for {action_type}")
                return True

            config = self.limits[action_type]

            # Determine window and limit
            if window == "minute":
                window_seconds = 60
                max_actions = config.get("max_per_minute", float('inf'))
            elif window == "hour":
                window_seconds = 3600
                max_actions = config.get("max_per_hour", float('inf'))
            elif window == "day":
                window_seconds = 86400
                max_actions = config.get("max_per_day", float('inf'))
            else:
                window_seconds = config.get("window_seconds", 3600)
                max_actions = config.get("max_per_hour", float('inf'))

            # Cleanup old entries
            self._cleanup_old_entries(action_type, window_seconds)

            # Check current count
            current_count = len(self.history.get(action_type, []))

            if current_count >= max_actions:
                logger.warning(
                    f"Rate limit exceeded for {action_type}: "
                    f"{current_count}/{max_actions} in {window}"
                )
                return False

            return True

    def record_action(self, action_type: str):
        """
        Record an action for rate limiting.

        Args:
            action_type: Type of action performed
        """
        with self.lock:
            if action_type not in self.history:
                self.history[action_type] = deque()

            self.history[action_type].append(time.time())
            logger.debug(f"Recorded action: {action_type}")

    def can_perform(self, action_type: str, check_all_windows: bool = True) -> tuple[bool, Optional[str]]:
        """
        Check if action can be performed (checks all windows).

        Args:
            action_type: Type of action
            check_all_windows: Check all time windows (minute, hour, day)

        Returns:
            Tuple of (can_perform, reason_if_not)
        """
        if not check_all_windows:
            if self.check_limit(action_type):
                return True, None
            return False, f"Rate limit exceeded for {action_type}"

        # Check all windows
        windows = ["minute", "hour", "day"]

        for window in windows:
            if not self.check_limit(action_type, window):
                return False, f"Rate limit exceeded for {action_type} ({window})"

        return True, None

    def wait_if_needed(self, action_type: str, max_wait: float = 60.0) -> bool:
        """
        Wait if rate limit is exceeded (blocking).

        Args:
            action_type: Type of action
            max_wait: Maximum seconds to wait (default: 60)

        Returns:
            True if can proceed, False if max_wait exceeded
        """
        start_time = time.time()

        while True:
            can_perform, reason = self.can_perform(action_type)

            if can_perform:
                return True

            elapsed = time.time() - start_time
            if elapsed >= max_wait:
                logger.error(f"Max wait time exceeded for {action_type}")
                return False

            # Wait a bit and try again
            wait_time = min(5.0, max_wait - elapsed)
            logger.info(f"Rate limited, waiting {wait_time:.1f}s...")
            time.sleep(wait_time)

    def get_status(self, action_type: Optional[str] = None) -> Dict:
        """
        Get current rate limit status.

        Args:
            action_type: Specific action type, or None for all

        Returns:
            Dictionary with status information
        """
        with self.lock:
            if action_type:
                if action_type not in self.limits:
                    return {"error": f"Unknown action type: {action_type}"}

                config = self.limits[action_type]

                # Cleanup and count
                self._cleanup_old_entries(action_type, 3600)  # Hour window
                count_hour = len(self.history.get(action_type, []))

                self._cleanup_old_entries(action_type, 86400)  # Day window
                count_day = len(self.history.get(action_type, []))

                return {
                    "action_type": action_type,
                    "limits": config,
                    "current_hour": count_hour,
                    "current_day": count_day,
                    "can_perform": self.can_perform(action_type)[0]
                }
            else:
                # Return status for all action types
                status = {}
                for action in self.limits.keys():
                    status[action] = self.get_status(action)
                return status

    def reset(self, action_type: Optional[str] = None):
        """
        Reset rate limit history.

        Args:
            action_type: Specific action type, or None for all
        """
        with self.lock:
            if action_type:
                if action_type in self.history:
                    self.history[action_type].clear()
                    logger.info(f"Reset rate limit for {action_type}")
            else:
                self.history.clear()
                logger.info("Reset all rate limits")

    def update_limit(self, action_type: str, **kwargs):
        """
        Update rate limit configuration.

        Args:
            action_type: Type of action
            **kwargs: Limit parameters (max_per_hour, max_per_day, etc.)
        """
        with self.lock:
            if action_type not in self.limits:
                self.limits[action_type] = {}

            self.limits[action_type].update(kwargs)
            self._save_limits()
            logger.info(f"Updated rate limit for {action_type}: {kwargs}")


# Decorator for rate-limited functions
def rate_limited(action_type: str, limiter: Optional[RateLimiter] = None):
    """
    Decorator to enforce rate limiting on functions.

    Args:
        action_type: Type of action for rate limiting
        limiter: RateLimiter instance (creates new if None)

    Example:
        @rate_limited("email_send")
        def send_email(to, subject, body):
            # Send email
            pass
    """
    if limiter is None:
        limiter = RateLimiter()

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check rate limit
            can_perform, reason = limiter.can_perform(action_type)

            if not can_perform:
                logger.error(f"Rate limit exceeded: {reason}")
                raise Exception(f"Rate limit exceeded: {reason}")

            # Record action
            limiter.record_action(action_type)

            # Execute function
            return func(*args, **kwargs)

        return wrapper
    return decorator


# Example usage and tests
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n=== Rate Limiter Tests ===\n")

    # Create rate limiter
    limiter = RateLimiter()

    # Test 1: Check limits
    print("Test 1: Checking email send limits")
    for i in range(12):
        can_send, reason = limiter.can_perform("email_send")
        if can_send:
            limiter.record_action("email_send")
            print(f"  Email {i+1}: ✓ Sent")
        else:
            print(f"  Email {i+1}: ✗ {reason}")

    # Test 2: Status check
    print("\nTest 2: Status check")
    status = limiter.get_status("email_send")
    print(f"  Current hour: {status['current_hour']}/{status['limits']['max_per_hour']}")
    print(f"  Can perform: {status['can_perform']}")

    # Test 3: Reset
    print("\nTest 3: Reset and retry")
    limiter.reset("email_send")
    can_send, _ = limiter.can_perform("email_send")
    print(f"  After reset, can send: {can_send}")

    # Test 4: Decorator
    print("\nTest 4: Decorator test")

    @rate_limited("api_call", limiter)
    def make_api_call(endpoint):
        return f"Called {endpoint}"

    try:
        for i in range(3):
            result = make_api_call(f"/api/endpoint{i}")
            print(f"  {result}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== Tests complete ===\n")
