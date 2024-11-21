# read version from installed package
from importlib.metadata import version

try:
    __version__ = version("a2")
except:
    __version__ = "0.0.1"  # Default version for development/testing
