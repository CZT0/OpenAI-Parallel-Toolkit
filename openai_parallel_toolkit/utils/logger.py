import logging

from colorlog import ColoredFormatter

from openai_parallel_toolkit.config import LOG_LABEL


class LogFilter(logging.Filter):
    def __init__(self, label):
        super().__init__()
        self.label = label

    def filter(self, record):
        if self.label in record.getMessage():
            record.msg = record.msg.replace(self.label, '')
            return True
        else:
            return False


def logger_init(label=LOG_LABEL, level=logging.INFO, datefmt=None):
    logger = logging.getLogger()
    logger.setLevel(level)
    handler = logging.StreamHandler()

    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red',
    }

    handler.addFilter(LogFilter(label))

    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt=datefmt,
        reset=True,
        log_colors=log_colors
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
