# OpenAI Parallel Toolbox

**English** | [中文](README.md)

This project leverages the key of the OpenAI $5 account. By purchasing a large number of $5 keys and combining key management and multi-threaded parallel processing of large amounts of data, it bypasses the limitation of only 3 requests per minute for a $5 account.

The speed of parallel processing is the number of keys/20, i.e., the speed of 20 keys is 1 it/s, 40 keys is 2 it/s, and so on. Please note that each account can only request 200 times per day.

The default model is `gpt-3.5-turbo-0613`. If your context is too long, you can use the [custom model](#custom-model-and-passing-model-parameters) after running it once, specifying `gpt-3.5-turbo-16k-0613` to run again, which will continue to process the unprocessable data.

## Features

1. ✅ Automatically rotate OpenAI API keys when usage reaches the limit, built-in error handling, and automatic retry mechanism.
2. ✅ Provides a solution for proxy access to OpenAI services in China.
3. ✅ Supports parallel processing of API and file operations, optimizing throughput and efficiency, supports checkpoint continuation.

## Installation

```bash
pip install openai-parallel-toolkit
```

## Usage

Three usage methods are currently provided:

1. Parallel processing of a dataset, supporting continued operation after interruption.
2. Process multiple data simultaneously in the code.
3. Process a single data item in the code.

### 1. Parallel Processing of Dataset

The input and output of the data are in jsonl format.

Example of input file `input.jsonl` format:

```json lines
{"index": "0", "instruction": "Translate this sentence into English", "input": "今天天气真好"}
{"index": "1", "instruction": "Write a sentence", "input": ""}
{"index": "2", "instruction": "Translate this sentence into English", "input": "你多大了"}
{"index": "3", "instruction": "Write a joke", "input": ""}
```

Example of output file `output.jsonl` format:

```json lines
{"0": "The weather is really nice today."}
{"1": "I'm trying my best to think about how to answer your question."}
{"2": "How old are you?"}
{"3": "Why does Xiao Ming always laugh behind the tree?\n\nBecause he is a wooden man!"}
```
Please note, if there are problems, such as the context being too long or network issues, the data will be marked in the following format, and running it again will attempt to process this data again.
```json lines
{"4":null}
```
Merge files

You can merge `input.jsonl` and `output.jsonl` into a single json file for easy LLM training.
```json
[
    {
        "index": "0",
        "instruction": "Translate this sentence into English",
        "input": "今天天气真好",
        "output": "The weather is really nice today."
    },
    {
        "index": "1",
        "instruction": "Write a sentence",
        "input": "",
        "output": "Please give me a cup of coffee."
    },
    {
        "index": "2",
        "instruction": "Translate this sentence into English",
        "input": "你多大了",
        "output": "How old are you?"
    },
    {
        "index": "3",
        "instruction": "Write a joke",
        "input": "",
        "output": "Why does Xiao Ming feel pain every time he laughs?\n\nBecause he always laughs his belly sore!"
    }
]
```
Usage:
```python
from openai_parallel_toolkit import ParallelToolkit

if __name__ == '__main__':
    tool = ParallelToolkit(config_path="config.json",
                           input_path="data.jsonl",
                           output_path="output.jsonl")
    tool.merge("merged.json")
```
Python code for processing the dataset:

```python
from openai_parallel_toolkit import ParallelToolkit

if __name__ == '__main__':
    tool = ParallelToolkit(config_path="config.json",
                           input_path="data.jsonl",
                           output_path="output.jsonl")
    tool.run()
    # If you want to merge files, you can call this after processing
    tool.merge("merged.json")
```

`ParallelToolkit` parameters:

- `config_path`: Configuration file path.
- `input_path`: Input file path.
- `output_path`: Output file path.
- `max_retries`: Maximum number of retries, default is 5.
- `threads`: Number of threads, default is 20, the final number of threads will take the smaller of half the number of keys and the number of datasets.
- `name`: Progress bar name, default is "ParallelToolkit Progress".
- `openai_model`: Default is gpt-3.5-turbo-0613, note that $5 accounts cannot use gpt-4.

### 2. Process Multiple Data Simultaneously in Code

Construct a `Dict` using the `Prompt` named tuple, and pass it into the `parallel_api` method.

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt

if __name__ == '__main__':
    data = {i: Prompt(instruction="Please write a sentence about the following topic: ", input="china") for i in
            range(10)}
    ans = ParallelToolkit(config_path="config.json").parallel_api(data=data)
    print(ans)
```

### 3. Process a Single Data in Code

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt

if __name__ == '__main__':
    prompt = Prompt(instruction="Please write a sentence about the following topic: ", input="flowers")
    ans = ParallelToolkit(config_path="config.json").api(prompt=prompt)
    print(ans)
```

## `config.json`

The `config.json` file contains your [OpenAI API Key ↗](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key) and `api_base`.

You can create the `config.json` file in the following way:

```json
{
  "api_keys": [
    "your_api_key1",
    "your_api_key2",
    "your_api_key3"
  ],
  "api_base": "your_api_base"
}
```

In this JSON, `api_keys` is an array containing your OpenAI API keys. Please replace `"your_api_key1"`, `"your_api_key2"`, `"your_api_key3"` with your actual API keys. If you only have one API key, then the array only needs to contain one element.

`"api_base"` is the base URL you use to send API requests. For OpenAI, it should be set to `"https://api.openai.com/v1"`.

Please note that your API key is very important and should be kept safe to prevent leakage to others. You can view OpenAI's [API Key Safety Best Practices ↗](https://help.openai.com/en/articles/4936850-where

## Custom Models and Passing Model Parameters

If you want to customize the model and parameters used, you can pass them in when initializing `ParallelToolkit`.

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt, OpenAIModel

if __name__ == '__main__':
    prompt = Prompt(instruction="Please write a sentence about the following topic: ", input="flowers")
    model = OpenAIModel("gpt-3.5-turbo", temperature=0.1)
    ans = ParallelToolkit(config_path="config.json", openai_model=model).api(prompt=prompt)
    print(ans)
```

## Proxy for Accessing OpenAI Services in China

If you find that the progress bar does not display any progress when running the program, it may be due to network connection issues, especially in areas where accessing OpenAI services is difficult, such as China.

To solve this problem, you can deploy your own proxy service and specify the URL of the proxy service in `api_base`. You can refer to the [OpenAI Proxy ↗](https://github.com/justjavac/openai-proxy) project for more information.

This project explains how to use Cloudflare as a proxy, offering up to 100,000 API requests per day for free. This can effectively solve network connection problems and ensure the smooth running of your program.

Remember, you need to replace the above link with your actual URL.

If you don't need to specify `api_base`, you can leave it blank in the `config.json` file.