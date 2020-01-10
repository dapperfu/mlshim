"""
Created on Thu Nov  9 13:00:33 2017
"""
import os

_MATLAB_DEFAULT = os.path.join(os.getenv("ProgramW6432"), "MATLAB")
_MATLAB_BASE = os.environ.get("MATLAB_BASE", _MATLAB_DEFAULT)
_HERE = os.path.dirname(os.path.abspath(__file__))
_APPDATA = os.environ.get("APPDATA", None)
