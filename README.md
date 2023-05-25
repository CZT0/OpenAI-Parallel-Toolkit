# OpenAI Parallel Toolkit

The OpenAI Parallel Toolkit is a specialized Python library crafted to proficiently manage multiple OpenAI API keys and
effectively supervise parallel tasks. It comes packed with features that cater to API key rotation, accelerating task
execution through multithreading, and provides an assortment of utility functions to optimize your OpenAI integration.
This toolkit serves as an efficient solution for extensive, high-performance OpenAI usage.

### Function

1. &#x2705; Enables automated OpenAI API key rotation when usage limit is reached, with built-in error handling and
   auto-retry mechanisms.
2. &#x2705; Provides a method for proxy access to OpenAI services in China.
3. &#x2705; Supports parallel processing for both API and file operations, optimizing throughput and efficiency.
4. &#x2705; Features a file processing resumption function, effectively skipping previously processed files.
5. &#x2705; Includes a utility to split long text into specified length segments, following the token count method used
   in GPT-3.5 model.

## Context

In the field of natural language processing (NLP), Generative Pretrained Transformer (GPT) models have revolutionized
the methodology of processing and comprehending textual data. They've equipped us with the ability to accomplish a vast
array of tasks such as data annotation, processing, and generating text with a human-like semblance. However, employing
GPT models for large-scale or time-critical tasks can often present unique hurdles.

A primary concern is the execution speed of tasks. Owing to the intricate and data-intensive nature of GPT models,
processing time can be substantial, particularly when confronted with significant data quantities. This can
substantially impede the efficiency of projects that require rapid completion.

The utilization of API keys presents another challenge. Each key has a defined limit, beyond which it is incapable of
handling more requests. In scenarios involving high data volumes, this limit can swiftly be reached, thereby
necessitating a manual transition to another key. This challenge intensifies when handling multiple keys across diverse
projects.

In an attempt to address these challenges and optimize the process, we developed a comprehensive solution: the OpenAI
Parallel Toolkit. This advanced framework is designed to efficiently manage multiple OpenAI API keys and effectively
supervise parallel tasks. The toolkit incorporates a range of features, including API key rotation, multithreading for
expedited task execution, file processing with resume capability, and an array of utility functions to enhance OpenAI
integration.

The OpenAI Parallel Toolkit's primary goal is to enable users to focus on the task's core aspects, eliminating the need
to continuously navigate peripheral challenges. It offers a streamlined and efficient solution for large-scale OpenAI
usage, empowering you to concentrate on your data processing needs.

## Installation

```bash
pip install openai-parallel-toolkit
```

## Usage

You are expected to override the `process_input`, `process_output`, and `process_data` methods of the `ParallelToolkit`
class. You only need to consider the processing workflow for a single file.

Specifically, the `process_input` method should handle how the file is read, the `process_data` method should handle the
processing of data within the file (you can call OpenAI API within this function), and the `process_output` method
should handle how the processed data is written back to a file.

Once these methods are implemented, the `run` method can be invoked. Here's an example of a `ParallelToolkit` subclass
that demonstrates the implementation of these methods:

```python
import json
from openai_parallel_toolkit import ParallelToolkit, Gpt35Turbo, request_openai_api


class MyParallelToolkit(ParallelToolkit):

    @staticmethod
    def process_input(file):
        # Read the file, the returned data will be the input for process_data
        return json.load(file)

    @staticmethod
    def process_data(data):
        # Call OpenAI API here, several call methods are provided for reference
        # For example, to use GPT-3.5, you can make the call as follows:
        model = Gpt35Turbo(content="hello world", prompt="", temperature=0.7)
        result = request_openai_api(model)
        return result

    @staticmethod
    def process_output(data, output_file_without_ext):
        # Process the result returned by process_data and write the result to a file
        output_file = output_file_without_ext + ".json"
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump({"result": data}, file, ensure_ascii=False)
```

Afterwards, you can invoke it as follows:

```python
MyParallelToolkit(
    config_path="/path/to/config.json",
    input_path="/path/to/input/folder",
    output_path="/path/to/output/folder").run()
```

Support for resuming file output means that if the output file already exists, the processing for that file will be
skipped. You can run the program multiple times until all files have been processed. Usually, a single run should be
sufficient to process all the files.
The parameters are explained below:

- `config_path (str)`: Path to the configuration file.
    - Example: `"/path/to/config.json"`
- `input_path (str)`: Path to the input file or directory.
    - Example: `"/path/to/input/"`
- `output_path (str)`: Path to the output file or directory.
    - Example: `"/path/to/output/"`
- `file_count (int, optional)`: Number of files to process.
    - Defaults to None, which means process all files.
- `num_threads (int, optional)`: Number of worker threads.
    - Defaults to 10 times the number of CPUs.
- `name (str, optional)`: Name to display for the progress.
    - Defaults to "ParallelToolkit Progress".

## config.json

The `config.json` file contains OpenAI API keys and the `api_base`.

You can create a `config.json` file as follows:

```json
{
  "api_keys": [
    "your api key 1",
    "your api key 2",
    "your api key 3"
  ],
  "api_base": "https://api.openai.com/v1"
}
```

### Troubleshooting: Progress Bar Not Moving

If you're running the program and the progress bar isn't showing any progress, it's possible that you're experiencing
connectivity issues, particularly if you're in China or another region where accessing OpenAI is challenging.

To resolve this issue, we recommend deploying your own proxy and passing in `api_base`. You can refer to
the [OpenAI Proxy](https://github.com/justjavac/openai-proxy) project for more details.

This project provides a method that uses Cloudflare's proxy, which allows up to 100,000 free calls per day. This can
effectively help bypass the connectivity issue and ensure the smooth running of your program.

Remember to replace the project link with the actual URL for your specific situation.

If you don't need the api base field, you can leave it unwritten to the config.json file.

## Parallel processing of one file

If you have a single file that is too long, you can split it into smaller segments, process them in parallel, and then
merge the results in order. You can use the `multi_process_one` function for this purpose. Here's an example of how to
use it in the `process_data` function:

Here's how you can add this information into your markdown documentation:

---

## Usage: Processing Data

In the Python function `multi_process_one`, `data` is a list of tuples. Here's an example:

```python
from openai_parallel_toolkit import multi_process_one, Gpt35Turbo


@staticmethod
def process_data(data):
    # data example: 
    # [('hello1', 'world'), ('hello2', 'world'), ('hello3', 'world'), 
    #  ('hello4', 'world'), ('hello5', 'world')]
    results = multi_process_one(data=data, openai_model_class=Gpt35Turbo, temperature=0.7)
    return results
```

It's important to note that in the `data` list, you need to pass the prompt as the first element and the content as the
second element of each tuple. This is necessary to ensure the correctness of the results.

Any remaining parameters should be passed in the order defined by the `Gpt35Turbo` (or your custom model) after the
prompt and content parameters.

If you're unsure about the parameters, you can refer to the source code of the `multi_process_one` function for
additional clarity.

## Customizing OpenAI API Interface

Currently, the OpenAI API interfaces supported are:

- GPT-3.5

This is a low-cost interface suitable for most data processing scenarios. If you want to use other models, you can
implement the abstract class `OpenAIModel`. For example, you can implement other interfaces similar to the `Gpt35Turbo`
class.

```python
from openai_parallel_toolkit import OpenAIModel
import openai


class Gpt35Turbo(OpenAIModel):

    def __init__(self, content, prompt, temperature):
        self.content = content
        self.prompt = prompt
        self.temperature = temperature

    def generate(self):
        # Create a chat completion with OpenAI
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": self.content}
            ],
            temperature=self.temperature
        )
        return completion
```

## Simple use OpenAI API request Only

If you just want to simply call the api. You can use the API key rotation with just two lines of code:

```python
from openai_parallel_toolkit import Gpt35Turbo, request_openai_api

model = Gpt35Turbo(content="hello world", prompt="", temperature=0.7)
result = request_openai_api(openai_model=model, config_path="config.json")
```

`multi_process_one` provides multi-thread processing for an array of data. It internally wraps
the `request_openai_api` function. If you want to use `multi_process_one` independently, you can do so as follows:

```python
from openai_parallel_toolkit import multi_process_one, Gpt35Turbo, APIKeyManager


def test_multi_process_one():
    data = [('hello1', 'world'), ('hello2', 'world'), ('hello3', 'world'), ('hello4', 'world'), ('hello5', 'world')]
    APIKeyManager(config_path="config.json", set_api_base=True)
    results = multi_process_one(data=data, openai_model_class=Gpt35Turbo, temperature=0.7)
    print(results)
```

This allows the API key manager to automatically rotate API keys once the per-minute limit is reached, which is
beneficial for streamlining the management of multiple keys and ensuring uninterrupted service.

`request_openai_api` and `multi_process_one` also provides handling of OpenAI request errors, including automatic retry,
removal of keys that reach the quota, and so on.

## Additional Utility Classes

### Token Count Calculation

The `num_tokens_from_string` function is provided to calculate the number of tokens in a string, using the default
behavior of GPT-3.5. It can be used as follows:

```python
from openai_parallel_toolkit import num_tokens_from_string

print(num_tokens_from_string("hello world"))
```

### Splitting Text by Token Length

The `split_string_by_tokens` function allows you to split a long text into segments of a specified token length and
store them in a list. It can be used as follows:

```python
from openai_parallel_toolkit import split_string_by_tokens

results = split_string_by_tokens(string="hello world", thunk_len=2, split_signal="。")
```

The parameters for `split_string_by_tokens` are as follows:

- `string (str)`: The text to be segmented.
- `thunk_len (int)`: The length of each segment in tokens.
- `split_signal (str)`: The delimiter used for splitting.
  It's important to note that if a sentence within a segment is too long, the segment may exceed the specified length.
  This function does not truncate the text, but only splits it when encountering the split signal.

## Contributing

We truly appreciate and value contributions from the community, as they play a significant role in enhancing the
OpenAI-Parallel-Toolkit. Whether it's by reporting bugs, proposing new features, or directly contributing code, you can
help us improve this project. Here are a few guidelines on how you can contribute:

1. **Reporting Bugs**: If you encounter any bugs or issues, please open an issue in the GitHub repository detailing the
   problem you faced. Include as much information as possible, such as the steps to reproduce the bug, the Python
   version you're using, etc.

2. **Proposing New Features**: Do you have an idea for a new feature that could improve this toolkit? Don't hesitate to
   share it! Please open an issue in the GitHub repository describing the feature, its potential benefits, and how it
   could be implemented.

3. **Contributing Code**: We welcome pull requests. If you want to contribute code, please fork the repository, make
   your changes, and submit a pull request. Try to keep your changes concise and ensure that the code is properly
   formatted and documented.

4. **Improving Documentation**: Good documentation is just as important as good code. If you notice that something is
   unclear, incorrect, or missing from the documentation, please update it and submit a pull request.

Before you contribute, please review the existing issues in the GitHub repository to see if someone else has already
reported the same issue or proposed the same feature.

Remember, the best way to ensure that your ideas and suggestions are implemented is by making a contribution yourself.
Together, we can make the OpenAI-Parallel-Toolkit even better.

Thank you for your interest in contributing to the OpenAI-Parallel-Toolkit!