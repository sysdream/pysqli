#-*- coding: utf-8 -*-

"""
Triggers are used in conjunction with injectors to determine the result
of an injection.

This module provides a default class (Trigger) and two other classes implement-
ing status-based triggering and regexp-based triggering.

Two modes are available: MODE_ERROR and MODE_SUCCESS.MODE_ERROR must be used
with triggers detecting errors, while MODE_SUCCESS must be used with triggers
detecting success answers. 

Note that PySQLi exploitation engine is based on conditional errors (when
the tested condition is false)

classes:
    
    Trigger (default trigger)
    StatusTrigger (status-based trigger)
    RegexpTrigger (regexp-based trigger)

"""

import re
from types import ListType

class Trigger:

    MODE_ERROR = 0
    MODE_SUCCESS = 1
    MODE_UNKOWN = 2

    def __init__(self, mode=MODE_SUCCESS):
        self._mode = mode
        pass

    def is_error(self):
        """
        Determine if MODE_ERROR is set
        """
        return (self._mode == Trigger.MODE_ERROR)

    def get_mode(self):
        """
        Retrieve the mode
        """
        return self._mode

    def set_mode(self, mode):
        """
        Set mode
        """
        self._mode = mode
    
    def execute(self, response):
        """
        Process response
        """
        return None


class StatusTrigger(Trigger):
    """
    Status-based trigger
    """
    
    def __init__(self, status, *args, **kargs):
        Trigger.__init__(self, *args, **kargs)
        self._status = status

    def execute(self, response):
        """
        Check if status code is the one expected
        """
        return (response.get_status() == self._status)

class RegexpTrigger(Trigger):
    """
    Regexp-bvased trigger
    """
    
    def __init__(self, regexps, *args, **kargs):
        """
        Constructor
        
        regexps: either a list of regexp or a string representing a regexp to match
        """
        Trigger.__init__(self, *args, **kargs)
        self._regexps = []
        if type(regexps) is ListType:
            for regexp in regexps:
                self._regexps.append(re.compile(regexp, re.I|re.MULTILINE))
        else:
            self._regexps=[re.compile(regexps)]

    def execute(self, response):
        """
        Process response
        
        Loop on every regexp and if one matches then returns True.
        """
        content = response.get_content()
        for regexp in self._regexps:
            if regexp.search(content):
                return True
        return False

