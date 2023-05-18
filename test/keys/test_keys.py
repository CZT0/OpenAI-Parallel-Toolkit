import unittest

from openai_parallel_toolkit.api.api import Gpt35Turbo
from openai_parallel_toolkit.api.keys import APIKeyManager
from openai_parallel_toolkit.api.request import request_openai_api


# This may cause problems with API Key Manager, so test it separately
class TestKeys(unittest.TestCase):
    def test_set_keys_with_empty_list(self):
        with self.assertRaises(ValueError) as context:
            api_keys = []
            APIKeyManager(api_keys)

        self.assertEqual(str(context.exception), "No OpenAi keys available")

    def test_set_keys_with_expire_key(self):
        with self.assertRaises(ValueError) as context:
            api_keys = [
                "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"
            ]
            model = Gpt35Turbo(content="", prompt="", temperature=0.7)
            request_openai_api(model, keys=api_keys)

            print(str(context.exception))
            self.assertEqual(str(context.exception), "No OpenAi keys available")

    if __name__ == '__main__':
        unittest.main()
