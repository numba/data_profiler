from .profile import *
from .pstats import *
from .display import plot

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
