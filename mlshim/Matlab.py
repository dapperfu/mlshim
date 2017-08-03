# -*- coding: utf-8 -*-
import os
import socket
import tempfile
import uuid
from datetime import datetime, timezone
from subprocess import Popen
from .utils import short_path

from jinja2 import Environment, FileSystemLoader, Template

matlab_root = r"C:\Program Files\Matlab"

class Matlab(object):
    """The summary line for a cl
    Attributes
    ----------
    START_TIMEOUT : int
        Amount of time to wait for Matlab to start and create the logfile.
    RUN_TIMEOUT : int
        Amount of time to allow Matlab to execute the scripts.
    """

    # Time in Seconds

    _SLEEP_TIME = 5
    _THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    _ENV = Environment(loader=FileSystemLoader(_THIS_DIR), trim_blocks=True)

    START_TIMEOUT = 180
    RUN_TIMEOUT = 7200

    def __init__(
            self,
            root=matlab_root,
            version=None,
            run_dir=tempfile.gettempdir()):
        """Example function with types documented in the docstring.


        Parameters
        ----------
        root : str
            Root directory for Matlab installs.
            Default: C:\Program Files\Matlab
        version : str
            MATLAB version to use. (R2014b, R2016a, R2017a)
            Default: Latest version found in `root`
            eg. R2016b > R2015a > R2009b ...
        run_dir : str
            Directory to put run script and log file in.
            Default: Output of ```tempfile.gettempdir()```
        """

        # Assign root.
        self.root = root
        # Assign version
        if version is None:
            # Get all matlab versions in the given root.
            vers = versions(self.root)
            self.version = vers[-1]
        else:
            self.version = version

        self.uuid = uuid.uuid4().hex

        # Verify that the executable exists given the root & version. Otherwise
        # raise error.
        if not os.path.exists(self.exe):
            raise FileNotFoundError(self.exe)

        self.run_dir = short_path(os.path.abspath(run_dir))

    def _cmd(self):
        """

        """
        cmd_array = [self.exe,
                     "-nosplash",
                     "-logfile", self.log_file,
                     "-r",
                     "run('{}');quit('force');".format(self.run_script)]
        return cmd_array

    @property
    def log_file(self):
        log_name = "mlshim_{}.log".format(self.uuid)
        return os.path.join(self.run_dir, log_name)

    @property
    def run_script(self):
        run_name = "mlshim_{}.m".format(self.uuid)
        return os.path.join(self.run_dir, run_name)

    @property
    def matlabroot(self):
        return os.path.join(self.root, self.version)

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
        headers["Script Creation"] = datetime.now(
            timezone.utc).astimezone().isoformat()
        headers["Machine"] = socket.gethostname()
        headers["User"] = os.getlogin()
        headers["UUID"] = self.uuid
        return headers

    def _generate_run_script(self,
                             scripts=list(),
                             datafiles=list(),
                             paths=list(),
                             working_directory=os.curdir):
        if isinstance(scripts, str):
            scripts = [scripts, ]
        if isinstance(datafiles, str):
            datafiles = [datafiles, ]
        if isinstance(paths, str):
            paths = [paths, ]
        working_directory = os.path.abspath(working_directory)
        return self._template.render(headers=self.headers,
                                     working_directory=working_directory,
                                     paths=paths,
                                     datafiles=datafiles,
                                     scripts=scripts)

    def run(self, scripts=list(), datafiles=list(), paths=list(), cwd=os.curdir):
        """Example function with types documented in the docstring.

        `PEP 484`_ type annotations are supported. If attribute, parameter, and
        return types are annotated according to `PEP 484`_, they do not need to be
        included in the docstring:

        Parameters
        ----------
        scripts : str, list
            Matlab script(s) to run. Must exist in the path.
        datafiles : str, list
            Data files to load. Loaded with `load` in the Matlab environment.
        paths : str, list
        cwd : str
            The working directory to execute Matlab in.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """

        cwd = os.path.abspath(cwd)
        run_script_body = self._generate_run_script(scripts, datafiles, paths, cwd)
        with open(self.run_script, 'w') as fid:
            print(run_script_body, file=fid)
        matlab_run_wait(self._cmd, self.log_file)

    @property
    def _template(self):
        return self._ENV.get_template("matlab_run_template.jinja")


def versions(root=matlab_root):
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

import time

def matlab_run_wait(cmd_array, matlab_log=None):
    """
    Run the cmd_array with Popen, parse matlab_log for
        output from generate_run_script.

    Wait until matlab finishes to exit.

    Args:

        cmd_array (list)
            Output of ```mlrunner.matlab_cmd```

        matlab_log (str)
            Logfile to parse for status.

    Exceptions:
        TimeoutError("Logfile creation timed out")
        TimeoutError("Matlab start timed out")
        TimeoutError("Matlab execution timed out")
        Runtimeprint("Matlab processing failed")
    """
       
    # Remove log file if it exists.
    if os.path.exists(matlab_log):
        os.unlink(matlab_log)
    
    # Run the matlab command
    proc = Popen(cmd_array)
    # Start timer
    t_start = time.time()

    # Step 1. Wait for the log file to exist
    while not os.path.exists(matlab_log):
        # Check to see if timeout has been exceeded
        if time.time() - t_start > START_TIMEOUT:
            # Print the ERROR and raise a timeout ERROR
            print('{:.2f}s Timelimit Exceeded'.format(START_TIMEOUT))
            raise TimeoutError("Logfile creation timed out")
        print("Waiting for log to exist.")
        # Sleep to allow the process to run
        time.sleep(SLEEP_TIME)
    if not os.path.exists(matlab_log):
        print('Matlab start failed')
        # exit
    else:
        print("Logfile created in {:.2f}s".format(time.time() - t_start))
    # Step 2
    # Wait for Matlab to start and execute the script
    started = False
    while not started:
        # Read the log file
        with open(matlab_log, "r") as fid:
            lines = fid.readlines()
        # Read each of the lines in it and remove the new line endings.
        lines = [line.strip() for line in lines]
        # If we've found the "Started" string, matlab has made it that far into
        # the script.
        if "########## Started ##########" in lines:
            started = True
            continue
        # Check to see if timeout has been exceeded
        if time.time() - t_start > START_TIMEOUT:
            proc.kill()
            # Print the error and raise a timeout error
            print('{:.2f}s Timelimit Exceeded'.format(START_TIMEOUT))
            TimeoutError("Matlab start timed out")
        print("Waiting for Matlab to start.")
        time.sleep(SLEEP_TIME)
    # While the processing isn't complete
    while True:
        # Open the log file read only
        with open(matlab_log, "r") as fid:
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
        if time.time() - t_start > START_TIMEOUT:
            # Kill the process
            proc.kill()
            # Print the error and raise a timeout error
            print('%.2fs Timelimit Exceeded', RUN_TIMEOUT)
            raise TimeoutError("Matlab execution timed out")
        print("Waiting for Matlab to finish.")
        time.sleep(SLEEP_TIME)
