"""
Created on Thu Nov  9 13:00:33 2017
"""
import os
from typing import Optional


_SLEEP_TIME = 10  # seconds
_START_TIMEOUT = 180  # seconds
_MATLAB_TIMEOUT: int = int(os.environ.get("MATLAB_TIMEOUT", 600))


_MATLAB_DEFAULT: str = os.path.join(os.getenv("ProgramW6432", ""), "MATLAB")
_MATLAB_BASE: str = os.environ.get("MATLAB_BASE", _MATLAB_DEFAULT)
_HERE: str = os.path.dirname(os.path.abspath(__file__))
_APPDATA: Optional[str] = os.environ.get("APPDATA", None)
