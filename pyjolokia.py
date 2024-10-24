#!/usr/bin/python3

# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json

try:
    import urllib2 as urllib
except ImportError:
    import urllib.request
#    import urllib.parse
#    import urllib.error

try:
    from urllib.request import Request
except ImportError:
    from urllib.request import Request
try:
    from urllib.request import urlopen
except ImportError:
    from urllib.request import urlopen

import base64


class Jolokia:
    '''
        pyJolokia class Jolokia is a JSON featching python class.
        It uses urllib2 and json or simplejson to do post requests
        to a jolokia URL. Then returns back a python dictionary.

        .. code-block:: python

            j4p = Jolokia('http://localhost:9199/jolokia/')
            j4p.request(type = 'read', mbean = 'java.lang:type=Threading',
                        attribute = 'ThreadCount' )
            >> { 'status' : 200, ...
    '''

    def __init__(self, url, **kwargs):
        """
        """
        self.url = url
        self.data = None
        self.proxy_config = {}
        self.auth_config = {}
        self.req_config = {}
        self.req_target = {}

        self.timeout = kwargs.get('timeout', 10)

    def auth(self, **kwargs):
        '''
            Used to add auth info if using jolokia via http to access the jmx

            example

            .. code-block:: python

                j4p.auth(httpusername='user',httppassword='password')

        '''
        self.auth_config['auth'] = {}
        if 'httpusername' in kwargs:
            self.auth_config['auth']['username'] = kwargs.get('httpusername')
        if 'httppassword' in kwargs:
            self.auth_config['auth']['password'] = kwargs.get('httppassword')

    def config(self, **kwargs):
        '''
            Used to set configuration options for the request
            see: http://www.jolokia.org/reference/html/protocol.html#processing-parameters

            example

            .. code-block:: python

                j4p.config(ignoreErrors=True)
        '''
        if kwargs is not None:
            for key, value in kwargs.items():
                self.req_config[key] = value

    def target(self, **kwargs):
        '''
            Used to set configuration options for the request
            see: http://www.jolokia.org/reference/html/protocol.html#processing-parameters

            example

            .. code-block:: python

                j4p.target('service:jmx:rmi:///jndi/rmi://localhost:{}/jmxrmi' . format(8099))
        '''
        if kwargs is not None:
            for key, value in list(kwargs.items()):
                self.req_target[key] = value

    def proxy(self, url, **kwargs):
        '''
            Used to add proxy info if using jolokia as a proxy to other
            java jmx apps.

            example

            .. code-block:: python

                j4p.proxy('service:jmx:rmi://somehost:1234/some.mbean.server',
                           user = 'cwood',
                           password = 'somePassword')

        '''
        self.proxy_config['target'] = {}
        self.proxy_config['target']['url'] = url
        if 'user' in kwargs:
            self.proxy_config['target']['user'] = kwargs.get('user')
        if 'password' in kwargs:
            self.proxy_config['target']['password'] = kwargs.get('password')

    def __get_json(self):
        """
        """
        if isinstance(self.data, dict):
            main_request = self.data.copy()
            main_request.update(self.proxy_config)
        else:
            main_request = []
            for request in self.data:
                request = request.copy()
                request.update(self.proxy_config)
                main_request.append(request)

        jdata = json.dumps(main_request).encode('utf-8')

        authheader = None

        if self.auth_config:

            if self.auth_config['auth']['username'] and self.auth_config['auth']['password']:

                authheader = base64.standard_b64encode(
                    (
                        f"{self.auth_config['auth']['username']}"
                        f":{self.auth_config['auth']['password']}"
                    ).encode()
                ).decode()

        response_stream = None

        try:
            request = Request(self.url, jdata,
                              {'content-type': 'application/json'})

            if authheader:
                request.add_header("Authorization", 'Basic ' + authheader)

            response_stream = urlopen(request, timeout=self.timeout)
            json_data = response_stream.read()

        except Exception as error:
            raise JolokiaError(f"Could not connect. Got error {error}")
        finally:
            if response_stream is not None:
                response_stream.close()

        try:
            python_dict = json.loads(json_data.decode())
        except Exception as error:
            raise JolokiaError(
                f"Could not decode into json. \
                Is Jolokia running at {self.url}. \
                Got error {error}.")
        return python_dict

    def __mkrequest(self, req_type, **kwargs):
        """
        """
        new_request = {}
        new_request['type'] = req_type
        new_request['config'] = self.req_config
        new_request['target'] = self.req_target

        if type != 'list':
            new_request['mbean'] = kwargs.get('mbean')
        else:
            new_request['path'] = kwargs.get('path')

        if type == 'read':
            new_request['attribute'] = kwargs.get('attribute')
            new_request['path'] = kwargs.get('path')
        elif type == 'write':
            new_request['attribute'] = kwargs.get('attribute', '')
            new_request['value'] = kwargs.get('value', '')
            new_request['path'] = kwargs.get('path', '')
        elif type == 'exec':
            new_request['operation'] = kwargs.get('operation')
            new_request['arguments'] = kwargs.get('arguments')
        return new_request

    def request(self, req_type, **kwargs):
        """
        """
        if not isinstance(self.data, dict):
            self.data = {}
        self.data = self.__mkrequest(req_type, **kwargs)
        response = self.__get_json()
        return response

    def add_request(self, req_type, **kwargs):
        """
        """
        new_response = self.__mkrequest(req_type, **kwargs)
        if not isinstance(self.data, list):
            self.data = []
        self.data.append(new_response)

    def clear_requests(self):
        """
        """
        self.data = {}

    def get_requests(self):
        """
        """
        response = self.__get_json()
        return response


class JolokiaError(Exception):
    """
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
