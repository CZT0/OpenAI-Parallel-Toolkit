import unittest

from openai_parallel_toolkit.api import Gpt35Turbo, APIKeyManager
from openai_parallel_toolkit.core import multi_process_one


class TestMultithread(unittest.TestCase):
    def test_multi_process_one(self):
        data = [('hello1', 'world'), ('hello2', 'world'), ('hello3', 'world'), ('hello4', 'world'), ('hello5', 'world')]
        APIKeyManager(config_path="need_config/config.json", set_api_base=True)
        results = multi_process_one(data=data, openai_model_class=Gpt35Turbo, temperature=0.7)
        self.assertEqual(len(data), len(results))
        self.assertTrue(None not in results)

    if __name__ == '__main__':
        unittest.main()
