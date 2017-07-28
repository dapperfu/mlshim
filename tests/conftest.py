import pytest

@pytest.fixture(scope='session')
def matlab_root(tmpdir_factory):
    mlroot = tmpdir_factory.mktemp("matlab")
    
    # Directories without Matlab installed.
    for release in range(2006, 2025):
        mlroot.join("R{}a".format(release)).ensure_dir()
        
    # Directories with Matlab installed.
    for release in range(2006, 2025):
        mlroot.join("R{}b".format(release)).join("bin").join("matlab.exe").ensure()
    # Yield the
    yield mlroot
    # Cleanup 
    tmpdir_factory.getbasetemp().remove()