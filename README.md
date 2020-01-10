# mlshim

A shim to run MATLAB with through Python. Uses Jinja2 to generate a .m file to run.

[Windows only](https://www.mathworks.com/help/matlab/ref/matlabwindows.html) since that what Automotive, Aerospace, & Heavy Equipment are all using

## Design & Justification:

Created for use with generating Model Based Design code with Jenkins and maintaining traceability. (ISO 2626, IEC 61508, DO-178B/C).

- Uses a new [MATLAB preferences](https://www.mathworks.com/matlabcentral/answers/93696-how-do-i-change-the-matlab-preferences-directory-location) directory to start MATLAB.
  - Removes any customization that engineers may have in ```startup.m``` or their preferences from causing potential issues.
  - Repeatable builds
  - Moves MATLAB towards proper DevOps.
- Create artifacts for everything that MATLAB touches.
- Run MATLAB from Python:
  - Treat MATLAB as one tool in a toolchain (not the entire toolchain)
  - Execute Matlab in Python unit tests.

# Install

    pip install git+https://github.com/jed-frey/mlshim.git

# Alternatives

## Python-matlab-bridge

https://arokem.github.io/python-matlab-bridge/

For just interactive Python <-> MATLAB scripting this is an excellent solution but I ran into issues with my specific use cases.

- Pros:
  - Works great.
  - Jupyter notebook magics
- Cons:
  - If something interrupts the bridge script MATLAB is no longer controllable. (i.e. ```clear all```)
  - Requires admin access to install libzmq. Making it harder to deploy in a corporate environment.


## MATLAB Engine API for Python

- Pros:
  - Supported by [Mathworks](https://www.mathworks.com/help/matlab/matlab-engine-for-python.html)
- Cons:
  - Beholden to Mathwork's and your company's Python & MATLAB upgrade cycle. For example R2016b only supports 2.7, 3.3, 3.4, and 3.5.
  - For reasons outside of engineers control (certifications, etc) projects are often on older versions of Matlab.

## MATLAB flag options:

Start MATLAB program from Windows system prompt.

https://www.mathworks.com/help/matlab/ref/matlabwindows.html

### ```-wait```

> Use in a script to process the results from MATLAB. Calling MATLAB with this option blocks the script from continuing until the results are generated.

- Pros:
  - No Python needed
  - Supported by Mathworks
- Cons:
  - MATLAB can hang indefinitely.

## ```-batch```

> Execute MATLAB script, statement, or function non-interactively. MATLAB:
>
> - Starts without the desktop
> - Does not display the splash screen
> - Executes statement
> - Disables changes to preferences
> - Disables toolbox caching
> - Logs text to stdout and stderr
> - Does not display dialog boxes
> - Exits automatically with exit code 0 if script executes successfully. Otherwise, MATLAB terminates with a non-zero exit code.

- Pros:
  - No Python Needed.
  - Supported by MathWorks
  - Perfect solution in an *ideal* world.
- Cons:
  - R2019a+ only. (Certified software development often lags on versions.)
  - No desktop makes debugging very tedious.
    Way too much Simulink/MATLAB code is 'manumatic' and needs a trained monkey for edge cases. (Source: Used to be said trained monkey).
