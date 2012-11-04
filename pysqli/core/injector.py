#-*- coding:utf-8 -*-

"""
This module implements the core injection components. Injection is performed
by 'injectors', dedicated to the SQL injection itself.

These injectors make the injection possible in every possible target: command
lines, HTTP requests, HTTP headers, ...

They only have to return a boolean result depending on the injected SQL code.

This module provides many injectors:
    
    HttpInjector
    GetInjector
    PostInjector
    CookieInjector
    UserAgentInjector
    CmdInjector
    
They can be used to inject into GET and POST requests, into cookies or user-
agent headers, and even in command line.
"""

import httplib
import urllib
import re
from subprocess import Popen, PIPE
from urlparse import urlparse, parse_qs
from triggers import RegexpTrigger, StatusTrigger, Trigger
from types import ListType, DictType


class Response(object):
    '''
    Default response class.
    
    This class is used to hold every response information:
        - status code 
        - response content
        
    It is used by triggers to determine the result of an injection (boolean)
    '''
    
    def __init__(self, status=-1, content=None):
        self._status = status
        self._content = content
        
    def get_status(self):
        '''
        Retrieve the response's status code
        '''
        return self._status

    def get_content(self):
        '''
        Retrieve the response content
        '''
        return self._content


class HttpResponse(Response):
    '''
    HTTP response (as returned by httplib)
    '''
    def __init__(self, response):
        '''
        Wrap an httplib HttpResponse into a compatible instance
        '''
        super(HttpResponse, self).__init__(response.status, response.read())
        self._response = response        
    
    def get_header(self, header):
        '''
        Retrieve a specific header
        '''
        return self._response.getheader(header)


class AbstractInjector(object):
    '''
    This is an bastract class representing an SQL injector.
    
    Basically, SQL injection exploitation is based on two steps:
        - parameter tampering
        - remote SQL injection
    
    The first one is achieved by this class. Second one is implemented
    as a method inherited classes must derive from. That is, you can use this
    absract class to basically inject wherever you want: cmdlines, HTTP
    requests, raw data, ...
    '''
    
    def __init__(self, parameters, target=None, smooth=False):
        '''
        parameters must be a dictionnary containg parameters as keys and
        their default values as values. 
        
        target specifies the parameter to use for the injection.
        smooth specifies the injection method (full replacement or
        inplace replacement)
        '''
        self._parameters = parameters
        self._target = target
        self._smooth = smooth
        self._trigger = None
    
    def set_parameters(self, parameters, target=None):
        '''
        Set parameters and optionally the target parameter.
        
        parameters: dict of parameters
        target: target parameter (default: None)
        '''
        self._parameters = parameters
        self._target = target
     
    def get_trigger(self):
        '''
        Retrieve trigger instance
        '''
        return self._trigger
        
    def set_trigger(self, trigger):
        '''
        Set default trigger
        
        trigger specifies the new trigger to use. see class Trigger.
        '''
        self._trigger = trigger

    def process_parameters(self, sql):
        '''
        Tamper target parameter given a specific mode: normal or smooth
        
        We do not care about what the injector does with these parameters,
        we tamper them as requested.
        '''
        if type(self._parameters) is DictType:
            tampered_params = {}
            # loop on all parameters
            for parameter in self._parameters:
                if parameter == self._target:
                    if self._smooth:
                        tampered_params[parameter] = self._parameters[parameter].replace('SQLHERE', sql)
                    else:
                        tampered_params[parameter] = sql
                else:
                    tampered_params[parameter] = self._parameters[parameter]
            return tampered_params
        elif type(self._parameters) is ListType:
            tampered_params = self._parameters
            if self._smooth:
                tampered_params[self._target] = self._parameters[self._target].replace('*', sql)
            else:
                tampered_params[self._target] = sql
            return tampered_params
        else:
            return self._parameters
    
    def process_injection(self, parameters):
        '''
        Inherited classes must implement their own injection routine here.
        '''
        raise 'MustBeOverriden'
    
    def inject(self, sql):
        '''
        The real injection method. This method relies on two other methods:
            - process_parameters
            - process_injection
        The first one modifies the parameters and the second one inject them.
        '''
        return self.process_injection(self.process_parameters(sql))


class ContextBasedInjector(AbstractInjector):
    '''
    Context-based injector. 
    
    This injector keeps a reference to the caller's context.
    '''
    
    def __init__(self, context):
        super(ContextBasedInjector, self).__init__(
            context.get_params(),
            context.get_target_param(),
            context.is_smooth()
        )
        self._context = context
        
    def get_context(self):
        '''
        Return the target context
        '''
        return self._context

    def process_response(self, response):
        '''
        Default response processing.
               
        This method processes the response, and execute the specified trigger
        to determine the result state (boolean). 
        
        Return None if inband mode is selected and nothing can be extracted.

        response: instance of Response or a child class representing the
            response of an injection.

        '''
        if self._context.is_blind():
            # if blind, ask the injector to return a boolean value
            if self._trigger.is_error():
                return (not self._trigger.execute(response))
            else:
                return self._trigger.execute(response)
        else:
            # if inband, check if we can extract some data
            result = re.search('%s(.*)%s' % (
                self._context.get_inband_tag(),
                self._context.get_inband_tag()
            ),response.get_content())
            if result:
                return result.group(1)
            else:
                return None
        
class HttpInjector(ContextBasedInjector):
    '''
    Default HTTP Injector. 
    
    This injector supports most of the HTTP methods, is able to set custom
    cookies and headers, and performs dynamic parameters tampering.
    '''
    
    def __init__(self, method, context):
        '''
        Constructor.
        
        Method specifies an HTTP method to use, context an injection context.
        '''
        super(HttpInjector, self).__init__(context)
        self._method = method

        # parse url
        self.set_url(self._context.get_url())
        
        # set default trigger
        self._trigger = RegexpTrigger(
            ['(error|unknown|illegal|warning|denied|subquery)'],
             mode=Trigger.MODE_ERROR
        )


    def set_url(self, url):
        '''
        Set the default URL to use for injection
        
        This causes the injector to re-parse the URL and reset some properties.
        '''
        # parse URL
        self._context.set_url(url)
        self._url = self._context.get_url()
        parsed_url = urlparse(self._url)
        if parsed_url.scheme == 'https' and not self._context.is_ssl():
            self._context.use_ssl(True)
            
        # rebuild our base url
        self._base_url = '%s://%s%s' % (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path
        )
        self._base_uri = parsed_url.path
        self._server = parsed_url.netloc
        
        # extract url parameters & fix the dictionnary
        if parsed_url.query != '':
            self._url_parameters = parse_qs(parsed_url.query)
            for param in self._url_parameters:
                self._url_parameters[param] = self._url_parameters[param][0]
        else:
            self._url_parameters = {}
            
    def get_url(self):
        '''
        Retrieve the URL
        '''
        return self._url
        
    def get_base_url(self):
        '''
        Retrieve the base URL (without query string)
        '''
        return self._base_url
        
    def get_base_uri(self):
        '''
        Retrieve the base URI (without query string)
        '''
        return self._base_uri
        
    def get_server(self):
        '''
        Retrieve server info as a string (server:port)
        '''
        return self._server
        
    def get_url_parameters(self):
        '''
        Get URL parameters (taken from query strings) as dict
        '''
        return self._url_parameters
        
    def set_url_parameters(self, parameters):
        '''
        Set URL parameters.
        
        parameters is a dict containing the new parameters. Use this with
        care, because concurrent accesses are made by the asynchronous workers
        and may alter reliability.
        '''
        self._url_parameters = parameters

    def build_uri(self, parameters):
        '''
        Build URI
        
        Override this method if you have to encode a URL parameter or somethg
        like this.
        '''
        return self.get_base_uri() + '?'+urllib.urlencode(self._url_parameters)

    def process_injection(self, parameters, data=None,
                          content_type=None, headers=None):
        '''
        Do the HTTP request, and execute trigger.execute
        
        In this default impl., parameters is not used. Override this
        to change behavior.
        '''
        # use ssl ?
        if self._context.use_ssl():
            request = httplib.HTTPSConnection(self._server)
        else:
            request = httplib.HTTPConnection(self._server)
        
        # create the request
        request.putrequest(self._method, self.build_uri(parameters))
        if data is not None:
            request.putheader('Content-Length', str(len(data)))
        if content_type is not None:
            request.putheader('Content-Type', content_type)
            
        # handle headers
        _headers = {}
        # load context headers first
        if self._context.has_headers():
            for header, value in self._context.get_headers().items:
                _headers[header] = value
        # overrides with headers if provided
        if headers:
            for header, value in headers:
                _headers[header,] = value
        # eventually set request headers
        for header, value in _headers:
            request.putheader(header, value)
        # if cookie set it
        if self._context.get_cookie() is not None:
            request.putheader('Cookie', self._context.get_cookie())
        request.endheaders()
        
        # perform
        if data is not None:
            request.send(data)
        response = request.getresponse()
        
        # execute trigger
        return self.process_response(HttpResponse(response))

        
class GetInjector(HttpInjector):
    '''
    Basic HTTP GET injector
    '''
    def __init__(self, context):
        HttpInjector.__init__(self, 'GET', context)
    
    def build_uri(self, parameters):
        '''
        Overrides URL parameters with tampered ones
        '''
        return self.get_base_uri() + '?'+urllib.urlencode(parameters)
    
class PostInjector(HttpInjector):
    '''
    Basic HTTP POST injector
    '''
    def __init__(self, context):
        super(PostInjector, self).__init__('POST', context)
        
    def process_injection(self, parameters):
        '''
        Serialize tampered data and inject them as form values
        '''
        # create data from modified parameters
        data = urllib.urlencode(parameters)
        return super(PostInjector, self).process_injection(
            parameters,
            data=data,
            content_type='application/x-www-form-urlencoded'
        )

class UserAgentInjector(HttpInjector):
    '''
    Basic HTTP User-Agent header injector
    '''
    def __init__(self, method, context, data=None, content_type=None):
        '''
        Constructor
        
        Add a default target parameter 'user-agent'.
        '''
        super(UserAgentInjector, self).__init__(method, context)
        self.set_parameters({'user-agent':''}, 'user-agent')
        self._data = data
        self._content_type = content_type
    
    def process_injection(self, parameters):
        '''
        Inject into our context the new header. 
        '''
        # get magic 'user-agent' parameter
        self.get_context().set_header('User-Agent', parameters['user-agent'])
        return super(UserAgentInjector, self).process_injection(parameters)
        
        
class CookieInjector(HttpInjector):
    '''
    Cookie-based SQL injector.
    
    Use this injector if you want to inject into a cookie param.
    Supports post data, url parameters, and other headers.
    '''
    def __init__(self, method, context, data=None, content_type=None):
        super(CookieInjector, self).__init__(method, context)
        self._data = data
        self._content_type = content_type
        
    def assemble_cookie(self, parameters):
        '''
        Build the cookie
        '''
        return '; '.join(['%s=%s' % k for k in parameters.items()])
        
    def process_injection(self, parameters):
        '''
        Create on-demand headers containing the injected string
        '''
        return super(CookieInjector, self).process_injection(
            parameters,
            data=self._data,
            content_type=self._content_type,
            headers={
                'User-Agent':self.assemble_cookie(parameters)
            }
        )


class CmdInjector(ContextBasedInjector):
    '''
    Command injector
    
    This injector should be used to inject SQL into a cmdline. Popen does not
    support multi-threading, which is disabled.
    '''
    
    def __init__(self, context):
        '''
        Constructor.
        
        Set up the lock and our default trigger (based on return code)
        '''
        super(CmdInjector, self).__init__(context)
        self._context = context
        
        # disable multi-threading
        self._context.set_multithread(False)
        
        # set default trigger
        self.set_trigger(StatusTrigger(0, mode=Trigger.MODE_SUCCESS))

    def process_injection(self, parameters):
        '''
        The real injection method.
        
        Launch the subprocess, and release the lock. Process the response.
        '''
        # launch process using Popen
        result = Popen(parameters, stdout=PIPE)
        content = result.communicate()[0]
        return self.process_response(Response(result.returncode, content))
 
