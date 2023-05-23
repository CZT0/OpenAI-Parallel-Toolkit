# Import the necessary libraries
import array
import datetime
import logging
import random
import threading
import time

import openai

from openai_parallel_toolkit.config import LOG_LABEL
from openai_parallel_toolkit.utils import read_keys, read_api_base
# Import related local modules
from .api import OpenAIModel


class APIKeyManager:
    """
    Class to manage the API keys of OpenAI. Implements the Singleton pattern.
    """
    _instance = None  # Singleton instance variable

    def __new__(cls, api_keys: array = None, config_path: str = None, set_api_base: bool = True):
        """
        Overload the __new__ method to create a singleton instance.
        If the instance doesn't exist, create it. If it does, return the existing instance.
        """
        if not cls._instance:
            if not api_keys:
                if config_path:
                    api_keys = read_keys(config_path)
                else:
                    raise Exception("No OpenAi keys available")
            if set_api_base:
                api_base = read_api_base(config_path)
                if api_base:
                    openai.api_base = api_base
            cls._instance = super().__new__(cls)
            cls._instance.__init_once(api_keys)
        cls.check_key_available(cls._instance)
        return cls._instance

    def __init_once(self, api_keys):
        """
        Initialize the instance.
        """
        self._api_keys = api_keys  # Store the keys
        self._key_lock = threading.Lock()  # Lock to manage concurrent access to keys
        self._key_failure_times = {key: None for key in api_keys}  # Record the failure time of each key
        self._key_status_lock = threading.Lock()  # Lock to manage concurrent access to key status
        self._key_status = {key: True for key in api_keys}  # The initial status of each key is True (available)
        openai.api_key = self.get_key  # Set the OpenAI API key to the first key in the list

    @property
    def get_key(self):
        """
        Getter for the keys, which shuffles the keys and returns the first one.
        """
        self.check_key_available()
        random.shuffle(self._api_keys)
        return self._api_keys[0]

    def remove_key(self, key):
        """
        Remove a key from the list.
        """
        with self._key_lock:
            if key in self._api_keys:
                self._api_keys.remove(key)
                self._key_failure_times.pop(key)
                self._key_status.pop(key)
                logging.warning(f"{LOG_LABEL}Removed key: {key}")
                openai.api_key = self.get_key
                logging.info(f"{LOG_LABEL}Switched to key: {openai.api_key}")

    def check_key_available(self):
        """
        Check if there is at least one key available.
        """
        if len(self._api_keys) == 0:
            logging.error(
                f"{LOG_LABEL} No OpenAI keys available. Please terminate the program and add keys to the config file.")
            raise Exception("No OpenAi keys available")

    def switch_api_key(self, openai_model: OpenAIModel):
        """Function to switch the API key, which is called when a rate limit error is encountered"""
        with self._key_status_lock:
            self._key_status[openai.api_key] = False
        with self._key_lock:
            if self._key_status[openai.api_key]:
                return None
            try:
                # Try generating a completion with the current key
                completion = openai_model.generate()
                return completion
            except Exception as e:
                # If a rate limit error occurs
                if "Rate limit" in str(e):
                    logging.info(f"{LOG_LABEL}Rate limit error encountered")
                    # Record the failure time of the current key
                    self._key_failure_times[openai.api_key] = datetime.datetime.now()
                    # Find a key that hasn't failed yet
                    for key, value in self._key_failure_times.items():
                        if value is None:
                            logging.info(f"{LOG_LABEL}Switched to key: {key}")
                            openai.api_key = key
                            return None
                    # Find keys that have been idle for at least 60 seconds
                    available_keys = [key for key, value in self._key_failure_times.items()
                                      if (datetime.datetime.now() - value).total_seconds() >= 60]
                    if available_keys:
                        # Switch to the first available key
                        openai.api_key = available_keys[0]
                        logging.info(f"{LOG_LABEL}Switched to key: {openai.api_key}")
                    else:
                        # If no keys are available, find the one that will be available soonest
                        min_key, min_value = min(self._key_failure_times.items(), key=lambda item: item[1])
                        next_time = min_value + datetime.timedelta(seconds=60)
                        # Wait until the next key becomes available
                        time_to_wait = (next_time - datetime.datetime.now()).total_seconds()
                        logging.info(
                            f"{LOG_LABEL}Waiting for key: {min_key} to become available in {time_to_wait} seconds")
                        time.sleep(time_to_wait)
                        logging.info(f"{LOG_LABEL}Switched to key: {min_key}")
                        openai.api_key = min_key
                else:
                    return None
            finally:
                # Mark the key as available
                with self._key_status_lock:
                    self._key_status[openai.api_key] = True
