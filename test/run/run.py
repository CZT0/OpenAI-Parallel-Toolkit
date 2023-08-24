import logging

from openai_parallel_toolkit import ParallelToolkit

if __name__ == "__main__":
    model = ParallelToolkit(
        config_path="/Users/jellow/code/python/OpenAI-Parallel-Toolkit/test/config_10.json",
        input_path="input.jsonl",
        output_path="output.jsonl",
        log_level=logging.INFO,
    )
    model.run()
    model.merge("merged.json")
