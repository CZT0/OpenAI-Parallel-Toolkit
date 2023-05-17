import unittest

from openai_parallel_toolkit import Gpt35Turbo, request_openai_api, APIKeyManager


class TestGPT35(unittest.TestCase):

    def test_test_gpt_35(self):
        APIKeyManager(config_path="config.json", set_api_base=True)
        result = Gpt35Turbo(content="hello world", prompt="", temperature=0.7).generate()
        self.assertTrue(len(result) > 0)

    def test_request_openai_api(self):
        model = Gpt35Turbo(content="hello world", prompt="", temperature=0.7)
        result = request_openai_api(openai_model=model, config_path="config.json")
        self.assertTrue(len(result) > 0)


if __name__ == '__main__':
    unittest.main()
