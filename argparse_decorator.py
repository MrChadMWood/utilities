import argparse
import inspect

def argparse_decorator(func):
    '''
    A decorator that automatically converts a decorated function's parameters into command-line
    arguments using argparse. This decorator handles parameters with type annotations and default
    values correctly.

    Parameters:
        func (callable): The function to be decorated.

    Returns:
        callable: A decorated function that can be called from the command line with argparse-
        generated arguments.

    Example usage:
    ```
    @argparse_decorator
    def foo(a: list, b: str, c: float = 3.14):
        print(f'a: {a}\nb: {b}\nc: {c}')

    if __name__ == "__main__":
        foo()
    ```
    '''
    parameters = inspect.signature(func).parameters
    param_names = list(parameters.keys())

    def wrapper(*args, **kwargs):
        parser = argparse.ArgumentParser()

        for param_name, param_info in parameters.items():
            param_type = param_info.annotation or type(param_info.default)
            
            # If the parameter has a default value
            if param_info.default != inspect.Parameter.empty:
                # Use the default value as the argparse default
                parser.add_argument(f'--{param_name}', type=param_type, default=param_info.default)
            else:
                # The argument is required without a default val
                parser.add_argument(f'--{param_name}', type=param_type, required=True)

        args_namespace = parser.parse_args()
        args_dict = vars(args_namespace)
        return func(**args_dict)

    return wrapper
