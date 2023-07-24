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


# 创建一个全局变量用于保存logger
_global_logger = None


def logger_init(label=LOG_LABEL, level=logging.INFO, datefmt=None):
    global _global_logger

    # 检查全局变量是否已经被初始化
    if _global_logger is not None:
        return _global_logger

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

    # 将新创建的logger保存在全局变量中，以便后续使用
    _global_logger = logger

    return logger
