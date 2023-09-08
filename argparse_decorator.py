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
    # test_app.py
    
    @argparse_decorator
    def foo(a: list, b: str, c: str = "default value"):
        print(f'a: {}\nb: {b}\nc: {c}')

    if __name__ == "__main__":
        foo()
    ```
    From Command Line:
    ```
    # python -m test_app --a=1 2 3 --b="s", --c="not default value"
    
    a: ['1', '2', '3']
    b: s
    c: not default value
    ```
    '''
    parameters = inspect.signature(func).parameters
    param_names = list(parameters.keys())

    def wrapper(*args, **kwargs):
        parser = argparse.ArgumentParser()

        for param_name, param_info in parameters.items():
            param_type = param_info.annotation or type(param_info.default)
            
            arg_config = {}
            if param_type == list:
                arg_config.update({'nargs': '*'})
                param_type = str
            
            # If the parameter has a default value
            if param_info.default != inspect.Parameter.empty:
                # Use the default value as the argparse default
                arg_config.update({'default': param_info.default})
            
            arg_config['type'] = param_type
            parser.add_argument(f'--{param_name}', **arg_config)

        args_namespace = parser.parse_args()
        args_dict = vars(args_namespace)
        user_specified_args = {k: v for k, v in args_dict.items() if v is not None}
        return func(**user_specified_args)

    return wrapper
