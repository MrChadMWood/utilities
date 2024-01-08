import json
import boto3
import os
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
This Python script provides functions to retrieve parameters from 
AWS Systems Manager (SSM) Parameter Store, read local files in JSON 
format, map keys to SSM parameters, and generate Docker secrets files 
and environment variable files.

Using `main` is recommended as it performs sanitation checks prior
to calling parameters from AWS.

This program exjects files in the working directory named:
    docker-secrets.json
    docker-env.json

Either file is a flat JSON file.
For docker-secrets.json, keys represent desired filenames and values represent AWS SSM parameter path/name
For docker-env.json, keys represent desired env-var keys and values represent AWS SSM parameter path/name

This program is not omnipotent. Running once will generate files and running again will raise error 
while those files are undeleted.
"""


def check_for_secrets(output_directory=".secrets", **kwargs):
    """
    Check if Docker secrets already exist in the specified directory.

    Args:
        output_directory (str, optional): Path to the Docker secrets directory. Default is '.secrets'.

    Raises:
        FileExistsError: If Docker secrets already exist in the specified directory.
    """
    secrets_exist = os.path.exists(output_directory) and os.listdir(output_directory)
    if secrets_exist:
        raise FileExistsError(f"Docker secrets already exist in directory: {output_directory}")


def check_for_env(output_file=".env", **kwargs):
    """
    Check if Docker environment file already exists.

    Args:
        output_file (str, optional): Path to the Docker environment file. Default is '.env'.

    Raises:
        FileExistsError: If Docker environment file already exists.
    """
    env_file_exists = os.path.exists(output_file)
    if env_file_exists:
        raise FileExistsError(f"Docker environment file already exists: {output_file}")
    

def retrieve_parameters(parameter_names: list, with_decryption=True, region='us-west-1', deconstruct=False):
    """
    Retrieve parameters from AWS Systems Manager (SSM) Parameter Store.

    Args:
        parameter_names (list): List of parameter names.
        with_decryption (bool, optional): Whether to retrieve the parameters in decrypted form using KMS.
        region (str, optional): The AWS region. Default is 'us-west-1'.
        deconstruct (bool, optional): Whether to convert the response into a dictionary of key, value pairs.

    Returns:
        If deconstruct is True, returns a dictionary containing parameter names as keys
        and their values from the get_parameters API call.
        If deconstruct is False, returns the response from the get_parameter API call.
    """

    # Create an SSM client
    client = boto3.client('ssm', region_name=region)

    # Retrieve parameters in one call
    response = client.get_parameters(
        Names=parameter_names,
        WithDecryption=with_decryption
    )

    if deconstruct:
        # Create a dictionary to store parameter names and values
        response = {param['Name']: param['Value'] for param in response['Parameters']}

    return response


def read_local_file(file_path: str = "docker-secrets.json|docker-env.json", raise_errors=False):
    """
    Read a local JSON file containing secrets or environment variables.

    Args:
        file_path (str): Path to the local file to read. Expected format is JSON.
        raise_errors (bool): If True, raise a ValueError for invalid file paths or non-existent files.

    Returns:
        None or A dictionary containing key-value pairs from the specified local JSON file.
        
    Raises:
        ValueError: If the provided file_path is not one of the expected paths
                    ("docker-secrets.json" or "docker-env.json") and raise_errors is True.
        FileNotFoundError: If raise_errors is True and the file_path does not exist.
    """

    expected_paths = ('docker-secrets.json', 'docker-env.json')
    if file_path not in expected_paths and raise_errors:
        raise ValueError(f'Expected file paths include: {", ".join(expected_paths)}')
    
    if os.path.isfile(file_path) or raise_errors:
        with open(file_path, 'r') as file:
            data = json.load(file)
            logger.info(f'Read {file_path} with {len(data)} entries.')
        return data


def map_keys_to_ssm_params(param_dict: {str: str}, region='us-west-1'):
    """
    Iterate through key-value pairs where each key is a filename or environment variable key,
    and each value is an SSM parameter name. Retrieve the SSM parameter values and return a dictionary with secret values.

    Args:
        param_dict (dict): Dictionary with (filename | env-key) as key and SSM parameter name as value.
        region (str, optional): The AWS region. Default is 'us-west-1'.

    Returns:
        A dictionary containing key-value pairs with filename or environment variable key as key
        and SSM parameter values as value.
    """
    param_names = list(param_dict.values())
    ssm_params = retrieve_parameters(parameter_names=param_names, region=region, deconstruct=True)
    
    return {key: ssm_params[param_name] for key, param_name in param_dict.items()}


def generate_docker_secrets_files(secrets_dict, output_directory=".secrets", raise_if_unsanitized=True, **kwargs):
    """
    Use the returned dictionary to generate a Docker .secrets directory.

    Args:
        secrets_dict (dict): Dictionary with filename or environment variable key as key
        and SSM parameter values as value.
        output_directory (str, optional): Path to the output Docker secrets directory. Default is '.secrets_docker'.
    """
    if raise_if_unsanitized:
        check_for_secrets(output_directory=output_directory)

    # Create the Docker secrets directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Write the secret values to individual files in the Docker secrets directory
    for filename, value in secrets_dict.items():
        secret_file_path = os.path.join(output_directory, filename)
        with open(secret_file_path, 'w') as secret_file:
            secret_file.write(value)
            logger.info(f'Wrote {secret_file_path}.')


def generate_docker_env_file(variables_dict, output_file=".env", raise_if_unsanitized=True, **kwargs):
    """
    Create a .env file string for Docker using the provided variables dictionary and save the result.

    Args:
        variables_dict (dict): Dictionary with variable names as keys and their values.
        output_file (str, optional): Path to the output Docker environment variables file. Default is '.env'.
    """
    if raise_if_unsanitized:
        check_for_env(output_file=output_file)

    # Create the Docker environment variables string
    docker_env_string = "\n".join([f"{name}={value}" for name, value in variables_dict.items()])

    # Save the Docker environment variables string to the output file
    with open(output_file, 'w') as env_file:
        env_file.write(docker_env_string)
        logger.info(f'Wrote {output_file}.')


def collect_env_params(param_names=[], env_map_file_path='docker-env.json', region='us-west-1'):
    """
    Collects environment parameters from AWS Systems Manager (SSM) Parameter Store.

    Args:
        param_names (list, optional): List of parameter names to retrieve from SSM.
                                      If not provided, it attempts to read from the 'docker-env.json' file.
        env_map_file_path (str, optional): Path to the 'docker-env.json' file.
                                           Default is 'docker-env.json' in the working directory.
        region (str, optional): The AWS region. Default is 'us-west-1'.

    Returns:
        A dictionary containing key-value pairs with parameter names as keys
        and their values from the get_parameters API call.
    Raises:
        ValueError: If param_names is empty and env_map_file_path is not found.
    """
    if not param_names:
        if os.path.exists(env_map_file_path):
            param_dict  = read_local_file(env_map_file_path)
            param_names = list(param_dict.values())
        else:
            raise ValueError('Must supply parameter names.')
        
    ssm_params = retrieve_parameters(parameter_names=param_names, region=region, deconstruct=True)
    return ssm_params
    
    
def main():
    jobs = {}
    config = {}
    secrets_map = 'docker-secrets.json'
    env_map = 'docker-env.json'

    # Handles checking for existing values before req of values
    if os.path.exists(secrets_map):
        jobs.update({secrets_map: generate_docker_secrets_files})
        config.update({'output_directory': '.secrets'})
        check_for_secrets(**config)

    # Handles checking for existing values before req of values
    if os.path.exists(env_map):
        jobs.update({env_map: generate_docker_env_file})
        config.update({'output_file': '.env'})
        check_for_env(**config)

    # Requests values as needed, generates output files dynamically
    for file_path, processor_func in jobs.items():
        param_dict = read_local_file(file_path)
        data       = map_keys_to_ssm_params(param_dict)
        processor_func(data, raise_if_unsanitized=False, **config)


if __name__ == '__main__':
    main()
