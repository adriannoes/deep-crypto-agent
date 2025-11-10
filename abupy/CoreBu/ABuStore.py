# -*- encoding:utf-8 -*-
"""
Storage utilities for ABU results.
"""
from __future__ import absolute_import
from collections import namedtuple
from enum import Enum

class EStoreAbu(Enum):
    """Storage types for ABU results"""
    E_STORE_NORMAL = "normal"
    E_STORE_CUSTOM_NAME = "custom_name"

AbuResultTuple = namedtuple('AbuResultTuple', 
                           ['orders_pd', 'action_pd', 'capital', 'benchmark'])

def store_abu_result_tuple(abu_result_tuple, n_folds=None, store_type=EStoreAbu.E_STORE_NORMAL, custom_name=None):
    """Store ABU result tuple"""
    # Placeholder implementation
    pass

def load_abu_result_tuple(n_folds=None, store_type=EStoreAbu.E_STORE_NORMAL, custom_name=None):
    """Load ABU result tuple"""
    # Placeholder implementation
    return None

__all__ = ['AbuResultTuple', 'EStoreAbu', 'store_abu_result_tuple', 'load_abu_result_tuple']

