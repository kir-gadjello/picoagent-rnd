import inspect
from types import ModuleType
from schema_generator import generate_schema
import tool_defs
import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter
from util import printd

def json_to_highlighted_str(json_data, strip=True):
    json_str = json.dumps(json_data, indent=4)
    lexer = JsonLexer()
    formatter = TerminalFormatter()
    highlighted_str = highlight(json_str, lexer, formatter)
    if strip:
        highlighted_str = highlighted_str.strip()
    return highlighted_str

def load_function_set(module: ModuleType, ignore_by_prefixes=["noexport_"]) -> dict:
    """Load the functions and generate schema for them, given a module object"""
    function_dict = {}

    for attr_name in dir(module):
        # Get the attribute
        attr = getattr(module, attr_name)

        # Check if it's a callable function and not a built-in or special method
        if inspect.isfunction(attr) and attr.__module__ == module.__name__:
            skip = False
            if len(ignore_by_prefixes):
                for prefix in ignore_by_prefixes:
                    if attr_name.startswith(prefix):
                        printd(f"Skipping function {attr_name} due to ignore_by_prefixes={ignore_by_prefixes}")
                        skip = True
            if skip:
                continue

            if attr_name in function_dict:
                raise ValueError(f"Found a duplicate of function name '{attr_name}'")

            generated_schema = generate_schema(attr)
            function_dict[attr_name] = {
                "python_function": attr,
                "json_schema": generated_schema,
            }

    if len(function_dict) == 0:
        raise ValueError(f"No functions found in module {module}")
    
    return function_dict

def load_fn_as_tool(fn):
    # Check if it's a callable function and not a built-in or special method
    if inspect.isfunction(fn): # and attr.__module__ == module.__name__:
        # if attr_name in function_dict:
        #     raise ValueError(f"Found a duplicate of function name '{attr_name}'")

        generated_schema = generate_schema(fn)
        return {
            "python_function": fn,
            "json_schema": generated_schema,
        }

available_tools = load_function_set(tool_defs)