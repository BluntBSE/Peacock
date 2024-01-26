import ast
import inspect
import textwrap
import subprocess
import sys
import os


def get_function_code_with_dependencies(input_function, *args, **kwargs):
    # Get the source code of the function
    source_code = inspect.getsource(input_function)


    # Get the function signature
    signature = inspect.signature(input_function)
    parameters = list(signature.parameters.keys())
    # Create a dictionary with parameter values
    param_values = dict(zip(parameters, args))
    param_values.update(kwargs)


    # Find all functions called within the input function
    called_functions = [node.func.id for node in ast.walk(ast.parse(source_code)) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]


    # Include the source code of called functions in the modified code


    ##REWRITE THE BELOW TO BE RECURSIVE AND ADD SOURCE CODE OF ALL CALLED CHILDREN TO SOURCE_CODE##
    for func_name in called_functions:
        func = globals().get(func_name)
        if func:
            source_code += inspect.getsource(func)
    ##REWRITE THE ABOVE TO BE RECURSIVE AND ADD SOURCE CODE OF ALL CALLED CHILDREN TO SOURCE_CODE#


       
    # Convert the AST (Abstract Syntax Tree) of the source code
    tree = ast.parse(source_code)


    # Modify the AST to include parameter values
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg in param_values:
                    # Insert parameter value as default value in the function definition
                    arg.default = ast.Name(id=repr(param_values[arg.arg]), ctx=ast.Load())
            # Remove duplicated defaults
            node.args.defaults = [ast.Name(id=repr(param_values[arg.arg]), ctx=ast.Load()) for arg in node.args.args if arg.arg in param_values]


    # Convert the modified AST back to source code
    #WHY DOES MODIFIED CODE NOT INCLUDE DEEPER_CHILD?????
    modified_code = ast.unparse(tree)
    #At this point modified_code is a potentially huge string containing function definitions etc.
    print(modified_code)


    # Extract the name of the input function
    func_name = input_function.__name__


    # Add a function call to the dynamically imported function with specified arguments
    modified_code += f"\n_peacock_output = {func_name}(*{repr(args)}, **{repr(kwargs)})"


    return textwrap.dedent(modified_code)






