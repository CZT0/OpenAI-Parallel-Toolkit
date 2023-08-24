import logging
import multiprocessing
from typing import Dict

from openai_parallel_toolkit.api.keys import KeyManager
from openai_parallel_toolkit.api.model import OpenAIModel, Prompt
from openai_parallel_toolkit.api.request import parallel_request_openai, request_openai_api
from openai_parallel_toolkit.utils.logger import LOG_LABEL, Logger
from openai_parallel_toolkit.utils.process_bar import ProgressBar
from openai_parallel_toolkit.utils.reader import (
    count_null_values,
    filter,
    merge_jsonl_files,
    read_jsonl_to_dict,
    read_sort_write_jsonl,
    remove_nulls_from_jsonl,
)


class ParallelToolkit:
    def __init__(
        self,
        config_path: str,
        openai_model: OpenAIModel = OpenAIModel(),
        input_path: str = None,
        output_path: str = None,
        threads=multiprocessing.cpu_count() * 20,
        name="ParallelToolkit Progress",
        max_retries=5,
        log_level=logging.WARNING,
    ):
        self.key_manager = KeyManager(config_path=config_path)
        self.logger = Logger(level=log_level)
        self.input_path = input_path
        self.output_path = output_path
        self.threads = threads
        self.openai_model = openai_model
        self.name = name
        self.max_retries = max_retries

    def run(self):
        remove_nulls_from_jsonl(self.output_path)
        data = read_jsonl_to_dict(self.input_path)
        filtered_data = filter(data, self.output_path)
        if len(filtered_data) == 0:
            logging.warning(f"{LOG_LABEL}All data have been processed")
            return
        logging.warning(
            f"{LOG_LABEL}Data is being processed, waiting for the first returned result."
            f"If the progress bar hasn't moved for a long time, it's likely due to a network issue."
            f" Please refer to the section in the readme about setting up a proxy."
        )
        threads = min(len(filtered_data), self.threads, self.key_manager.get_key_length())
        threads = max(threads, 1)
        process_bar = ProgressBar(total=len(data), desc=self.name, initial=len(data) - len(filtered_data))
        parallel_request_openai(
            data=filtered_data,
            openai_model=self.openai_model,
            key_manager=self.key_manager,
            threads=threads,
            max_retries=self.max_retries,
            process_bar=process_bar,
            output_path=self.output_path,
        )
        read_sort_write_jsonl(self.output_path)
        process_bar.close()
        null_values = count_null_values(self.output_path)
        if null_values == 0:
            logging.warning(f"{LOG_LABEL}All data processing is complete")
        else:
            logging.warning(
                f"{LOG_LABEL}There are {null_values} data processing failures. "
                f"Please attempt to reprocess this data again. "
                f"If the data length exceeds the default model limit, "
                f"you can refer to the solution in the documentation and use gpt-3.5-turbo-16k-0613 for reprocessing."
            )

    def api(self, prompt: Prompt):
        return request_openai_api(
            openai_model=self.openai_model, prompt=prompt, key_manager=self.key_manager, max_retries=self.max_retries
        )

    def parallel_api(self, data: Dict[int, Prompt]):
        logging.warning(f"{LOG_LABEL}Data is being processed, waiting for the first returned result")
        process_bar = ProgressBar(total=len(data), desc=self.name)
        return parallel_request_openai(
            data=data,
            openai_model=self.openai_model,
            key_manager=self.key_manager,
            threads=self.threads,
            max_retries=self.max_retries,
            process_bar=process_bar,
            output_path=self.output_path,
        )

    def merge(self, merged_file):
        merge_jsonl_files(self.input_path, self.output_path, merged_file)
