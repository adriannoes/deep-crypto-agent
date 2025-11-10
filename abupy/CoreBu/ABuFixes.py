# -*- encoding:utf-8 -*-
"""
Compatibility fixes for Python 2/3 and common utilities.
"""
from __future__ import absolute_import

import six
from concurrent.futures import ThreadPoolExecutor
from functools import partial, reduce
import pickle
from inspect import signature, Parameter

# Re-export six for compatibility
__all__ = ['six', 'ThreadPoolExecutor', 'signature', 'Parameter', 
           'zip', 'xrange', 'range', 'reduce', 'map', 'filter',
           'pickle', 'Pickler', 'Unpickler', 'partial']

# Python 2/3 compatibility
try:
    from builtins import zip, range, map, filter
except ImportError:
    # Python 2
    from __builtin__ import zip, xrange as range, map, filter

try:
    from pickle import Pickler, Unpickler
except ImportError:
    from pickle import Pickler, Unpickler

# For Python 2 compatibility
try:
    xrange = xrange
except NameError:
    xrange = range

