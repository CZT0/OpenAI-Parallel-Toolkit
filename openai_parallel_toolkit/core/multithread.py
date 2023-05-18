import concurrent
import logging
import multiprocessing
import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Type

from openai_parallel_toolkit.api import APIKeyManager
from openai_parallel_toolkit.api import request_openai_api, OpenAIModel
from openai_parallel_toolkit.config import LOG_LABEL
from openai_parallel_toolkit.utils import ProgressBar, partition_data, read_folder, logger_init


def process_data_chunk(data_chunk, output_path, process_output, process_data):
    """Process a chunk of data and write results to output file.

    Args:
        data_chunk (dict): The data chunk to be processed.
        output_path (str): The path of the output file.
        process_output (function): The function used to process the output.
        process_data (function): The function used to process the data.
    """
    for key, value in data_chunk.items():
        data = process_data(value)
        if output_path is not None:
            output_file_without_ext = os.path.join(output_path, key)
            process_output(data, output_file_without_ext)
            ProgressBar().get_instance().update()


def multi_process_one(data: list, openai_model_class: Type[OpenAIModel], threads=multiprocessing.cpu_count() * 5,
                      **kwargs):
    """Request OpenAI API in parallel using multiple threads.

    Args:
        data (list): The data to be processed.
        openai_model_class (Type[OpenAIModel]): The OpenAI model class to use.
        threads (int, optional): The number of threads to use. Defaults to 5 times the number of CPUs.
        **kwargs: Additional arguments for the OpenAI model class.

    Returns:
        list: The results from the OpenAI API.
    """
    with ThreadPoolExecutor(max_workers=threads) as executor:
        try:
            results = list(
                executor.map(lambda item: request_openai_api(
                    openai_model_class(prompt=item[0], content=item[1], **kwargs)),
                             data))
        except Exception as e:
            tb = traceback.format_exc()
            logging.error(f"{LOG_LABEL}Error occurred while processing data: {e}\n{tb}")
            return None
    return results


def multi_thread_run(config_path, input_path, file_count, output_path, process_input, process_output, process_data,
                     num_threads=multiprocessing.cpu_count() * 10, name="Progress"):
    logger_init()
    """Run the processing task using multiple threads.

    Args:
        config_path (str): The path of the configuration file.
        input_path (str): The path of the input file.
        file_count (int): The number of files to be processed.
        output_path (str): The path of the output file.
        process_input (function): The function used to process the input.
        process_output (function): The function used to process the output.
        process_data (function): The function used to process the data.
        num_threads (int, optional): The number of threads to use. Defaults to 10 times the number of CPUs.
        name (str, optional): The name of the progress bar. Defaults to "Progress".
    """
    APIKeyManager(config_path=config_path)
    if output_path is not None:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
    data = read_folder(input_path=input_path, file_count=file_count, output_path=output_path,
                       process_input=process_input)
    if data is None:
        return
    ProgressBar.get_instance(total=len(data), desc=name)  # Initialize the progress bar
    threads = min(len(data), num_threads)  # Determine the number of threads to use
    data_chunks = partition_data(data, threads)  # Partition the data into chunks for each thread

    # Use ThreadPoolExecutor to manage our threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for i in range(threads):
            # For each thread, submit the data chunk to be processed
            futures.append(executor.submit(process_data_chunk,
                                           data_chunk=data_chunks[i], output_path=output_path,
                                           process_output=process_output,
                                           process_data=process_data))

        # As each future completes, check if there was an exception and log the error if so
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                tb = traceback.format_exc()
                logging.fatal(f"{LOG_LABEL}Error occurred while processing data: {e}\n{tb}")
    ProgressBar().get_instance().close()
    ProgressBar().get_instance().destroy()  # Close the progress bar when all threads are done
