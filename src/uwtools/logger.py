"""
Logger
"""

import sys
from pathlib import Path
from typing import Union, List
import logging


class ColoredFormatter(logging.Formatter):
    """
    Logging colored formatter
    adapted from https://stackoverflow.com/a/56944256/3638629
    """

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.formats = {
            logging.DEBUG: self.blue + self.fmt + self.reset,
            logging.INFO: self.grey + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    """
    Improved logging
    """
    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    DEFAULT_LEVEL = 'INFO'
    DEFAULT_FORMAT = '%(asctime)s - %(levelname)-8s - %(name)-12s: %(message)s'
    def __init__(self, name: str = None,
                 level: str = DEFAULT_LEVEL,
                 _format: str = DEFAULT_FORMAT,
                 colored_log: bool = False,
                 logfile_path: Union[str, Path] = None):
        """
        Constructor for Logger
        """

        self.name = name
        self.level = level.upper()
        self.format = _format
        self.colored_log = colored_log

        if self.level not in Logger.LOG_LEVELS:
            raise LookupError('{self.level} is unknown logging level\n' +
                              'Currently supported log levels are:\n' +
                              f'{" | ".join(Logger.LOG_LEVELS)}')

        # Initialize the root logger if no name is present
        self._logger = logging.getLogger(name) if name else logging.getLogger()

        self._logger.setLevel(self.level)

        _handlers = []
        # Add console handler for logger
        _handler = Logger.add_stream_handler(level=self.level, _format=self.format, colored_log=self.colored_log)
        _handlers.append(_handler)
        self._logger.addHandler(_handler)

        # Add file handler for logger
        if logfile_path is not None:
            _handler = Logger.add_file_handler(logfile_path, level=self.level, _format=self.format)
            self._logger.addHandler(_handler)
            _handlers.append(_handler)

    def __getattr__(self, attribute):
        """
        Allows calling logging module methods directly
        """
        return getattr(self._logger, attribute)

    def get_logger(self):
        '''
        Return the logging object
        '''
        return self._logger

    @classmethod
    def add_handlers(cls, logger: logging.Logger, handlers: List[logging.Handler]):
        """
        Add a list of handlers to a logger
        Parameters
        ----------
        logger
        handlers

        Returns
        -------
        logger
        """
        for h_h in handlers:
            logger.addHandler(h_h)

        return logger

    @classmethod
    def add_stream_handler(cls, level: str = DEFAULT_LEVEL,
                            _format: str = DEFAULT_FORMAT,
                            colored_log: bool = False):
        """
        Create stream handler
        This classmethod will allow setting a custom stream handler on children
        """

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        _format = ColoredFormatter(_format) if colored_log else logging.Formatter(_format)
        handler.setFormatter(_format)

        return handler

    @classmethod
    def add_file_handler(cls, logfile_path: Union[str, Path],
                         level: str = DEFAULT_LEVEL,
                         _format: str = DEFAULT_FORMAT):
        """
        Create file handler.
        This classmethod will allow setting custom file handler on children
        """

        logfile_path = Path(logfile_path)

        # Create the directory containing the logfile_path
        if not logfile_path.parent.is_dir():
            logfile_path.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(str(logfile_path))
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(_format))

        return handler
    