# OpenAI Parallel Toolkit

**English** | [中文](README.md)

This project utilizes the keys of OpenAI's $5 accounts by purchasing a large number of $5 keys and combining key management with multithreading to process large amounts of data in parallel, bypassing the limitation of only 3 requests per minute for each $5 account.

The processing speed scales with the number of keys, with 20 keys achieving a speed of 1 it/s, 40 keys achieving 2 it/s, and so forth. Note that each account is limited to 200 requests per day.

The default model used is `gpt-3.5-turbo-0613`. If your context is too long, after running once, you can use [custom models](#custom-models-and-passing-model-parameters) and specify `gpt-3.5-turbo-16k-0613` to reprocess data that couldn't be handled initially.

## Simplified Framework
If you are looking for a simpler key management framework, check out my other open-source project [StableOpenAI](https://github.com/CZT0/StableOpenAI). This project uses an exponential backoff algorithm and read-write locks to implement thread-safe Key management efficiently and succinctly.

## Features

1. ✅ Automatically rotates OpenAI API keys when usage limits are reached, with built-in error handling and automatic retry mechanisms.
2. ✅ Provides a solution for accessing OpenAI services via proxy in China.
3. ✅ Supports parallel processing of API and file operations, optimizing throughput and efficiency, with support for resuming from breakpoints.

## Installation

```bash
pip install openai-parallel-toolkit
```

## Usage

There are currently three ways to use this:

1. Process a dataset in parallel, supporting resumption after interruption.
2. Handle multiple data points simultaneously in code.
3. Handle a single data point in code.

### 1. Processing a Dataset

#### Dataset Format

Both input and output data use the jsonl format.

Input file `input.jsonl` example, note that the index is a string:

```json lines
{"index": "0", "instruction": "Translate this sentence into English", "input": "今天天气真好"}
{"index": "1", "instruction": "Write a sentence", "input": ""}
{"index": "2", "instruction": "Translate this sentence into English", "input": "你多大了"}
{"index": "3", "instruction": "Write a joke", "input": ""}
```

Output file `output.jsonl` example:

```json lines
{"0": "The weather is really nice today."}
{"1": "I am trying my best to think of how to answer your question."}
{"2": "How old are you?"}
{"3": "Why does Xiaoming always laugh behind the tree?\n\nBecause he's a wooden man!"}
```
Note, if there are issues, like overly long context or network problems, the data will be marked in the following format, and reprocessing will be attempted upon rerunning.
```json lines
{"4":null}
```
Merging Files

You can merge `input.jsonl` with `output.jsonl` into a single JSON file, which is convenient for LLM training.
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
        "output": "Why does Xiaoming always feel pain when he laughs?\n\nBecause his laughter always hurts his stomach!"
    }
]
```
Invocation method:
```python
from openai_parallel_toolkit import ParallelToolkit

if __name__ == '__main__':
    tool = ParallelToolkit(config_path="config.json",
                           input_path="data.jsonl",
                           output_path="output.jsonl")
    tool.merge("merged.json")
```
#### Processing the Dataset:

```python
from openai_parallel_toolkit import ParallelToolkit

if __name__ == '__main__':
    tool = ParallelToolkit(config_path="config.json",
                           input_path="data.jsonl",
                           output_path="output.jsonl")
    tool.run()
    # If you want to merge files, you can call

 this after processing
    # tool.merge("merged.json")
```

`ParallelToolkit` Parameters:

- `config_path`: Configuration file path.
- `input_path`: Input file path.
- `output_path`: Output file path.
- `max_retries`: Maximum number of retries, default is 5.
- `threads`: Number of threads, default is 20. The final number of threads will be the minimum of half the number of keys and the dataset size.
- `name`: Progress bar name, default is "ParallelToolkit Progress".
- `openai_model`: Default is gpt-3.5-turbo-0613. Note that the $5 account cannot use gpt-4.

### 2. Handling Multiple Data Points Simultaneously

Construct a `Dict` using the `Prompt` namedtuple, then pass it to the `parallel_api` method.

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt

if __name__ == '__main__':
    data = {i: Prompt(instruction="Please write a sentence about the following topic: ", input="china") for i in
            range(10)}
    ans = ParallelToolkit(config_path="config.json").parallel_api(data=data)
    print(ans)
```

### 3. Handling a Single Data Point

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt

if __name__ == '__main__':
    prompt = Prompt(instruction="Please write a sentence about the following topic: ", input="flowers")
    ans = ParallelToolkit(config_path="config.json").api(prompt=prompt)
    print(ans)
```

## `config.json`

The `config.json` file contains your [OpenAI API Keys ↗](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key) and `api_base`.

You can create a `config.json` file as follows:

```json
{
  "api_keys": [
    "your api key 1",
    "your api key 2",
    "your api key 3"
  ],
  "api_base": "your api_base"
}
```

In this JSON, `api_keys` is an array containing your OpenAI API keys. Replace `"your api key 1"`, `"your api key 2"`, `"your api key 3"` with your actual API keys. If you have only one API key, then this array should contain only one element.

`"api_base"` is the base URL you use for sending API requests. For OpenAI, it should be set to `"https://api.openai.com/v1"`.

Please note that your API key is very important and should be kept secure to prevent it from being disclosed to others. You can read more about [API Key Safety Best Practices ↗](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key) provided by OpenAI.

## Custom Models and Passing Model Parameters

If you want to customize the model and parameters used, you can pass them during the initialization of `ParallelToolkit`.

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt, OpenAIModel

if __name__ == '__main__':
    prompt = Prompt(instruction="Please write a sentence about the following topic: ", input="flowers")
    model = OpenAIModel("gpt-3.5-turbo", temperature=0.1)
    ans = ParallelToolkit(config_path="config.json", openai_model=model).api(prompt=prompt)
    print(ans)
```

## Proxy for Accessing OpenAI Services in China

If you find that the progress bar does not show any progress when running the program, it may be due to network connection issues, especially in China or other regions where accessing OpenAI services is difficult.

To resolve this issue, you can deploy your own proxy service and specify the URL of the proxy service in `api_base`. You can refer to the [OpenAI Proxy ↗](https://github.com/justjavac/openai-proxy) project for more information.

This project describes how to use Cloudflare as a proxy, providing up to 100,000 API requests/day for free. This can effectively solve network connection problems and ensure your program runs smoothly.

Remember to replace the above link with your actual URL.

If you do not need to specify `api_base`, you can leave it empty in the `config.json` file.
