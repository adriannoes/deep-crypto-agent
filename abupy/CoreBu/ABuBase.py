# -*- encoding:utf-8 -*-
"""
Base classes for ABU system components.
"""
from __future__ import absolute_import

class AbuParamBase(object):
    """Base class for parameter objects"""
    pass

class FreezeAttrMixin(object):
    """Mixin to freeze attributes after initialization"""
    _frozen = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._frozen = True
    
    def __setattr__(self, key, value):
        if self._frozen and not hasattr(self, key):
            raise AttributeError(f"Cannot set attribute {key} on frozen object")
        super().__setattr__(key, value)

class PickleStateMixin(object):
    """Mixin for pickle state management"""
    pass

__all__ = ['AbuParamBase', 'FreezeAttrMixin', 'PickleStateMixin']

