# Import the necessary libraries
from abc import ABC, abstractmethod

import openai


class OpenAIModel(ABC):
    """Abstract Base Class (ABC) for OpenAI models."""

    @abstractmethod
    def __init__(self, **kwargs):
        """
        Abstract method for initialization.
        Subclasses should implement this method and make use of the parameters in the generate method.
        """
        pass

    @abstractmethod
    def generate(self):
        """
        Abstract method for generating a completion using the OpenAI API.
        Subclasses should implement this method if you want to use other models.
        """
        pass


class Gpt35Turbo(OpenAIModel):
    """
    Gpt35Turbo is a subclass of OpenAIModel, often used for data processing.
    """

    def __init__(self, content, prompt, temperature):
        """
        Initialize a Gpt35Turbo instance.

        Args:
            content (str): User input to be processed by the model.
            prompt (str): System message that guides the conversation.
            temperature (float): Parameter that controls the randomness of the model's output.
        """
        self.content = content
        self.prompt = prompt
        self.temperature = temperature

    def generate(self):
        """
        Generate a completion using the OpenAI API.

        Returns:
            dict: Response from the OpenAI API.
        """
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


class Gpt35Turbo16K(OpenAIModel):
    """
    Gpt35Turbo is a subclass of OpenAIModel, often used for data processing.
    """

    def __init__(self, content, prompt, temperature):
        """
        Initialize a Gpt35Turbo instance.

        Args:
            content (str): User input to be processed by the model.
            prompt (str): System message that guides the conversation.
            temperature (float): Parameter that controls the randomness of the model's output.
        """
        self.content = content
        self.prompt = prompt
        self.temperature = temperature

    def generate(self):
        """
        Generate a completion using the OpenAI API.

        Returns:
            dict: Response from the OpenAI API.
        """
        # Create a chat completion with OpenAI
        completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": self.content}
                ],
                temperature=self.temperature
        )
        return completion


class Gpt35Turbo0613(OpenAIModel):
    """
    Gpt35Turbo0613 is a subclass of OpenAIModel, often used for data processing.
    """

    def __init__(self, content, prompt, temperature):
        """
        Initialize a Gpt35Turbo instance.

        Args:
            content (str): User input to be processed by the model.
            prompt (str): System message that guides the conversation.
            temperature (float): Parameter that controls the randomness of the model's output.
        """
        self.content = content
        self.prompt = prompt
        self.temperature = temperature

    def generate(self):
        """
        Generate a completion using the OpenAI API.

        Returns:
            dict: Response from the OpenAI API.
        """
        # Create a chat completion with OpenAI
        completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": self.content}
                ],
                temperature=self.temperature
        )
        return completion


class Gpt4(OpenAIModel):
    """
    Gpt4 is a subclass of OpenAIModel
    """

    def __init__(self, content, prompt, temperature):
        """
        Initialize a Gpt35Turbo instance.

        Args:
            content (str): User input to be processed by the model.
            prompt (str): System message that guides the conversation.
            temperature (float): Parameter that controls the randomness of the model's output.
        """
        self.content = content
        self.prompt = prompt
        self.temperature = temperature

    def generate(self):
        """
        Generate a completion using the OpenAI API.

        Returns:
            dict: Response from the OpenAI API.
        """
        # Create a chat completion with OpenAI
        completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": self.content}
                ],
                temperature=self.temperature
        )
        return completion
