#!/usr/bin/env python3
"""
Retry Handler with Exponential Backoff
Provides retry logic for transient failures
"""

import time
import logging
from functools import wraps
from typing import Callable, Type, Tuple, Optional

logger = logging.getLogger(__name__)


class TransientError(Exception):
    """Exception for transient errors that should be retried"""
    pass


class PermanentError(Exception):
    """Exception for permanent errors that should not be retried"""
    pass


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        exceptions: Tuple of exceptions to catch and retry (default: all)
        on_retry: Optional callback function called on each retry

    Example:
        @with_retry(max_attempts=3, base_delay=1, max_delay=60)
        def fetch_data():
            # Code that might fail transiently
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)

                except PermanentError:
                    # Don't retry permanent errors
                    logger.error(f"{func.__name__}: Permanent error, not retrying")
                    raise

                except exceptions as e:
                    attempt += 1

                    if attempt >= max_attempts:
                        logger.error(
                            f"{func.__name__}: Failed after {max_attempts} attempts"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** (attempt - 1)),
                        max_delay
                    )

                    logger.warning(
                        f"{func.__name__}: Attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt, delay, e)
                        except Exception as callback_error:
                            logger.error(f"Retry callback failed: {callback_error}")

                    # Wait before retry
                    time.sleep(delay)

            # Should never reach here, but just in case
            raise Exception(f"{func.__name__}: Max retries exceeded")

        return wrapper
    return decorator


def retry_with_backoff(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    *args,
    **kwargs
):
    """
    Retry a function with exponential backoff (non-decorator version).

    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function

    Returns:
        Result of successful function call

    Example:
        result = retry_with_backoff(api_call, max_attempts=5, arg1="value")
    """
    attempt = 0

    while attempt < max_attempts:
        try:
            return func(*args, **kwargs)

        except PermanentError:
            logger.error(f"{func.__name__}: Permanent error, not retrying")
            raise

        except Exception as e:
            attempt += 1

            if attempt >= max_attempts:
                logger.error(f"{func.__name__}: Failed after {max_attempts} attempts")
                raise

            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)

            logger.warning(
                f"{func.__name__}: Attempt {attempt}/{max_attempts} failed: {e}. "
                f"Retrying in {delay:.1f}s..."
            )

            time.sleep(delay)

    raise Exception(f"{func.__name__}: Max retries exceeded")


class RetryContext:
    """
    Context manager for retry logic.

    Example:
        with RetryContext(max_attempts=3) as retry:
            while retry.should_retry():
                try:
                    # Code that might fail
                    result = api_call()
                    retry.success()
                    break
                except Exception as e:
                    retry.failed(e)
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.attempt = 0
        self.last_error = None
        self._success = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and not self._success:
            logger.error(f"RetryContext: Failed after {self.attempt} attempts")
        return False

    def should_retry(self) -> bool:
        """Check if should continue retrying"""
        return self.attempt < self.max_attempts and not self._success

    def failed(self, error: Exception):
        """Mark attempt as failed"""
        self.attempt += 1
        self.last_error = error

        if self.attempt < self.max_attempts:
            delay = min(
                self.base_delay * (2 ** (self.attempt - 1)),
                self.max_delay
            )
            logger.warning(
                f"Attempt {self.attempt}/{self.max_attempts} failed: {error}. "
                f"Retrying in {delay:.1f}s..."
            )
            time.sleep(delay)
        else:
            logger.error(f"Failed after {self.max_attempts} attempts: {error}")

    def success(self):
        """Mark operation as successful"""
        self._success = True


# Example usage and tests
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test 1: Decorator with eventual success
    print("\n=== Test 1: Decorator with eventual success ===")

    attempt_count = 0

    @with_retry(max_attempts=3, base_delay=0.5, max_delay=2)
    def flaky_function():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise TransientError(f"Attempt {attempt_count} failed")
        return "Success!"

    try:
        result = flaky_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed: {e}")

    # Test 2: Permanent error (should not retry)
    print("\n=== Test 2: Permanent error ===")

    @with_retry(max_attempts=3, base_delay=0.5)
    def permanent_failure():
        raise PermanentError("This should not be retried")

    try:
        permanent_failure()
    except PermanentError as e:
        print(f"Caught permanent error (as expected): {e}")

    # Test 3: Context manager
    print("\n=== Test 3: Context manager ===")

    with RetryContext(max_attempts=3, base_delay=0.5) as retry:
        attempt = 0
        while retry.should_retry():
            try:
                attempt += 1
                if attempt < 2:
                    raise Exception(f"Attempt {attempt} failed")
                print("Success with context manager!")
                retry.success()
                break
            except Exception as e:
                retry.failed(e)

    print("\n=== All tests complete ===")
