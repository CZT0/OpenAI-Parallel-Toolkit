# OpenAI Parallel Toolkit

**English** | [中文](README_CN.md)

This project uses the key of the OpenAI $5 account. By purchasing a large number of $5 keys and combining key management
with multithreaded parallel processing of large amounts of data, it bypasses the restriction of the $5 account that can
only request 3 times per minute.

The speed of parallel processing is the number of keys/20, that is, the speed of 20 keys is 1 it/s, the speed of 40 keys
is 2 it/s, and so on.
Note that each account can only make 200 requests per day.

## Features

1. ✅ When the usage reaches the limit, it can automatically rotate the OpenAI API key, with built-in error handling and
   automatic retry mechanism.
2. ✅ Provides a solution for proxy access to OpenAI services in China.
3. ✅ Supports parallel processing of API and file operations, optimizes throughput and efficiency, and supports
   resumable transmission.

## Installation

```bash
pip install openai-parallel-toolkit
```

## Usage

Currently provide three usage methods:

1. Parallel processing of a dataset, support for continuing to run after interruption.
2. Process multiple data simultaneously in the code.
3. Process a single data in the code.

### 1. Dataset parallel processing

The input and output of data are all in jsonl format.

Input file `input.jsonl` format example:

```json lines
{
  "index": 0,
  "instruction": "Translate this sentence into English",
  "input": "Today the weather is really good"
}
{
  "index": 1,
  "instruction": "Write a sentence",
  "input": ""
}
{
  "index": 2,
  "instruction": "Translate this sentence into English",
  "input": "How old are you"
}
{
  "index": 3,
  "instruction": "Write a joke",
  "input": ""
}
```

Output file `output.jsonl` format example:

```json lines
{
  "0": "The weather is really nice today."
}
{
  "1": "I am trying hard to think about how to answer your question."
}
{
  "2": "How old are you?"
}
{
  "3": "Why pull the cow to the church? \n\n Because it is a “pastor”!"
}
```

Python code for processing datasets:

```python
from openai

-parallel - toolkit
import ParallelToolkit

if __name__ == '__main__':
    ParallelToolkit(config_path="config.json",
                    input_path="input.jsonl",
                    output_path="output.jsonl").run()
```

`ParallelToolkit` parameters:

- `config_path`: Configuration file path.
- `input_path`: Input file path.
- `output_path`: Output file path.
- `max_retries`: Maximum number of retries, default is 5.
- `threads`: Number of threads, default is 20, the final number of threads will take the minimum value of half the
  number of keys and the number of datasets.
- `name`: Progress bar name, default is "ParallelToolkit Progress".
- `openai_model`: Default is gpt-3.5-turbo-0613, note that the $5 account cannot use gpt-4.

### 2. Process multiple data simultaneously in the code

Use the `Prompt` named tuple to construct a `Dict` and then pass it into the `parallel_api` method.

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt

if __name__ == '__main__':
    data = {i: Prompt(instruction="Please write a sentence about the following topic: ", input="china") for i in
            range(10)}
    ans = ParallelToolkit(config_path="config.json").parallel_api(data=data)
    print(ans)
```

### 3. Process a single data in the code

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt

if __name__ == '__main__':
    prompt = Prompt(instruction="Please write a sentence about the following topic: ", input="flowers")
    ans = ParallelToolkit(config_path="config.json").api(prompt=prompt)
    print(ans)
```

## `config.json`

The `config.json` file contains
the [OpenAI API key ↗](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key) and `api_base`.

You can create the `config.json` file as follows:

```json
{
  "api_keys": [
    "Your api key 1",
    "Your api key 2",
    "Your api key 3"
  ],
  "api_base": "Your api_base"
}
```

In this JSON, `api_keys` is an array that contains your OpenAI API keys. Please
replace `"Your api key 1"`, `"Your api key 2"`, `"Your api key 3"` with your actual API keys. If you only have one API
key, then this array only needs to contain one element.

`"api_base"` is the basic URL you use to# OpenAI Parallel Toolkit

## China Access to OpenAI Service Agent
If you're running the program and the progress bar isn't showing any progress, it's possible that you're experiencing
connectivity issues, particularly if you're in China or another region where accessing OpenAI is challenging.

To resolve this issue, we recommend deploying your own proxy and passing in `api_base`. You can refer to
the [OpenAI Proxy](https://github.com/justjavac/openai-proxy) project for more details.

This project provides a method that uses Cloudflare's proxy, which allows up to 100,000 free calls per day. This can
effectively help bypass the connectivity issue and ensure the smooth running of your program.

Remember to replace the project link with the actual URL for your specific situation.

If you don't need the api base field, you can leave it unwritten to the config.json file.
