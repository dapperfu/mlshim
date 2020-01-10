import os

import pytest

from mlshim import Matlab
from mlshim.utils import get_versions

versions = get_versions()


@pytest.mark.parametrize("version", get_versions())
def xtest_all_versions_launch(version):
    matlab = Matlab(version=version)
    matlab.run(scripts=[f"disp('Hello World: {version}');"])


@pytest.mark.parametrize("version", get_versions())
def test_all_versions_bench(version):
    matlab = Matlab(version=version)
    matlab.run(scripts=[f"bench;"])
