from typing import Any, Callable
from functools import wraps
import time
import json

def debug(*, label: str = "", verbose: bool = False) -> Callable:
    """A decorator that prints function arguments and return values for debugging.
    
    Args:
        label: A string message to print before the debug log
        verbose: If True, logs all details. If False, logs only function name and lengths.
    
    Usage:
        @debug(label="Custom message", verbose=True)
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

            if verbose:
                if label:
                    print(f"\n[DEBUG] {label}")
                print(f"[DEBUG] Calling {func_name}")
                print(f"  Args: {args_to_show}")
                print(f"  Args length: {args_length}")
                if kwargs:
                    print(f"  Kwargs: {kwargs}")
                    print(f"  Kwargs length: {kwargs_length}")
                print(f"[DEBUG] {func_name} returned: {result}")
                print(f"[DEBUG] Response length: {result_length}")
                print(f"[DEBUG] Execution time: {execution_time:.4f} seconds\n")
            else:
                if label:
                    print(f"\n[DEBUG] {label}")
                print(f"[DEBUG] {func_name} - args_len: {args_length}, kwargs_len: {kwargs_length}, response_len: {result_length}\n")

            return result

        return wrapper

    return decorator
