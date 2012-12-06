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

class Trigger:

    MODE_ERROR = 0
    MODE_SUCCESS = 1
    MODE_UNKNOWN = 2

    def __init__(self, mode=MODE_SUCCESS):
        self._mode = mode
        pass

    def is_error(self):
        """
        Determine if MODE_ERROR is set
        """
        return self._mode is Trigger.MODE_ERROR

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
    
    def __init__(self, status, *args, **kwargs):
        Trigger.__init__(self, *args, **kwargs)
        self._status = status

    def execute(self, response):
        """
        Check if status code is the one expected
        """
        return response.get_status() is self._status

class RegexpTrigger(Trigger):
    """
    Regexp-based trigger
    """
    
    def __init__(self, regexps, *args, **kwargs):
        """
        Constructor
        
        regexps: either a list of regexp or a string representing a regexp to match
        """
        Trigger.__init__(self, *args, **kwargs)
        self._regexps = []
        if isinstance(regexps, list):
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

