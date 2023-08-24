import json
import os
from typing import Dict

from openai_parallel_toolkit.api.model import Prompt


def read_config(config_path: str) -> (str, str):
    with open(config_path, "r") as f:
        config = json.load(f)
        api_keys = config["api_keys"]
        api_base = "https://api.openai.com/v1"
        if "api_base" in config:
            api_base = config["api_base"]
    return api_keys, api_base


def read_jsonl_to_dict(jsonl_file: str) -> Dict[int, Prompt]:
    new_dict = {}
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            index = obj["index"]
            new_dict[index] = Prompt(instruction=obj["instruction"], input=obj["input"])
    return new_dict


def filter(data: dict, path) -> dict:
    data_copy = data.copy()

    if not os.path.exists(path):
        return data_copy

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            key = list(item.keys())[0]
            if key in data_copy:
                del data_copy[key]

    return data_copy


def read_sort_write_jsonl(path: str):
    data = []

    with open(path, "r") as f:
        for line in f:
            item = json.loads(line)
            data.append((int(list(item.keys())[0]), list(item.values())[0]))
    data.sort(key=lambda x: x[0])

    with open(path, "w", encoding="utf-8") as f:
        for key, value in data:
            json.dump({key: value}, f, ensure_ascii=False)
            f.write("\n")


def remove_nulls_from_jsonl(file_path):
    if not os.path.exists(file_path):
        return
    non_null_data = []

    # Read non-null data into a list.
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            if any(value is None for value in data.values()):
                continue
            non_null_data.append(data)

    # Write the non-null data back to the file.
    with open(file_path, "w") as f:
        for data in non_null_data:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


def jsonl_to_dict_special(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = {}
        for line in file:
            json_data = json.loads(line.strip())
            if "index" in json_data.keys():
                data[json_data["index"]] = json_data
            else:
                data.update(json_data)
        return data


def merge_jsonl_files(input_file, output_file, merged_file):
    input = jsonl_to_dict_special(input_file)
    output = jsonl_to_dict_special(output_file)
    # Combine the dictionaries
    merged = []
    for key, value in output.items():
        if key in input:
            temp = input[key].copy()  # Make a copy to prevent changing the original dictionary
            temp.update({"output": value})
            merged.append(temp)  # Directly merge the inner objects

    # Save the result to a new json file
    with open(merged_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=4)


def count_null_values(filename):
    count = 0
    with open(filename, "r") as file:
        for line in file:
            data = json.loads(line)
            count += sum(1 for value in data.values() if value is None)
    return count
