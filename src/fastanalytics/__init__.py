import logging

from .__version__ import __version__

_LOGGER_NAME = "fast-analytics"

__all__ = ["__version__", "get_logger"]


def get_logger() -> logging.Logger:
    return logging.getLogger(_LOGGER_NAME)
