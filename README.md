# OpenAI 并行工具箱

**中文** | [English](README_EN.md)

这个项目利用 OpenAI 5美元账户的密钥，通过购买大量5美元密钥并结合密钥管理与多线程并行处理大量数据，绕过了5美元账户每分钟只能请求3次的限制。

并行处理的速度为 key的数目/20，即20个key的速度为1 it/s，40个key的速度为2 it/s，以此类推。注意每个账号每天只能请求200次。

默认模型使用的是`gpt-3.5-turbo-0613`，如果你的上下文过长，可以在运行完成一遍后使用[自定义模型](#自定义模型与传递模型参数)，指定`gpt-3.5-turbo-16k-0613`再次运行，会将无法处理的数据继续处理。

## 功能

1. ✅ 在使用量达到限制时，自动轮换 OpenAI API 密钥，内置错误处理和自动重试机制。
2. ✅ 提供在中国代理访问 OpenAI 服务的解决方案。
3. ✅ 支持 API 和文件操作的并行处理，优化吞吐量和效率，支持断点续传。

## 安装

```bash
pip install openai-parallel-toolkit
```

## 使用方法

目前提供三种使用方法：

1. 对一个数据集进行并行处理，支持中断后继续运行。
2. 在代码中同时处理多个数据。
3. 在代码中处理单个数据。

### 1. 处理数据集

#### 数据集格式

数据的输入和输出都采用 jsonl 格式。

输入文件 `input.jsonl` 格式例子，注意index为字符串：

```json lines
{"index": "0", "instruction": "把这句话翻译成英文", "input": "今天天气真好"}
{"index": "1", "instruction": "写一句话", "input": ""}
{"index": "2", "instruction": "把这句话翻译成英文", "input": "你多大了"}
{"index": "3", "instruction": "写一个笑话", "input": ""}
```

输出文件 `output.jsonl` 格式例子：

```json lines
{"0": "The weather is really nice today."}
{"1": "我正在尽力思考如何回答你的问题。"}
{"2": "How old are you?"}
{"3": "为什么小明总是躲在树后笑？\n\n因为他是一个木头人！"}
```
注意，如果遇到问题，比如上下文过长或者网络问题，数据会以下面的格式标记，重新运行会再次尝试处理这些数据。
```json lines
{"4":null}
```
合并文件

可以将input.jsonl与output.jsonl合并成一个json文件，便于进行LLM训练
```json
[
    {
        "index": "0",
        "instruction": "把这句话翻译成英文",
        "input": "今天天气真好",
        "output": "The weather is really nice today."
    },
    {
        "index": "1",
        "instruction": "写一句话",
        "input": "",
        "output": "请给我一杯咖啡。"
    },
    {
        "index": "2",
        "instruction": "把这句话翻译成英文",
        "input": "你多大了",
        "output": "How old are you?"
    },
    {
        "index": "3",
        "instruction": "写一个笑话",
        "input": "",
        "output": "为什么小明每次笑都能感受到疼痛呢？\n\n因为他笑起来总是把肚子笑疼了！"
    }
]
```
调用方式：
```python
from openai_parallel_toolkit import ParallelToolkit

if __name__ == '__main__':
    tool = ParallelToolkit(config_path="config.json",
                           input_path="data.jsonl",
                           output_path="output.jsonl")
    tool.merge("merged.json")
```
#### 处理数据集：

```python
from openai_parallel_toolkit import ParallelToolkit

if __name__ == '__main__':
    tool = ParallelToolkit(config_path="config.json",
                           input_path="data.jsonl",
                           output_path="output.jsonl")
    tool.run()
    # 如果你想要合并文件，可以在处理完成后调用
    # tool.merge("merged.json")
```

`ParallelToolkit` 参数：

- `config_path`: 配置文件路径。
- `input_path`: 输入文件路径。
- `output_path`: 输出文件路径。
- `max_retries`: 最大重试次数，默认为5。
- `threads`: 线程数，默认为20，最后的线程数会取 key 数目的一半和数据集数目的最小值。
- `name`: 进度条名称，默认为"ParallelToolkit Progress"。
- `openai_model`: 默认为 gpt-3.5-turbo-0613，注意 5 美元账号无法使用 gpt-4。

### 2. 同时处理多个数据

使用 `Prompt` 命名元组构造一个 `Dict`，然后传入 `parallel_api` 方法中。

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt

if __name__ == '__main__':
    data = {i: Prompt(instruction="Please write a sentence about the following topic: ", input="china") for i in
            range(10)}
    ans = ParallelToolkit(config_path="config.json").parallel_api(data=data)
    print(ans)
```

### 3. 处理单个数据

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt

if __name__ == '__main__':
    prompt = Prompt(instruction="Please write a sentence about the following topic: ", input="flowers")
    ans = ParallelToolkit(config_path="config.json").api(prompt=prompt)
    print(ans)
```

## `config.json`

`config.json`
文件包含了 [OpenAI API 密钥 ↗](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key)
和 `api_base`。

你可以按照以下方式创建 `config.json` 文件：

```json
{
  "api_keys": [
    "你的api密钥1",
    "你的api密钥2",
    "你的api密钥3"
  ],
  "api_base": "你的api_base"
}
```

在这段 JSON 中，`api_keys` 是一个数组，包含了你的 OpenAI API
密钥。请将 `"你的api密钥1"`, `"你的api密钥2"`, `"你的api密钥3"` 替换为你的实际 API 密钥。如果你只有一个 API
密钥，那么该数组中只需要包含一个元素。

`"api_base"` 是你用来发送 API 请求的基本 URL。对于 OpenAI，它应该设置为 `"https://api.openai.com/v1"`。

请注意，你的 API 密钥非常重要，应当妥善保管，避免泄露给其他人。你可以查看 OpenAI
的 [API Key Safety Best Practices ↗](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key)
获取更多信息。

## 自定义模型与传递模型参数

如果你想自定义使用的模型和参数，可以在 `ParallelToolkit` 初始化时传入。

```python
from openai_parallel_toolkit import ParallelToolkit, Prompt, OpenAIModel

if __name__ == '__main__':
    prompt = Prompt(instruction="Please write a sentence about the following topic: ", input="flowers")
    model = OpenAIModel("gpt-3.5-turbo", temperature=0.1)
    ans = ParallelToolkit(config_path="config.json", openai_model=model).api(prompt=prompt)
    print(ans)
```

## 中国访问 OpenAI 服务代理

如果你在运行程序时发现进度条没有显示任何进度，可能是由于网络连接问题，特别是在中国或其他访问 OpenAI 服务困难的地区。

为了解决这个问题，你可以部署自己的代理服务并在 `api_base` 中指定代理服务的
URL。你可以参考 [OpenAI Proxy ↗](https://github.com/justjavac/openai-proxy) 项目获取更多信息。

该项目介绍了如何使用 Cloudflare 作为代理，免费提供高达 100,000 次/天的 API 请求。这可以有效地解决网络连接问题，并确保你的程序可以顺畅运行。

请记住，需要将上述链接替换为你自己的实际 URL。

如果你不需要指定 `api_base`，可以在 `config.json` 文件中将其留空。
