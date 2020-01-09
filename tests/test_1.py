import os

import mlshim


def test_1(matlab_root):
    # Find all faux versions of matlab in the test directory.
    versions = mlshim.versions(matlab_root)
    # Assert that there are 19 found versions.
    assert len(versions) == 19
    # Assert that all versions end with 'b'.
    for version in versions:
        assert version.endswith("b")


def test_2(matlab_root):
    # Get all directories in the matlab root
    dirs = os.listdir(matlab_root)
    # Assert 38 found directories.
    # 19 R20##a - Does not contain bin/matlab.exe
    # 19 R20##b - Contain bin/matlab.exe
    assert len(dirs) == 38


def test_3(matlab_root):
    mlshim.Matlab(root=matlab_root)


def test_4(matlab_root):
    versions = mlshim.versions(matlab_root)
    for version in versions:
        ml = mlshim.Matlab(root=matlab_root, version=version)
        assert ml.version == version
