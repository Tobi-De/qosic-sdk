"""Top-level package for qosic-sdk."""
from .qosic import Client  # noqa
from .models import (  # noqa
    MtnConfig,
    MTN,
    MOOV,
    OPERATION_CONFIRMED,
    OPERATION_REJECTED,
    get_random_string
)

__author__ = """Tobi DEGNON"""
__email__ = "degnonfrancis@gmail.com"
__version__ = "2.0.0"
