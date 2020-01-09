import datetime
import os
import socket
import tempfile
import time
from datetime import datetime
from datetime import timezone
from subprocess import Popen

from cached_property import cached_property
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template

from .consts import _APPDATA
from .consts import _HERE
from .consts import _MATLAB
from .utils import get_licenses
from .utils import get_versions
from .utils import short_path

if not os.path.exists(_MATLAB):
    raise FileNotFoundError(_MATLAB)

_SLEEP_TIME = 0.5
_START_TIMEOUT = 180
_RUN_TIMEOUT = 3600


class Matlab:
    def __init__(
        self,
        working_directory=os.path.abspath(os.curdir),
        template="run_script.m",
        version=None,
        pref_dir=None,
        env_dirs=list(),
    ):
        r"""Example function with types documented in the docstring.


        Parameters
        ----------
        root : str
            Root directory for Matlab installs.
            Default: C:\Program Files\Matlab
        version : str
            MATLAB version to use. (R2014b, R2016a, R2017b, etc.)
            Default: Latest version found in `root`
            eg. R2016b > R2015a > R2009b ...
        working_directory : str
            Directory to put run script and log file in.
            Default: Output of ```tempfile.gettempdir()```
        """
        # Matlab script template
        self.template = template
        # Assign version
        if version is None:
            # Get all matlab versions in the given root.
            vers = get_versions()
            self.version = vers[-1]
        else:
            self.version = version

        # Verify that the executable exists given the root & version. Otherwise
        # raise error.
        if not os.path.exists(self.exe):
            raise FileNotFoundError(self.exe)

        self.working_directory = os.path.abspath(working_directory)

        if pref_dir is None:
            self.pref_dir = os.path.join(self.working_directory, ".prefs")
        else:
            self.pref_dir = pref_dir

        self.licences = get_licenses()

        loader_directories = [_HERE, os.curdir] + env_dirs
        self._env = Environment(
            loader=FileSystemLoader(loader_directories), trim_blocks=True
        )

    @property
    def cmd(self):
        """

        """
        cmd_array = [
            self.exe,
            "-logfile",
            self.log_file,
            "-r",
            f"run('{self.run_script}');",
        ]
        return cmd_array

    @property
    def log_file(self):
        log_name = f"mlshim_{self.now}.log"
        return os.path.join(self.working_directory, log_name)

    @property
    def run_script(self):
        run_name = f"mlshim_{self.now}.m"
        return os.path.abspath(os.path.join(self.working_directory, run_name))

    @property
    def matlabroot(self):
        return os.path.join(_MATLAB, self.version)

    @property
    def exe(self):
        return short_path(os.path.join(self.matlabroot, "bin", "matlab.exe"))

    @property
    def headers(self):
        headers = dict()
        # Add script creation time,
        # script creation machine
        # script creation,
        # and random uuid.
        headers["Script Creation"] = self._now.astimezone().isoformat()
        headers["Machine"] = socket.gethostname()
        headers["User"] = os.getlogin()
        return headers

    def _render_template(self, **kwargs):
        return self._template.render(obj=self, **kwargs)

    def run(self, **kwargs):
        run_script_body = self._render_template(**kwargs)
        with open(self.run_script, "w") as fid:
            print(run_script_body, file=fid)
        time.sleep(1)
        matlab_runner(self)

    @cached_property
    def _now(self):
        return datetime.datetime.now()

    @property
    def now(self):
        return datetime.datetime.strftime(self._now, "%Y%b%d_%H%m%S_%f")

    @property
    def _template(self):
        return self._env.get_template(self.template)


def matlab_runner(mlab):
    """
    Run the cmd_array with Popen, parse mlab.log_file for
        output from generate_run_script.

    Wait until matlab finishes to exit.

    Exceptions:
        TimeoutError("Logfile creation timed out")
        TimeoutError("Matlab start timed out")
        TimeoutError("Matlab execution timed out")
        Runtimeprint("Matlab processing failed")
    """

    if not os.path.exists(mlab.working_directory):
        os.makedirs(mlab.working_directory)

    os.environ["MATLAB_PREFDIR"] = mlab.prefdir
    os.chdir(mlab.working_directory)

    # Remove log file if it exists.
    if os.path.exists(mlab.log_file):
        os.unlink(mlab.log_file)

    # Run the matlab command
    proc = Popen(mlab.cmd)
    # Start timer
    t_start = time.time()

    # Step 1. Wait for the log file to exist
    while not os.path.exists(mlab.log_file):
        # Check to see if timeout has been exceeded
        if time.time() - t_start > _START_TIMEOUT:
            # Print the ERROR and raise a timeout ERROR
            print(f"{_START_TIMEOUT:.2f}s Timelimit Exceeded")
            raise TimeoutError("Logfile creation timed out")
        # Sleep to allow the process to run
        time.sleep(_SLEEP_TIME)
    # Step 2
    # Wait for Matlab to start and execute the script
    started = False
    while not started:
        # Read the log file
        with open(mlab.log_file, "r") as fid:
            lines = fid.readlines()
        # Read each of the lines in it and remove the new line endings.
        lines = [line.strip() for line in lines]
        # If we've found the "Started" string, matlab has made it that far into
        # the script.
        if "########## Started ##########" in lines:
            started = True
            break
        # Check to see if timeout has been exceeded
        if time.time() - t_start > _START_TIMEOUT:
            proc.kill()
            # Print the error and raise a timeout error
            print(f"{_START_TIMEOUT:.2f}s Timelimit Exceeded")
            raise TimeoutError("Matlab start timed out")
        time.sleep(_SLEEP_TIME)
    # While the processing isn't complete
    while True:
        # Open the log file read only
        with open(mlab.log_file, "r") as fid:
            lines = fid.readlines()
        # Strip ending new line from all lines
        lines = [line.strip() for line in lines]
        # Check for the finished line
        if "########## Finished ##########" in lines:
            print("Matlab finished")
            break
        # Check for the failed line
        elif "########## Failed ##########" in lines:
            print("Matlab failed")
            # Throw error
            raise RuntimeError("Matlab processing failed")
        # Check to see if timeout has been exceeded
        if time.time() - t_start > _START_TIMEOUT:
            # Kill the process
            proc.kill()
            # Print the error and raise a timeout error
            print("%.2fs Timelimit Exceeded", _RUN_TIMEOUT)
            raise TimeoutError("Matlab execution timed out")
        time.sleep(_SLEEP_TIME)
