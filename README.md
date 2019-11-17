# mlshim

A shim to run Matlab with Python. [Windows only](https://www.mathworks.com/help/matlab/ref/matlabwindows.html).

Uses Jinja2 to generate a .m file to run. 

Uses a new [Matlab preferences](https://www.mathworks.com/matlabcentral/answers/93696-how-do-i-change-the-matlab-preferences-directory-location) directory to start Matlab from a clean slate.

Created for use with generating Model Based Design code with Jenkins and maintaining tracability. (ISO 26262/IEC 61508).

This is heavily tailored to suit my use case, FOSS because I developed it on my time for use at work.

- Run Matlab from Python
- Run Matlab through pytest
- Create artifacts for everything that Matlab runs.


# Alternatives

Unless you need to thread the needle on my use case, these are probably a better idea:

## Python-matlab-bridge

https://arokem.github.io/python-matlab-bridge/

For just interactive Python <-> Matlab scripting this is an excellent solution but I ran into issues with my specific use cases. 

- Pros:
  - Works great.
  - Jupyter notebook magics
- Cons:
  - If something intetrrupts the bridge script Matlab is no longer controllable.
  - Requires admin access to install libzmq. Making it harder to deploy in a corporate environment.


## MATLAB Engine API for Python

- Pros:
  - Supported by [Mathworks](https://www.mathworks.com/help/matlab/matlab-engine-for-python.html)
- Cons:
  - Beholden to Mathwork's and your company's Python & Matlab upgrade cycle. For example R2016b only supports 2.7, 3.3, 3.4, and 3.5.
  - For reasons outside of my control some of our certified projects are still on much older versions.

## /wait

- Pros:
  - No Python needed
- Cons:
  - Matlab can hang indefinitely.

# Install

    pip install git+https://github.com/jed-frey/mlshim.git