import json
import os
import random
import time
import unittest

from openai_parallel_toolkit import ParallelToolkit

FILE = 1000


class MyParallelToolkit(ParallelToolkit):
    @staticmethod
    def process_output(data, output_file_without_ext):
        output_file = output_file_without_ext+".json"
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump({"result": data}, file, ensure_ascii=False)

    @staticmethod
    def process_input(file):
        return json.load(file)

    @staticmethod
    def process_data(data):
        time.sleep(random.uniform(0.1, 0.3))
        return data["data"] + "ok"


class TestMain(unittest.TestCase):
    def setUp(self):
        self.input_path = "../data/input"
        self.output_path = "../data/output"
        os.makedirs(self.input_path, exist_ok=True)
        for i in range(0, FILE):
            file_name = f"{i}.json"
            file_path = os.path.join(self.input_path, file_name)
            with open(file_path, "w") as file:
                data = {"data": str(i)}
                json.dump(data, file)

    def tearDown(self):
        self.clear_folder(self.output_path)
        self.clear_folder(self.input_path)

    def test_main(self):
        tool_kit = MyParallelToolkit(
            config_path="config.json",
            input_path=self.input_path,
            output_path=self.output_path
        )
        tool_kit.run()
        self.assertTrue(len(os.listdir(self.output_path)) == FILE)

        for file_name in os.listdir(self.output_path):
            file_path = os.path.join(self.output_path, file_name)
            with open(file_path, "r") as file:
                data = json.load(file)
                self.assertTrue(data["result"].endswith("ok"))

    @staticmethod
    def clear_folder(folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            if os.path.isfile(file_path):
                os.remove(file_path)


if __name__ == '__main__':
    unittest.main()
