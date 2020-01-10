"""Top-level package for mlshim"""
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

from .matlab import Matlab
