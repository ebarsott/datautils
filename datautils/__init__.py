#!/usr/bin/env python

import warnings

from . import ddict
from .import grouping
from . import structure
from . import qfilter

# get some useful functions
from .listify import listify
from .qfilter import qf
from .rmap import remap

__version__ = '1.0.2'
__all__ = [
    'ddict', 'grouping', 'listify', 'structure', 'qf', 'qfilter', 'remap']

try:
    from .import mongo
except ImportError as E:
    warnings.warn('datautils.mongo failed to import with: %s' % E)

try:
    from .import np
    from .np import mask_array
    __all__.append('mask_array')
except ImportError as E:
    warnings.warn('datautils.np failed to import with: %S' % E)


try:
    import plot
    __all__.append('plot')
except ImportError as E:
    warnings.warn('datautils.plot failed to import with: %S' % E)
