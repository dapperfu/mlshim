import logging
import os
import socket
import tempfile
import time
import uuid
from datetime import datetime
from subprocess import Popen
from typing import Optional
from typing import Union

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template

from .consts import _APPDATA
from .consts import _HERE
from .consts import _MATLAB_BASE
from .consts import _MATLAB_TIMEOUT
from .consts import _SLEEP_TIME
from .consts import _START_TIMEOUT
from .utils import abs_short_path
from .utils import get_licenses
from .utils import get_versions

if not os.path.exists(_MATLAB_BASE):
    raise FileNotFoundError(_MATLAB_BASE)


logger = logging.getLogger(__name__)


class Matlab:
    def __init__(
        self,
        *args,
        working_directory: str = os.path.abspath(os.curdir),
        start_directory: str = None,  # Matlab Start Directory
        template: Optional[str] = None,  # Template to render
        version: Optional[str] = None,  # Version of Matlab to run
        timeout: Union[int, bool] = 600,  # Seconds
        threaded: bool = True,  #
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
        # No ambigious calls.
        assert len(args) == 0
        # Instance UUID.
        self.uuid = uuid.uuid4()

        # Matlab script template
        self.template = template
        # Timeout
        self.timeout = timeout

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

        # Matlab start directory.
        if start_directory is None:
            self.start_directory = self.working_directory
        else:
            self.start_directory = start_directory

        self.pref_dir = os.path.join(
            self.working_directory, f"prefdir_{self._uuid}"
        )

        loader_directories = [os.path.join(_HERE, "templates"), os.curdir]
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
        if self.threaded:
            cmd_array.append("-singleCompThread")

        return cmd_array

    @property
    def _uuid(self):
        return str(self.uuid).replace("-", "")

    @property  # type: ignore
    def log_file(self):
        log_name = f"mlshim_{self._uuid}.log"
        return os.path.join(self.working_directory, log_name)

    @property  # type: ignore
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

    @property  # type: ignore
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
        assert len(args) == 0
        return self._template.render(obj=self, **kwargs)

    def gen_script(self, *args, **kwargs):
        """Write rendered Jinja2 script template and write to run_script path.

        All keyword arguments are passed to the Jinja2 template.
        """
        assert len(args) == 0
        while not os.path.exists(self.working_directory):
            os.makedirs(self.working_directory)
            time.sleep(1)
        run_script_body = self.render_template(**kwargs)
        with open(self.run_script, "w") as fid:
            print(run_script_body, file=fid)

    def run(self, *args, **kwargs):
        """Execute MATLAB® instance.

        """
        assert len(args) == 0
        self.gen_script(**kwargs)
        self._matlab_runner()

    @property
    def _template(self):
        return self._env.get_template(self.template)

    def _matlab_runner(self):
        """Run and monitor MATLAB®

        Exceptions:
            TimeoutError("MATLAB® Logfile creation timed out")
            TimeoutError("MATLAB® start timed out")
            TimeoutError("MATLAB® execution timed out")
            RuntimeError("MATLAB® processing failed")
        """
        os.environ["MATLAB_PREFDIR"] = self.pref_dir
        os.chdir(self.working_directory)

        # Remove log file if it exists.
        if os.path.exists(self.log_file):
            os.unlink(self.log_file)

        # Run the MATLAB® command
        proc = Popen(self.cmd)
        # Start timer
        t_start = time.time()

        # Step 1. Wait for the log file to exist
        while not os.path.exists(self.log_file):
            # Check to see if timeout has been exceeded
            if time.time() - t_start > _START_TIMEOUT:
                # Print the ERROR and raise a timeout ERROR
                logger.error(f"{_START_TIMEOUT:.2f}s Timelimit Exceeded")
                raise TimeoutError("Logfile creation timed out")
            logger.debug(
                f"logfile existence wait: {time.time() - t_start:.2f}, {t_start:.2f}, {time.time():.2f}"
            )
            # Sleep to allow the process to run
            time.sleep(_SLEEP_TIME)
        logger.info("MATLAB® logfile created")
        # Step 2
        # Wait for Matlab to start and execute the script
        while True:
            # Read the log file
            with open(self.log_file, "r") as fid:
                lines = fid.readlines()
            # Read each of the lines in it and remove the new line endings.
            lines = [line.strip() for line in lines]
            # If we've found the "Started" string, MATLAB® has made it that far into
            # the script.
            if "########## Started ##########" in lines:
                logger.info("MATLAB® Started")
                break
            # Check to see if timeout has been exceeded
            if time.time() - t_start > _START_TIMEOUT:
                proc.kill()
                # Print the error and raise a timeout error
                logger.error(f"{_START_TIMEOUT:.2f}s Timelimit Exceeded")
                raise TimeoutError("Matlab start timed out")
            logger.debug(
                f"MATLAB® start wait: {time.time() - t_start:.2f}, {t_start:.2f}, {time.time():.2f}"
            )
            time.sleep(_SLEEP_TIME)
        # While the processing isn't complete
        while True:
            # Open the log file read only
            with open(self.log_file, "r") as fid:
                lines = fid.readlines()
            # Strip ending new line from all lines
            lines = [line.strip() for line in lines]
            if self.timeout is None:
                logger.info("Not Waiting for Matlab")
                break
            # Check for the failed line
            elif "########## Failed ##########" in lines:
                logger.error("Not Waiting for Matlab")
                # Throw error
                raise RuntimeError("Matlab processing failed")
            # Check for the finished line
            if "########## Finished ##########" in lines:
                logger.info("Matlab finished")
                break
            # Check to see if timeout has been exceeded
            if time.time() - t_start > self.timeout:
                # Kill the process
                proc.kill()
                # Print the error and raise a timeout error
                logger.error(f"{timeout:.2f}s Timelimit Exceeded")
                raise TimeoutError("Matlab execution timed out")

            logger.debug(
                f"MATLAB® exceution wait: {time.time() - t_start:.2f}, {t_start:.2f}, {time.time():.2f}"
            )
            time.sleep(_SLEEP_TIME)

        # Debugging
        with open(self.log_file, "r") as fid:
            lines = fid.readlines()
        # Strip ending new line from all lines
        lines = [line.strip() for line in lines]
        if "Error checking out license" in lines:
            raise Exception("License Error.")
