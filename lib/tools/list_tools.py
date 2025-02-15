import os
import inspect
import importlib.util

def list_tools() -> str:
    """List all tools in the tools directory and return their information."""
    try:
        # Get the current directory (tools directory)
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Get all Python files in the directory
        tool_files = [f for f in os.listdir(tools_dir) if f.endswith('.py')]
        
        tool_info = []
        for file_name in tool_files:
            module_name = file_name[:-3]  # Remove .py extension
            file_path = os.path.join(tools_dir, file_name)
            
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get all functions in the module
                functions = inspect.getmembers(module, inspect.isfunction)
                for func_name, func in functions:
                    # Get the docstring and signature
                    doc = inspect.getdoc(func) or 'No documentation available'
                    sig = str(inspect.signature(func))
                    
                    tool_info.append(
                        f"File: {file_name}\n"
                        f"Function: {func_name}{sig}\n"
                        f"Documentation: {doc}\n"
                    )
        
        return '\n'.join(tool_info) if tool_info else 'No tools found'
        
    except Exception as e:
        return f"Error listing tools: {str(e)}"