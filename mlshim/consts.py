"""
Created on Thu Nov  9 13:00:33 2017
"""
import os

_MATLAB = os.path.join(os.getenv("ProgramW6432"), "MATLAB")
_HERE = os.path.dirname(os.path.abspath(__file__))
_APPDATA = os.environ.get("APPDATA", None)

_SLEEP_TIME = 5
_START_TIMEOUT = 60
_RUN_TIMEOUT = 720
