import tiktoken


def num_tokens_from_string(string: str, encoding_name: str = "gpt-3.5-turbo") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def split_string_by_tokens(string: str, thunk_len: int, split_signal) -> list:
    sentences = string.split(split_signal)
    result = []
    current_sentence = ""
    for sentence in sentences:
        sentence = sentence.strip() + split_signal
        sentence_tokens = num_tokens_from_string(current_sentence + sentence)
        if sentence_tokens > thunk_len:
            if current_sentence:
                result.append(current_sentence)
            current_sentence = sentence
        else:
            current_sentence += sentence

    if current_sentence:
        result.append(current_sentence)
    return result
