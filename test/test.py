import unittest

from openai_parallel_toolkit import OpenAIModel, ParallelToolkit, Prompt


class TestApi(unittest.TestCase):
    def test_api(self):
        prompt = Prompt(instruction="Please write a sentence about the following topic: ", input="flowers")
        model = OpenAIModel("gpt-3.5-turbo", temperature=0.1)
        ans = ParallelToolkit(config_path="config.json", openai_model=model).api(prompt=prompt)
        print(ans)
        self.assertTrue(len(ans) > 0)


class TestParallelApi(unittest.TestCase):
    def test_parallel_api(self):
        data = {i: Prompt(instruction="Please write a sentence about the following topic: ", input="china") for
                i in
                range(10)}
        ans = ParallelToolkit(config_path="config.json").parallel_api(data=data)
        print(ans)
        self.assertTrue(len(ans) == 10)


class TestRun(unittest.TestCase):
    def test_run(self):
        ParallelToolkit(config_path="config.json",
                        input_path="data.jsonl",
                        output_path="output.jsonl").run()
