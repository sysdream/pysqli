#-*- coding: utf-8 -*-

"""
This module contains the following classes:
    
    Context
    InbandContext
    BlindContext
    
A context represents a set of conditions required to perform correctly
an SQL injection. 

"""

from random import choice

class Context:
    
    """
    Context class
    
    This class is used to store every info related to the injection context.
    """
    
    FIELD_STR = 'string'
    FIELD_INT = 'int'
    INBAND = 'inband'
    BLIND = 'blind'
    
    def __init__(self, method=INBAND, field_type=FIELD_STR, url='', \
        params=None, target=None, comment='/*', strdelim="'", union_tag=None,\
        union_fields=[], default='0', union_target=-1, use_ssl=False, \
        smooth=False, headers=None, cookie=None, multithread=True, \
        truncate=False,encode_str=False):
        
        '''
        Default injection context constructor.
        '''
        
        # injection method
        self.__method = method
        self.__url = url
        self.__params = params
        self.__target = target
        self.__comment = comment
        self.__str_delim = strdelim
        self.__default = default
        self.__use_ssl = use_ssl
        self.__encode_str = encode_str
        self.__truncate = truncate
        self.__field_type = field_type
        self.__smooth = smooth
        self.__headers = headers
        self.__cookie = cookie
        self.__multithread = multithread
        
        # inband specific 
        self.__union_fields = union_fields
        self.__union_target = union_target
        if union_tag is not None:
            self.__union_tag = union_tag
        else:
            self.__union_tag = ''.join([choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(32)])
        
    def get_url(self):
        """
        Returns the target URL
        """
        return self.__url


    def set_url(self, url):
        """
        Set the target URL
        """
        self.__url = url

    ## Set vulnerable field type
    # @param field_type Field type, must be either FIELD_STR or FIELD_INT
        
    def set_field_type(self, field_type):
        """
        Set field type (FIELD_INT or FIELD_STR)
        """
        self.__field_type = field_type

    ## Get vulnerable field type
    # @return Vulnerable field type (FIELD_INT or FIELD_STR)
    
    def get_field_type(self):
        """
        Get field type (FIELD_INT or FIELD_STR)
        """
        return self.__field_type
        
    ## Enable SQL string encvoding
    # Enable SQL string encoding to evade anti-quote functions or WAF
    
    def enable_string_encoding(self, enabled):
        """
        Enable/disable string encoding.
        """
        self.__encode_str = enabled

    ## Enable SQL query truncation
    # If enabled, comment out the rest of the SQL query
        
    def enable_truncate(self, enabled):
        """
        Enable/disable request truncate.
        """
        self.__truncate = enabled
        
    ## Check if context asks for query truncating        
    # @return True if query truncation is enabled, False otherwise    
    def require_truncate(self):
        """
        Retrieve request truncation requirement.
        """
        return self.__truncate
        
    ## Check if string encoding is required        
    # @return True if string encoding is required, False otherwise
    
    def require_string_encoding(self):
        """
        Determine if string encoding is required or not.
        """
        return self.__encode_str        
        
    ## Enable SSL support
    # @param enabled True to enable, False to disable
    
    def enable_ssl(self, enabled):
        """
        Enable/disable SSL support.
        """
        self.__use_ssl = enabled

    ## Check if SSL is required
    # @return True if SSL is required, False otherwise
    
    def use_ssl(self):
        """
        Return True if SSL must be used, False otherwise.
        """
        return self.__use_ssl        


    def set_smooth(self, enabled=True):
        """
        Enable/disable smooth mode
        """
        self.__smooth = enabled

    def is_smooth(self):
        """
        Determine if smooth must be used or not.
        """
        return self.__smooth
        
    def set_multithread(self, enabled=True):
        """
        Enable/disable multithreading.
        """
        self.__multithread = enabled
        
    def is_multithread(self):
        """
        Determine if multithreading must be used or not.
        """
        return self.__multithread

    def has_headers(self):
        """
        Determine if extra headers must be used
        """
        return (self.__headers is not None)

    def set_headers(self, headers):
        """
        Set extra headers.Headers
        
        headers: dict of extra headers (mostly HTTP)
        """
        self.__headers = headers

    def set_header(self, header, value):
        """
        Set a given header
        
        header: header name (string)
        value: header value (usually, string)
        """
        if self.__headers is not None:
            self.__headers[header] = value
        else:
            self.__headers = {}
            self.__headers[header] = value

    def get_headers(self):
        """
        Get all headers
        """
        return self.__headers

    def set_cookie(self, cookie):
        """
        Set HTTP cookie.
        
        cookie: cookie value. 
        """
        self.__cookie = cookie

    def get_cookie(self):
        """
        Get cookie.
        """
        return self.__cookie

    def set_params(self, params, target=None):
        """
        Set parameters and target parameter.
        
        params: dict of parameters
        target: target parameter
        """
        self.__params = params
        self.__target = target
        
    def get_params(self):
        """
        Retrieve parameters.
        """
        return self.__params

    def get_target_param(self):
        """
        Retrieve the target parameter
        """
        return self.__target    
    
    def get_comment(self):
        """
        Get comment sequence
        """
        return self.__comment    

    def set_comment(self, comment):
        """
        Set comment seqence
        """
        self.__comment = comment

    def get_string_delimiter(self):
        """
        Retrieve string delimiter
        """
        return self.__str_delim
    
    def set_string_delimiter(self, delim):
        """
        Set string delimiter
        
        delim: string delimiter
        """
        self.__str_delim = delim
        
    def set_default_value(self, default):
        """
        Set default value to use in the SQL code
        
        default: default value (string in case of FIELD_STR,
                    int in case of FIELD_INT)
        """
        self.__default = default

    def get_default_value(self):
        """
        Retrieve default value
        """
        return self.__default
        
    def set_inband_fields(self, fields):
        """
        Set inband fields
        
        Inband fields are quite special: they are described with a single string
        with these possible caracters:
            - s: specify a string field
            - i: specify an integer field
        
        This is used to be compliant with Oracle, Mssql, and other DBMS. 
        
        Example:
            
            context.set_inband_fields('sssisi')
        
        declares 6 fields, [string, string, string, integer, string, integer]
        """
        self.__union_fields = fields
    
    def get_inband_fields(self):
        """
        Retrieve inband fields types
        """
        return self.__union_fields
    
    def get_inband_tag(self):
        """
        Get inband tag
        
        The inband tag is a string used to wrap the extracted string in order
        to extract it easily. This tag is randomly generated when an instance
        of the Context class is created.
        """
        return self.__union_tag
    
    def set_inband_target(self, target):
        """
        Sets inband target field index
        """
        self.__union_target = int(target)

    def get_inband_target(self):
        """
        Retrieve inband target field index
        """
        return self.__union_target

    def is_blind(self):
        """
        Determines if the actual injection context is blind
        """
        return (self.__method==Context.BLIND)

    def is_inband(self):
        """
        Determines if the actual injection context is inband
        """
        return (self.__method==Context.INBAND)

    def in_string(self):
        """
        Determines if the target field is a string
        """
        return (self.__field_type==Context.FIELD_STR)
    
    def in_int(self):
        """
        Determines if the target field is an int
        """
        return (self.__field_type==Context.FIELD_INT)

    def use_blind(self):
        """
        Switch to blind injection
        """
        self.__method = Context.BLIND

    def use_inband(self):
        """
        Switch to inband injection
        """
        self.__method = Context.INBAND


class InbandContext(Context):
    """
    Inband injection context
    """
    
    def __init__(self, **kwargs):
        kwargs['method'] = Context.INBAND
        Context.__init__(self, **kwargs)
        
class BlindContext(Context):
    """
    Blind injection context
    """
    
    def __init__(self, **kwargs):
        kwargs['method'] = Context.BLIND
        Context.__init__(self, **kwargs)
