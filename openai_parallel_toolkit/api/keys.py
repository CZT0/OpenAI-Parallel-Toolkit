import logging
import random
import threading
import time

import openai
from cachetools import TTLCache

from openai_parallel_toolkit.utils.logger import LOG_LABEL
from openai_parallel_toolkit.utils.reader import read_config


class KeyManager:

    def __init__(self, config_path: str = None):
        """
        Initialize the instance.
        """
        if not config_path:
            raise Exception("No OpenAI keys available")

        api_keys, api_base = read_config(config_path)
        openai.api_base = api_base
        self.keys = set(api_keys)  # All keys
        self.using_keys = set()  # Keys that have been used
        self.limited_keys = TTLCache(maxsize=len(self.keys),
                                     ttl=30)  # Keys that have reached the request limit
        self.using_keys_lock = threading.Lock()  # Lock for keys and using_keys
        # self.limited_keys_lock = threading.Lock()  # Separate using_keys_lock for limited_keys

    def get_new_key(self, key=None) -> str:
        """
        Get a new key. The key is one that is in keys but not in using_keys or limited_keys.
        """
        min_ttl = None
        min_key = None
        with self.using_keys_lock:
            logging.info(f"{LOG_LABEL} {key} get lock ")
            self.limited_keys.expire()
            unused_keys = self.keys - self.using_keys - set(self.limited_keys.keys())
            logging.info(f"{LOG_LABEL}unused_keys {len(unused_keys)}")
            if key:
                logging.info(f"{LOG_LABEL}locked {key}")
                self.limited_keys[key] = time.time()
                self.using_keys.discard(key)
            if unused_keys:
                logging.info(f"{LOG_LABEL} limited_keys {len(self.limited_keys.keys())}")
                new_key = random.choice(list(unused_keys))
                self.using_keys.add(new_key)
                return new_key
            else:
                logging.info(f"{LOG_LABEL}keys {len(self.keys)}")
                logging.info(f"{LOG_LABEL}using_keys {len(self.using_keys)}")
                logging.info(f"{LOG_LABEL}limited_keys {len(self.limited_keys.keys())}")
                if len(self.keys) == 0:
                    raise Exception("No OpenAI keys available,All keys have expired")
                else:
                    min_key, min_ttl = self.get_min_ttl_key()
                    if min_ttl:
                        logging.info(f"{LOG_LABEL}min_ttl {min_ttl}, min_key {min_key}")
                        self.limited_keys.pop(min_key)
                        self.using_keys.add(min_key)
            logging.info(f"{LOG_LABEL} {key}  leave lock ")

        if min_ttl:
            time.sleep(min_ttl)
            return min_key
        else:
            time.sleep(random.randint(1, 5))
            return self.get_new_key()

    def release_key(self, key):
        """
        Release a key. The key is removed from using_keys.
        """
        self.using_keys.discard(key)

    def remove_key(self, key):
        """
        Remove a key. The key is removed from keys.
        """
        with self.using_keys_lock:
            self.keys.discard(key)
            self.using_keys.discard(key)
            self.limited_keys.pop(key)
        logging.warning(f"{LOG_LABEL}remove_key {key}")

    def get_key_length(self):
        return len(self.keys)

    def get_min_ttl_key(self):
        if not self.limited_keys:
            return None, None
        now = time.time()
        # Get the remaining TTL for each key and put them in a list
        valid_keys = [(self.limited_keys[key] + self.limited_keys.ttl - now, key)
                      for key in self.limited_keys if self.limited_keys[key] + self.limited_keys.ttl - now > 0]

        min_ttl_key = min(valid_keys)
        return min_ttl_key[1], min_ttl_key[0],
