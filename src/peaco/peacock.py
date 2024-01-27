import inspect
import ast
import textwrap
import subprocess

# import arcpy
import sys
import os
import pandas as pd



def get_imports():
    with open(__file__, "r") as file:
        script_content = file.read()

    import_lines = []
    inside_function = False

    for line in script_content.splitlines():
        line = line.strip()
        if line.startswith("def "):
            inside_function = True
        elif line.startswith("import") or line.startswith("from"):
            if not inside_function:
                import_lines.append(line)
        elif line.startswith(")"):
            inside_function = False

    return "\n".join(import_lines)

def get_imports_from_path(path):
    with open(path, "r") as file:
        script_content = file.read()

    import_lines = []
    inside_function = False

    for line in script_content.splitlines():
        line = line.strip()
        if line.startswith("def "):
            inside_function = True
        elif line.startswith("import") or line.startswith("from"):
            if not inside_function:
                import_lines.append(line)
        elif line.startswith(")"):
            inside_function = False

    return "\n".join(import_lines)


def get_function_code_with_dependencies_recursive(input_function, *args, **kwargs):
    # Get the source code of the function
    source_code = inspect.getsource(input_function)

    # Get the function signature
    signature = inspect.signature(input_function)
    parameters = list(signature.parameters.keys())
    # Create a dictionary with parameter values
    param_values = dict(zip(parameters, args))
    param_values.update(kwargs)

    # Find all functions called within the input function

    # Include the source code of called functions in the modified code

    # function that recursively returns a list of node.func.ids for all functions called within a function that is a parameter
    def get_called_functions(i_function):
        ids = []
        i_source = inspect.getsource(i_function)
        i_called_functions = [
            node.func.id
            for node in ast.walk(ast.parse(i_source))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        for id in i_called_functions:
            if id not in ids:
                ids.append(id)
                i_func = globals().get(id)
                if i_func:
                    ids += get_called_functions(i_func)

        return ids

    called_functions = get_called_functions(input_function)

    for func_name in called_functions:
        func = globals().get(func_name)
        if func:
            source_code += inspect.getsource(func)

    # Convert the AST (Abstract Syntax Tree) of the source code
    tree = ast.parse(source_code)

    # Modify the AST to include parameter values
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg in param_values:
                    # Insert parameter value as default value in the function definition
                    arg.default = ast.Name(
                        id=repr(param_values[arg.arg]), ctx=ast.Load()
                    )
            # Remove duplicated defaults
            node.args.defaults = [
                ast.Name(id=repr(param_values[arg.arg]), ctx=ast.Load())
                for arg in node.args.args
                if arg.arg in param_values
            ]

    # Convert the modified AST back to source code

    modified_code = ast.unparse(tree)
    # At this point modified_code is a potentially huge string containing function definitions etc.
    # print(modified_code)

    # Extract the name of the input function
    func_name = input_function.__name__

    # Add a function call to the dynamically imported function with specified arguments
    modified_code += f"\n_peacock_output = {func_name}(*{repr(args)}, **{repr(kwargs)})"

    return textwrap.dedent(modified_code)


def fan_data(function, targets):
    #print the filename of the function passed in
    func_path = function.__code__.co_filename



    # Make sure that whatever python executable called this script is used to call child processes.
    py_prefix = sys.exec_prefix
    py_path = sys.executable

    # current_dir = path of the directory that this script is in
    current_dir = os.path.dirname(os.path.realpath(__file__))
    daemon_path = os.path.join(current_dir, "daemon.py")

    args_array = [py_path, daemon_path]
    # The first two arguments in args_array are the python executable and the daemon script.
    # You can add additional arguments to args_array here. They will be passed to the daemon script.
    # Access those arguments with sys.argv in the daemon script.

    for target in targets:
        execution_string = get_imports_from_path(func_path)
        execution_string += "\n"
        execution_string += get_function_code_with_dependencies_recursive(
            function, target
        )
        args_array.append(execution_string)

        # When calling subprocess, all arguments will be stringified. That's why we don't just pass an entire array here, but append each item.
        # You can avoid having to call subprocess if you are willing to run your script from the command line.

        # We use "subprocess" to open a new python process that then manages the daemons.
        # We do this because multiprocessing is not possible out of a mark
        # Check_output is friendly to Python 2.7. There are more options in Python 3.
        # Children of the subprocess can only report their output via print(), not ArcPy.AddMessage.
        # Recommend writing a function that logs to both.

    try:
        print("Trying")
        result = subprocess.check_output(args_array, stderr=subprocess.STDOUT, text=True)
        #Wait for subprocess to finish before assinging result
        output_list = ast.literal_eval(result)
        return output_list
    except subprocess.CalledProcessError as e:
        print("Excepting")
        raise e
