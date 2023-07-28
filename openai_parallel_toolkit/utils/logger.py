import logging

from colorlog import ColoredFormatter

LOG_LABEL = "MYLOG"
LOG_COLORS = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}


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


class Logger:
    def __init__(self, label=LOG_LABEL, level=logging.WARNING, datefmt=None):
        self.label = label
        self.level = level
        self.datefmt = datefmt
        self.logger = self.create_logger()
        self.handler = self.create_handler()
        self.formatter = self.create_formatter()

        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def create_logger(self):
        logger = logging.getLogger()
        logger.setLevel(self.level)
        return logger

    def create_handler(self):
        handler = logging.StreamHandler()
        handler.addFilter(LogFilter(self.label))
        return handler

    def create_formatter(self):
        formatter = ColoredFormatter(
                "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
                datefmt=self.datefmt,
                reset=True,
                log_colors=LOG_COLORS
        )
        return formatter
