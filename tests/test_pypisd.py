from pypisd import __version__
import subprocess
from pypisd.main import cli

def test_version():
    assert __version__ == '0.1.0'

def test_pypisd():
    subprocess.run(["pypisd"], capture_output=True)