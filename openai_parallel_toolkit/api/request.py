import json
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from threading import Lock
from typing import Dict, Optional, Tuple

from openai_parallel_toolkit.utils.logger import LOG_LABEL
from openai_parallel_toolkit.utils.process_bar import ProgressBar
from .keys import KeyManager
from .model import OpenAIModel, Prompt


def request_openai_api(openai_model: OpenAIModel, prompt: Prompt, key_manager: KeyManager, max_retries: int) -> \
        Optional[str]:
    key = key_manager.get_new_key()
    completion = None  # Initialize the completion variable
    attempts = 0  # Initialize attempts

    while attempts < max_retries:
        try:
            # Attempt to generate a completion
            openai_model.set_key(key)
            completion = openai_model.generate(instruction=prompt.instruction, input=prompt.input)
            logging.info(f"{LOG_LABEL}key {key} ,request ok")
            key_manager.release_key(key)
            break
        except Exception as e:
            # Handle different types of errors
            if "exceeded your current quota" in str(e) or "<empty message>" in str(e) or "Limit: 200 / day" in str(e):
                # If the quota has been exceeded, remove the key and try again
                key_manager.remove_key(key)
                key = key_manager.get_new_key()
                continue
            if "Limit: 3 / min" in str(e) or "Limit: 40000 / min" in str(e):
                # If the rate limit is hit, switch the API key and try again
                key = key_manager.get_new_key(key)
                continue
            if "maximum context length" in str(e):
                # If the context length is too long, log an error and break the loop
                logging.error(f"{LOG_LABEL}Error occurred while accessing openai API: {e}")
                break
            if "Max retries exceeded with url" in str(e):
                # If retries are exceeded, try again
                continue
            if "That model is currently overloaded with other requests" in str(e):
                # If the model is overloaded, try again
                continue
            if "The server is overloaded" in str(e):
                continue
            # If an unknown error occurs, log an error and increment the attempt counter
            logging.error(
                    f"{LOG_LABEL}Unknown error occurred while accessing OpenAI API: {e}. Retry attempt {attempts + 1} "
                    f"of "
                    f"{max_retries}")
            attempts += 1

    if not completion:
        return None

    output = completion['choices'][0]['message']['content'].strip()

    return output


def request_openai_api_with_tqdm(item: Tuple[int, Prompt], openai_model: OpenAIModel, key_manager: KeyManager,
                                 process_bar: ProgressBar, lock: Lock, max_retries: int, output_path: str = None):
    key, prompt = item
    result = request_openai_api(openai_model=openai_model, prompt=prompt, key_manager=key_manager,
                                max_retries=max_retries)

    if output_path:
        with lock:
            with open(output_path, 'a') as file:
                file.write(json.dumps({key: result}, ensure_ascii=False) + '\n')
                file.flush()
    process_bar.update()
    return result


def parallel_request_openai(data: Dict[int, Prompt], openai_model: OpenAIModel,
                            threads: int, key_manager: KeyManager, max_retries: int,
                            process_bar: ProgressBar,
                            output_path: str):
    lock = Lock()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        request_func = partial(request_openai_api_with_tqdm, openai_model=openai_model, key_manager=key_manager,
                               max_retries=max_retries, process_bar=process_bar, output_path=output_path, lock=lock)
        results = []
        for prompt in data.items():
            try:
                result = executor.submit(request_func, prompt)
                results.append(result)
            except Exception as e:
                tb = traceback.format_exc()
                logging.error(f"{LOG_LABEL}Error occurred while processing prompt {prompt[0]}: {e}\n{tb}")

    # Wait for all tasks to complete, regardless of whether they were successful or not
    results = [future.result() for future in as_completed(results)]

    return results
