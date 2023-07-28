import json
import os
from typing import Dict

from openai_parallel_toolkit.api.model import Prompt


def read_config(config_path: str) -> (str, str):
    with open(config_path, 'r') as f:
        config = json.load(f)
        api_keys = config['api_keys']
        api_base = "https://api.openai.com/v1"
        if "api_base" in config:
            api_base = config['api_base']
    return api_keys, api_base


def read_jsonl_to_dict(jsonl_file: str) -> Dict[int, Prompt]:
    new_dict = {}
    with open(jsonl_file, 'r') as f:
        for line in f:
            obj = json.loads(line)
            index = obj['index']
            new_dict[index] = Prompt(instruction=obj['instruction'], input=obj['input'])
    return new_dict


def filter(data: dict, path) -> dict:
    data_copy = data.copy()

    if not os.path.exists(path):
        return data_copy

    with open(path, 'r') as f:
        for line in f:
            item = json.loads(line)
            key = int(list(item.keys())[0])
            if key in data_copy:
                del data_copy[key]

    return data_copy


def read_sort_write_jsonl(path: str):
    data = []

    with open(path, 'r') as f:
        for line in f:
            item = json.loads(line)
            data.append((int(list(item.keys())[0]), list(item.values())[0]))
    data.sort()

    with open(path, 'w') as f:
        for key, value in data:
            json.dump({str(key): value}, f, ensure_ascii=False)
            f.write('\n')
