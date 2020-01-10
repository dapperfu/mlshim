import datetime
import os
import socket
import tempfile
import time
import uuid
from datetime import datetime
from datetime import timezone
from subprocess import Popen

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template

from .consts import _APPDATA
from .consts import _HERE
from .consts import _MATLAB_BASE
from .utils import abs_short_path
from .utils import get_licenses
from .utils import get_versions

# from cached_property import cached_property

_SLEEP_TIME = 5  # seconds
_START_TIMEOUT = 60  # seconds

if not os.path.exists(_MATLAB_BASE):
    raise FileNotFoundError(_MATLAB_BASE)


class Matlab:
    def __init__(
        self,
        working_directory=os.path.abspath(os.curdir),
        pref_dir=None,
        template="run_template.m",
        version=None,
        timeout=720,
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
        # Instance UUID.
        self.uuid = uuid.uuid4()
        # Matlab script template
        self.template = template
        # Assign version
        if version is None:
            # Get all MATLAB® versions in the given root.
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
            self.pref_dir = os.path.join(
                self.working_directory, f"prefs_{self.uuid}"
            )
        else:
            self.pref_dir = pref_dir

        loader_directories = [
            os.path.join(_HERE, "templates"),
            os.curdir,
        ]
        self._env = Environment(
            loader=FileSystemLoader(loader_directories), trim_blocks=True
        )

    def __repr__(self):
        return (
            f"Matlab<{self.version}, '{self.working_directory}', {self.uuid}>"
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
    def _uuid(self):
        return str(self.uuid).replace("-", "")

    @property
    @abs_short_path
    def log_file(self):
        log_name = f"mlshim_{self._uuid}.log"
        return os.path.join(self.working_directory, log_name)

    @property
    @abs_short_path
    def run_script(self):
        run_name = f"mlshim_{self._uuid}.m"
        return os.path.join(self.working_directory, run_name)

    @property
    def matlabroot(self):
        """matlabroot
        
        A character vector giving the full path to the folder where MATLAB® is installed.
        
        Should match the output of calling ```matlabroot``` inside of MATLAB®.
        """
        return os.path.join(_MATLAB_BASE, self.version)

    @property
    @abs_short_path
    def exe(self):
        """Full path to the MATLAB® executable."""
        return os.path.join(self.matlabroot, "bin", "matlab.exe")

    @property
    def headers(self):
        headers = dict()
        # Add script creation time,
        # Matlab object instance uuid,
        # unique script uuid.
        headers["Script Creation"] = datetime.now().astimezone().isoformat()
        headers["mlshim uuid"] = self.uuid
        headers["script uuid"] = uuid.uuid4()
        return headers

    def render_template(self, *args, **kwargs):
        """Render Jinja2 MATLAB® script template.
        
        All keyword arguments are passed to the Jinja2 template.
        """
        assert len(args)==0
        return self._template.render(obj=self, **kwargs)
        
 
    def gen_script(self, *args, **kwargs):
        """Write rendered Jinja2 script template and write to run_script path.
        
        All keyword arguments are passed to the Jinja2 template.
        """
        assert len(args)==0
        run_script_body = self.render_template(**kwargs)
        with open(self.run_script, "w") as fid:
            print(run_script_body, file=fid)

    def run(self, *args, wait=True, timeout=720, **kwargs):
        """Execute MATLAB® instance.
        
        """
        assert len(args)==0
        if not os.path.exists(self.working_directory):
            os.makedirs(self.working_directory)
        time.sleep(1)
        self.gen_script(**kwargs)
        matlab_runner(self, wait=wait, timeout=timeout)

    @property
    def _template(self):
        return self._env.get_template(self.template)


    def _matlab_runner(matlab, wait=True, timeout=720):
        """
        Run the cmd_array with Popen, parse matlab.log_file for
            output from generate_run_script.

        Wait until MATLAB® finishes to exit.

        Exceptions:
            TimeoutError("Logfile creation timed out")
            TimeoutError("Matlab start timed out")
            TimeoutError("Matlab execution timed out")
            Runtimeprint("Matlab processing failed")
        """
        if not os.path.exists(matlab.working_directory):
            os.makedirs(matlab.working_directory)

        os.environ["MATLAB_PREFDIR"] = matlab.pref_dir
        os.chdir(matlab.working_directory)

        # Remove log file if it exists.
        if os.path.exists(matlab.log_file):
            os.unlink(matlab.log_file)

        # Run the MATLAB® command
        proc = Popen(matlab.cmd)
        # Start timer
        t_start = time.time()

        # Step 1. Wait for the log file to exist
        while not os.path.exists(matlab.log_file):
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
            with open(matlab.log_file, "r") as fid:
                lines = fid.readlines()
            # Read each of the lines in it and remove the new line endings.
            lines = [line.strip() for line in lines]
            # If we've found the "Started" string, MATLAB® has made it that far into
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
            with open(matlab.log_file, "r") as fid:
                lines = fid.readlines()
            # Strip ending new line from all lines
            lines = [line.strip() for line in lines]
            if wait is False:
                print("Not Waiting for Matlab")
                break
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
            if time.time() - t_start > timeout:
                # Kill the process
                proc.kill()
                # Print the error and raise a timeout error
                print(f"{timeout:.2f}s Timelimit Exceeded")
                raise TimeoutError("Matlab execution timed out")
            print(proc)
            time.sleep(_SLEEP_TIME)
