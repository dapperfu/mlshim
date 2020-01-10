"""Console script for mlshim."""
import os
import sys

import click

from mlshim import __name__ as module_name
from mlshim import Matlab
from mlshim.consts import _MATLAB_BASE
from mlshim.log import configure_logger
from mlshim.log import logging


class Config:
    """
    An information object to pass data between CLI functions.
    """

    def __init__(self):  # Note: This object must have an empty constructor.
        pass


# pass_config is a decorator for functions that pass 'Config' objects.
#: pylint: disable=invalid-name
pass_config = click.make_pass_decorator(Config, ensure=True)

# Change the options to below to suit the actual options for your task (or
# tasks).
@click.group()
@click.option("--verbose", "-v", count=True, help="Enable verbose output.")
@click.option(
    "--working_directory",
    "-wd",
    help="MATLAB Working Directory",
    default=os.path.abspath(os.path.curdir),
)
@click.option(
    "--matlab_base", "--base", help="MATLAB base", default=_MATLAB_BASE
)
@click.option("--debug_file", "-d", help="Python Debug File", default=None)
@click.option("--version", "--ver", help="MATLAB version", default=None)
@pass_config
def main(
    config, **kwargs
):  # info: Config, verbose: int, log: str, ver: str, tempdir):
    """
    # Use the verbosity count to determine the logging level.
    """
    for key, value in kwargs.items():
        setattr(config, key, value)
    config.logging = configure_logger(
        stream_level=config.verbose, debug_file=config.debug_file,
    )
    config.matlab = Matlab(template=None, version=config.version)
    config.logging.debug(f"MATLAB Prefs Dir: {config.matlab.pref_dir}")
    config.logging.debug(
        f"MATLAB Working Directory: {config.matlab.working_directory}"
    )
    config.logging.debug(f"MATLAB Log File: {config.matlab.log_file}")


@main.command()
@pass_config
def debug(config: Config):
    for key, value in config.__dict__.items():
        config.logging.info(f"{key}: {value}")


@main.command()
@pass_config
def launch(_: Config):
    """
    
    """
    matlab = MATLAB(template="launch_template.m")
    matlab.run(wait=False)


@main.command()
@click.argument("m_script")
@pass_config
def run(_: Config, m_script: str):
    """
    Run a matlab script.
    """
    from mlshim import MATLAB

    matlab = MATLAB(template="run_template.m")
    config.logging.info(f"MATLAB Prefs Dir: {matlab.pref_dir}")
    config.logging.info(f"MATLAB Working Directory: {matlab.working_directory}")
    config.logging.info(f"MATLAB Log File: {matlab.log_file}")
    matlab.run(wait=True, scripts=[m_script])


@main.command()
@click.argument("model")
@pass_config
def build(_: Config, model: str):
    """
    Run a matlab script.
    """
    from mlshim import MATLAB

    matlab = MATLAB(template="run_template.m")
    config.logging.info(f"MATLAB Prefs Dir: {matlab.pref_dir}")
    config.logging.info(f"MATLAB Working Directory: {matlab.working_directory}")
    config.logging.info(f"MATLAB Log File: {matlab.log_file}")
    matlab.run(wait=True, scripts=m_scripts)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
