import multiprocessing  # For accessing the number of CPUs
from abc import ABC, abstractmethod  # For defining abstract base classes

from .multithread import multi_thread_run  # Importing the local function for multithreaded execution


class ParallelToolkit(ABC):
    """
    Abstract base class for parallel processing tools.
    This class provides a template for tools that process files in parallel.

    Subclasses should implement the process_input, process_data, and process_output methods.
    """

    def __init__(self,
                 config_path: str,
                 input_path: str,
                 output_path: str,
                 file_count: int = None,
                 num_threads=multiprocessing.cpu_count() * 10,
                 name="ParallelToolkit Progress"):
        """
        Initializes the ParallelToolkit object.

        Args:
            config_path (str): Path to the configuration file.
                Example: "/path/to/config.json"

            input_path (str): Path to the input file or directory.
                Example: "/path/to/input/"

            output_path (str): Path to the output file or directory.
                Example: "/path/to/output/"

            file_count (int, optional): Number of files to process.
                Defaults to None, which means process all files.
                Example: 10

            num_threads (int, optional): Number of worker threads.
                Defaults to 10 times the number of CPUs.
                Example: 4

            name (str, optional): Name to display for the progress.
                Defaults to "ParallelToolkit Progress".
                Example: "Processing Progress"
        """
        self.input_path = input_path
        self.output_path = output_path
        self.max_workers = num_threads
        self.name = name
        self.file_count = file_count
        self.config_path = config_path

    @staticmethod
    @abstractmethod
    def process_input(file):
        """
        Abstract method to process an input file.
        This method should read the file and return the file content.
        Must be implemented in a subclass.

        Args:
            file (TextIO): Read byte stream object

        Returns:
            Any: The content of the file.

        Example:
            @staticmethod
            def process_input(file):
                data = json.load(file)
                return data
        """
        pass

    @staticmethod
    @abstractmethod
    def process_data(data):
        """
        Abstract method to process data.
        This method should process the data (e.g., by calling a model) and return the result.
        Must be implemented in a subclass.

        Args:
            data (Any): The content returned by the process_input method.

        Returns:
            Any: The result of the processing.

        Example:
            result = model.predict(data)
            return result
        """
        pass

    @staticmethod
    @abstractmethod
    def process_output(data, output_file_without_ext: str):
        """
        Abstract method to process output data.
        This method should write the processed data to the output file.
        Must be implemented in a subclass.

        Args:
            data (Any): The content returned by the process_data method.
            output_file_without_ext (str): The output file path without the extension.

        Example:
            @staticmethod
            def process_output(data, output_file_without_ext):
                output_file = output_file_without_ext+".json"
                with open(output_file, 'w', encoding='utf-8') as file:
                    json.dump({"result": data}, file, ensure_ascii=False)
        """
        pass

    def run(self):
        """
        Runs the processing in multiple threads.
        This method calls the multi_thread_run function with the initialized parameters and the implemented methods.

        Example:
            toolkit = SubclassOfParallelToolkit("/path/to/config", "/path/to/input", "/path/to/output")
            toolkit.run()
        """
        multi_thread_run(
            config_path=self.config_path,
            input_path=self.input_path,
            output_path=self.output_path,
            file_count=self.file_count,
            process_input=self.process_input,
            process_output=self.process_output,
            process_data=self.process_data,
            num_threads=self.max_workers,
            name=self.name
        )
