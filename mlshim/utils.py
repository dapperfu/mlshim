import ctypes
import glob
import os
from ctypes import wintypes

_GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
_GetShortPathNameW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.LPWSTR,
    wintypes.DWORD,
]
_GetShortPathNameW.restype = wintypes.DWORD

from mlshim.consts import _APPDATA
from mlshim.consts import _HERE

from functools import wraps


def clean_log(log_path):
    pass


def abs_short_path(f):
    """ Wrapper to return absolute short path for Windows.

    Returns a short Windows path if the path exists.
    Returns absolute path otherwise.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        # Get a path from the function
        path = f(*args, **kwargs)
        # Get the absolute path.
        path = os.path.abspath(path)
        # If the path exists (short path dosen't exist otherwise)
        if os.path.exists(path):
            path = short_path(path)
        # Return Windowfied path.
        return path

    return wrapper


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


def get_licenses(matlab_version=None, root=None):
    """Return all licenses for the current user."""
    if root is None:
        if _APPDATA is None:
            return None
        if matlab_version is None:
            matlab_version = get_versions()[-1]
        root = os.path.join(
            _APPDATA, "MathWorks", "MATLAB", f"{matlab_version}_licenses"
        )
    license_files = glob.glob(os.path.join(root, "*.lic"))
    return license_files


def get_templates():
    """Return all templates in the templates directory."""
    import glob

    templates = glob.glob(os.path.join(_HERE, "templates", "*.m"))
    templates = [os.path.basename(path) for path in templates]
    return templates


def get_versions(root=None):
    """Return all versions of MATLAB installed in a given folder.

    Returns
    -------
    list

    """
    if root is None:
        from .consts import _MATLAB_BASE as root
    vers = list()
    for ver in os.listdir(root):
        if os.path.exists(os.path.join(root, ver, "bin", "matlab.exe")):
            vers.append(ver)
    vers.sort()
    return vers
