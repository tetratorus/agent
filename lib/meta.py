from functools import wraps
import time
import json
from typing import Any

class AgentMeta(type):
    def __new__(mcs, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and not attr_name.startswith('__'):
                attrs[attr_name] = mcs._wrap_with_logging(attr_value)
        return super().__new__(mcs, name, bases, attrs)

    @staticmethod
    def _wrap_with_logging(func):
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            class_name = self.__class__.__name__
            func_name = func.__name__

            if not hasattr(self, 'log_handler'):
                raise AttributeError(f"Missing log_handler in {class_name}. Did you forget to set it?")
            if not callable(self.log_handler):
                raise TypeError(f"log_handler in {class_name} must be callable, got {type(self.log_handler)}")
            if not hasattr(self, 'debug_verbose'):
                raise AttributeError(f"Missing debug_verbose in {class_name}. Did you forget to set it?")

            # Combine args and kwargs for semantic clarity
            inputs = {}
            if args and hasattr(args[0], '__class__'):  # Skip self
                inputs.update({f"arg{i}": arg for i, arg in enumerate(args[1:])})
            else:
                inputs.update({f"arg{i}": arg for i, arg in enumerate(args)})
            inputs.update(kwargs)
            inputs_length = len(json.dumps(inputs))

            start_time = time.time()
            result = func(self, *args, **kwargs)
            execution_time = time.time() - start_time
            result_length = len(json.dumps(result))

            if self.debug_verbose:
                messages = [
                    f"\n[{class_name}.{func_name}]",
                    f"  Inputs: {inputs}",
                    f"  Inputs length: {inputs_length}",
                    f"  Result: {result}",
                    f"  Result length: {result_length}",
                    f"  Time: {execution_time:.4f}s\n"
                ]
            else:
                messages = [f"[{class_name}.{func_name}] inputs_len: {inputs_length}, result_len: {result_length}\n"]

            for message in messages:
                self.log_handler(message)

            return result
        return wrapper
