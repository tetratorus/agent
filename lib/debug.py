from typing import Any, Callable
from functools import wraps

def debug(prefix: str = "") -> Callable:
    """A decorator that prints function arguments and return values for debugging.

    Args:
        prefix: A string message to print before the debug log

    Usage:
        @debug("Custom message")
        def my_function(x, y):
            return x + y
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get the function name
            func_name = func.__name__

            # Print function call info with prefix if provided
            if prefix:
                print(f"\n[DEBUG] {prefix}")
            print(f"[DEBUG] Calling {func_name}")

            # Print args (excluding self for class methods)
            if args and hasattr(args[0], '__class__'):
                print(f"  Args: {args[1:]}")
            else:
                print(f"  Args: {args}")

            # Print kwargs
            if kwargs:
                print(f"  Kwargs: {kwargs}")

            # Call the function
            result = func(*args, **kwargs)

            # Print the result
            print(f"[DEBUG] {func_name} returned: {result}\n")

            return result

        return wrapper

    return decorator
