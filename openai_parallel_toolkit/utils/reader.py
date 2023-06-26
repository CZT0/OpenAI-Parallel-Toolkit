import json
import logging
import os

from openai_parallel_toolkit.config import LOG_LABEL


def read_files(path):
    """
    Given a directory path, return a list of files within that directory.

    Args:
        path (str): The directory from which to read files.

    Returns:
        list: A list of filenames within the specified directory.
    """
    files = [
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and not os.path.splitext(f)[0].startswith(".")
    ]
    return files


def read_folder(input_path, output_path, process_input, file_count=None):
    """
    Process files from input_path with process_input function, skipping files already present in output_path.

    Args:
        input_path (str): The path to the directory containing input files.
        output_path (str): The path to the directory containing output files.
        process_input (function): Function to process the input file data.
        file_count (int, optional): Maximum number of files to process. Processes all if not specified. Default is None.

    Returns:
        dict: A dictionary mapping filenames (without extension) to processed data. Returns None if there's no data
        to process.
    """
    skipped_files_count = 0
    if output_path is not None:
        output_files = read_files(output_path)
        output_files_basename = [os.path.splitext(f)[0] for f in output_files]
        files = [f for f in read_files(input_path) if os.path.splitext(f)[0] not in output_files_basename][:file_count]
        skipped_files_count = len(output_files)
        logging.info(f"{LOG_LABEL}Output path: {output_path} Skipped files count: {skipped_files_count}")
    else:
        files = [
                    f for f in os.listdir(input_path) if
                    os.path.isfile(os.path.join(input_path, f)) and f[0] != "." and not os.path.splitext(f)[
                        0].startswith(
                            ".")
                ][:file_count]

    data = {}
    for file in files:
        file_path = os.path.join(input_path, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            file_name = os.path.splitext(file)[0]
            data[file_name] = process_input(f)
    if len(data) == 0:
        if skipped_files_count != 0:
            logging.info(f"{LOG_LABEL}All files have been processed: {input_path},file count: {skipped_files_count}")
            return None
        logging.error(f"{LOG_LABEL}input_path error, No data to process:{input_path}")
        return None
    return data


def partition_data(data, num_partitions):
    """
    Partition a dictionary into a specified number of smaller dictionaries.

    Args:
        data (dict): The dictionary to partition.
        num_partitions (int): The number of partitions to divide the dictionary into.

    Returns:
        list: A list of dictionaries representing the partitioned data.
    """
    partitions = [{} for _ in range(num_partitions)]
    data_items = list(data.items())

    for i, item in enumerate(data_items):
        partition_id = i % num_partitions
        partitions[partition_id][item[0]] = item[1]
    return partitions


def read_keys(config_path):
    """
    Read and return the 'api_keys' field from a JSON configuration file.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        str: The 'api_keys' field from the configuration file.
    """
    with open(config_path, 'r') as f:
        config = json.load(f)
        if 'api_keys' in config:
            return config['api_keys']
        raise Exception("No OpenAi keys available")


def read_api_base(config_path):
    """
    Read and return the 'api_base' field from a JSON configuration file.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        str: The 'api_base' field from the configuration file.
    """
    if not config_path:
        return None
    with open(config_path, 'r') as f:
        config = json.load(f)
    if 'api_base' in config:
        return config['api_base']
    return None
