#-*- coding: utf-8 -*-

"""
Exceptions
"""

class OutboundException(Exception):
    """
    Outbound bisection exception.
    
    This exception is raised 
    """
    def __repr__(self):
        return "Dichotomy returned an outbound exception."

class SQLBadURL(Exception):
    """
    Bad URL exception
    """
    def __init__(self):
        Exception.__init__(self)
        
    def __repr__(self):
        return '<SQLBadURL Exception>'

class Unavailable(Exception):
    """
    Feature is unavailable.
    """
    def __init__(self):
        Exception.__init__(self)
        
    def __repr__(self):
        return '<Unavailable Exception>'

class PluginMustOverride(Exception):
    """
    Developer must override
    """
    def __init__(self):
        Exception.__init__(self)
    def __repr__(self):
        return '<PluginMustOverride Exception>'


class SQLInvalidTargetParam(Exception):
    """
    Invalid target parameter
    """
    def __init__(self):
        Exception.__init__(self)
    def __repr__(self):
        return '<SQLInvalidTargetParam Exception>'


class UnknownField(Exception):
    """
    Unknown field specified
    """
    def __init__(self, field_name):
        Exception.__init__(self)
        self._field_name = field_name
    def __repr__(self):
        return '<UnknownField name="%s">' % self._field_name

