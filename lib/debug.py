from typing import Any, Callable
from functools import wraps
import time
import json

# Global debug settings
DEBUG_VERBOSE = False
DEBUG_LOG_HANDLER = None

def set_debug_verbosity(verbose: bool) -> None:
    """Set the global debug verbosity level."""
    global DEBUG_VERBOSE
    DEBUG_VERBOSE = verbose

def set_debug_log_handler(handler: Callable[[str], None]) -> None:
    """Set the debug log handler function."""
    global DEBUG_LOG_HANDLER
    DEBUG_LOG_HANDLER = handler

def debug(*, label: str = "") -> Callable:
    """A decorator that prints function arguments and return values for debugging.

    Args:
        label: A string message to print before the debug log

    Usage:
        @debug(label="Custom message")
        def my_function(x, y):
            return x + y
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = func.__name__

            # Convert args/kwargs to string lengths
            args_to_show = args[1:] if args and hasattr(args[0], '__class__') else args
            args_length = len(json.dumps(args_to_show))
            kwargs_length = len(json.dumps(kwargs)) if kwargs else 0

            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            result_length = len(json.dumps(result))

            if DEBUG_VERBOSE:
                messages = []
                if label:
                    messages.append(f"\n[DEBUG] {label}")
                messages.append(f"[DEBUG] Calling {func_name}")
                messages.append(f"  Args: {args_to_show}")
                messages.append(f"  Args length: {args_length}")
                if kwargs:
                    messages.append(f"  Kwargs: {kwargs}")
                    messages.append(f"  Kwargs length: {kwargs_length}")
                messages.append(f"[DEBUG] {func_name} returned: {result}")
                messages.append(f"[DEBUG] Response length: {result_length}")
                messages.append(f"[DEBUG] Execution time: {execution_time:.4f} seconds\n")
            else:
                messages = []
                if label:
                    messages.append(f"\n[DEBUG] {label}")
                messages.append(f"[DEBUG] {func_name} - args_len: {args_length}, kwargs_len: {kwargs_length}, response_len: {result_length}\n")

            if DEBUG_LOG_HANDLER:
                for message in messages:
                    DEBUG_LOG_HANDLER(message)
            else:
                for message in messages:
                    print(message)

            return result

        return wrapper

    return decorator
