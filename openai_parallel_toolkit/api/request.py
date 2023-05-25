import logging
import random
import time

import openai

# Import related local modules
from .api import OpenAIModel
from .keys import APIKeyManager
from ..config import LOG_LABEL


def request_openai_api(openai_model: OpenAIModel, keys=None, config_path=None, max_retries=5):
    """Function to handle requests to the OpenAI API.

    Args:
        openai_model (OpenAIModel): Instance of the OpenAIModel class that will generate the completion.
        keys (list, optional): List of API keys. Defaults to None.
        config_path (str, optional): Path to the configuration file. Defaults to None.
        max_retries (int, optional): Maximum number of retries in case of failures. Defaults to 5.

    Returns:
        str: The generated content from the completion.
    """

    # Initialize the APIKeyManager
    key_manager = APIKeyManager(api_keys=keys, config_path=config_path)

    completion = None  # Initialize the completion variable
    attempts = 0  # Initialize attempts

    while attempts < max_retries:
        key = openai.api_key  # Get the current API key

        try:
            # Attempt to generate a completion
            time.sleep(random.uniform(0, 0.2))  # Sleep for 0-0.2s seconds to avoid infinite requests
            completion = openai_model.generate()
            break
        except Exception as e:
            # Handle different types of errors
            if "exceeded your current quota" in str(e) or "<empty message>" in str(e):
                # If the quota has been exceeded, remove the key and try again
                key_manager.remove_key(key)
                continue
            if "Rate limit" in str(e):
                # If the rate limit is hit, switch the API key and try again
                completion = key_manager.switch_api_key(openai_model)
                if completion is None:
                    continue
                break
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
            # If an unknown error occurs, log an error and increment the attempt counter
            logging.error(
                f"{LOG_LABEL}Error occurred while accessing openai API: {e}. Retry attempt {attempts + 1} of {max_retries}")
            attempts += 1

    if completion is None:
        return None

    # Extract the generated message content from the completion
    output = completion['choices'][0]['message']['content'].strip()

    # Uncomment the following line if you need the total token count
    # token = completion['usage']['total_tokens']

    return output
