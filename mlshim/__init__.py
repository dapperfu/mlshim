__version__ = "0.0.1"
import os
import socket
import tempfile
import time
import uuid
from datetime import datetime, timezone
from subprocess import Popen

from jinja2 import Environment, FileSystemLoader, Template

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

    def __init__(self, root=r"C:\Program Files\Matlab", version=None, license=None, run_dir=tempfile.gettempdir()):
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
        
        # Verify that the executable exists given the root & version. Otherwise raise error.
        if not os.path.exists(self.exe):
            raise FileNotFoundError(self.exe)
        
        self.license = license
        self.run_dir = run_dir

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
        return os.path.join(self.run_dir, log_name)
        
    @property
    def matlabroot(self):
        return os.path.join(self.root, self.version)
    
    @property
    def exe(self):
        return os.path.join(self.matlabroot, "bin", "matlab.exe")
    
    @property
    def headers(self):
        headers = dict()
        # Add script creation time,
        # script creation machine
        # script creation,
        # and random uuid.
        headers["Script Creation"] = datetime.now(timezone.utc).astimezone().isoformat()
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
            scripts = [scripts,]
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
        
    def run(scripts=list(), data=list(), paths=list(), cwd=os.curdir):
        """Example function with types documented in the docstring.

        `PEP 484`_ type annotations are supported. If attribute, parameter, and
        return types are annotated according to `PEP 484`_, they do not need to be
        included in the docstring:

        Parameters
        ----------
        scripts : str, list
            Matlab script(s) to run. Must exist in the path.
        data : str, list
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
            
        run_script = self._generate_run_script(script, data, paths, cwd)
        
        #cmd = self._
        
    @property
    def _template(self):
        return self._ENV.get_template("matlab_run_template.jinja")

def versions(root):
    """
    
    Returns
    -------
    list
        
    """
    vers = list()
    for ver in os.listdir(root):
        if os.path.exists(os.path.join(root,ver,"bin","matlab.exe")):
            vers.append(ver)
    vers.sort()
    return vers