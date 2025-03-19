# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The logger.
"""


import logging
import sys


def init_logger() -> logging.Logger:
    """Initialize and configure the logger."""
    logger: logging.Logger = logging.getLogger("company-operation-data-gen")
    logger.setLevel(logging.DEBUG)
    handler: logging.Handler = logging.StreamHandler(stream=sys.stderr)
    formatter: logging.Formatter = logging.Formatter(fmt="%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


LOGGER: logging.Logger = init_logger()
"""The logger."""
