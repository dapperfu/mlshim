import os


def test_3():
    from mlshim import Matlab

    Matlab()


def test_4():
    from mlshim import Matlab
    from mlshim.utils import get_versions

    versions = get_versions()
    for version in versions:
        matlab = Matlab(version=version)
        assert matlab.version == version


def test_4():
    from mlshim import Matlab
    from mlshim.utils import get_versions

    versions = get_versions()
    for version in versions:
        matlab = Matlab(version=version)
        matlab.run(scripts=[f"disp('Hello World: {version}');"])
