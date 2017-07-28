# -*- coding: utf-8 -*-
from datetime import datetime, timezone
import socket
import os
import tempfile
import uuid
from jinja2 import Template

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader(THIS_DIR),
                    trim_blocks=True)
                    
def matlab_cmd(matlab_root=r"C:\Program Files\MATLAB",
               matlab_ver=r"R2016a",
               init_script=None,
               log_file=None):
    """
    Get a Popen command array to call matlab.

    Note: This is a rather dumb script. It just mashes the matlab_root and
                    matlab_ver together. If you have a custom install of Matlab
                    in "C:\Matlab\MySpecialMatlabVersion" set
                matlab_root = "C:\Matlab"
                matlab_ver  = "MySpecialMatlabVersion"
    Args:
        matlab_root (str): Matlab path to use as root directory where Matlab is
            installed
            Default: C:\Program Files\MATLAB

        matlab_ver (str): Matlab version to use.
            Default: R2016a

        init_script (str):
            Script to run when matlab starts, called with ```run(init_script)```
            This is typically going to be the file created with ```generate_run_script```
            See also: http://www.mathworks.com/help/matlab/ref/run.html

        log_file (str):
            File where to log Matlab output.
            See also: http://www.mathworks.com/help/matlab/ref/matlabwindows.html

    Returns:
        cmd_array (list): list of commands to run for Popen
                          (or other similar function)
    """
    """
    if not os.path.exists(init_script):
        raise FileNotFoundError(
            "Init script \"{}\" not found".format(init_script))
    matlab_exe = os.path.join(matlab_root, matlab_ver, "bin", "matlab.exe")
    if not os.path.exists(matlab_exe):
        raise FileNotFoundError(
            "Matlab executable \"{}\" not found".format(matlab_exe))
    """
    if log_file is None:
        log_name = "ml_runner_{}.log".format(tempfile._get_candidate_names())
        log_file = os.path.join(tempfile._get_default_tempdir(), log_name)
        
    matlab_exe = os.path.join(matlab_root, matlab_ver, "bin", "matlab.exe")
    cmd_array = [matlab_exe,
                 "-nosplash",
                 "-logfile", log_file,
                 "-r",
                 "run('{}');quit force;".format(init_script)]
    return cmd_array


def opt_script(script, **opts):
    """
    Generate opt_script body from a template.

    opt_scripts are MATLAB functions designed to return a struct if
    called with no input variables and one output variable. The options
    returned are the default options for the script.

    The struct can then be manipulated and then passed back into the script to
    run it.

    Example:
        script = opt_script(script="sample_opt_script", arg1="arg1", arg2=5)

    Args (dict):
        opt script args named inputs.
    Returns (str):
        Rendered script.
    """
    # Get template.
    matlab_template = env.get_template("matlab_opt_script_template.jinja")
    # Render and return.
    return matlab_template.render(matlab_script=script, opts=opts)


def generate_run_script(write=False,
                        headers=None,
                        working_directory=None,
                        script_body='',
                        load_mats=list(),
                        ext_scripts=list()):
    """
    Args:
        Arguments are parsed in the following order:
        headers (dict):
            Dict of additional headers to add.
                By default script creation time, hostname, and windows username are saved.

        working_directory (str):
            Change to working directory in matlab.

        load_mats (list):
            List of matfile paths to load.

        ext_scripts (list):
            List of external scripts to run

        script_body (str) [Default: '']
            Text of m-code to run in generated run_script.

        write (bool/str) [Default: False]:
            Write the script to a file.
            If write is a bool, a temp file is created and the file
            name returned. If write is a string it is used as file name

    Returns:
        If write = False:
            generate_run_script returns the script as a string
        If write = True
            generate_run_script writes the script into a tempfile and
            returns the filename as a string.
        If write = (string):
            generate_run_script writes the script into a the file name
            specified by write
    """
    run_uuid=uuid.uuid4()
    # If headers aren't specified, create an empty dictionary to store the
    # default settings
    if headers is None:
        headers = dict()
        # Add script creation time,
        # script creation machine
        # script creation,
        # and random uuid.
        headers["Script Creation"] = datetime.now(timezone.utc).astimezone().isoformat()
        headers["Machine"] = socket.gethostname()
        headers["User"] = os.getlogin()
        headers["UUID"] = str(uuid.uuid4())

    # Read the matlab script template.
    matlab_template = env.get_template("matlab_template.jinja")

    # Render it with known variables.
    script = matlab_template.render(headers=headers,
                                    ext_scripts=ext_scripts,
                                    load_mats=load_mats,
                                    working_directory=working_directory,
                                    int_script=int_script)                             
    # Determine where the script ends up
    if write:
        # If is write is just true, generate a temporary file
        if isinstance(write, bool):
            fid = tempfile.NamedTemporaryFile(mode='w',
                                              suffix='.m',
                                              delete=False)
        else:
            # Otherwise open the file for writing
            fid = open(write, mode="w")
        # Write the script to the file identifier
        print(script, file=fid)
        # Close the file identifier.
        fid.close()
        # Return the file name.
        return fid.name
    else:
        # If not write, just return the script.
        return script