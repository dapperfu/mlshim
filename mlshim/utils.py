# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes
_GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
_GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
_GetShortPathNameW.restype = wintypes.DWORD

from .consts import _MATLAB, _APPDATA

def short_path(long_name):
    """
    Gets the short path name of a given long path.
    http://stackoverflow.com/a/23598461/200291
    """
    output_buf_size = 0
    while True:
        output_buf = ctypes.create_unicode_buffer(output_buf_size)
        needed = _GetShortPathNameW(long_name, output_buf, output_buf_size)
        if output_buf_size >= needed:
            return output_buf.value
        else:
            output_buf_size = needed
            
import os
import glob

def get_licenses(matlab_version=None, root=None):
    if root is None:
        if _APPDATA is None:
            return None
        if matlab_version is None:
            matlab_version = get_versions()[-1]
        root = os.path.join(_APPDATA,
                            'MathWorks',
                            'MATLAB',
                            '{}_licenses'.format(matlab_version))
    license_files = glob.glob(os.path.join(root, '*.lic'))
    return license_files

def get_versions(root=_MATLAB):
    """Return all versions of MATLAB installed in a given folder.
    
    Returns
    -------
    list

    """
    vers = list()
    for ver in os.listdir(root):
        if os.path.exists(os.path.join(root, ver, "bin", "matlab.exe")):
            vers.append(ver)
    vers.sort()
    return vers
