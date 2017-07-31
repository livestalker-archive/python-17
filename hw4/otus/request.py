# -*- coding: utf-8 -*-
import os
import urllib
from .response import Response
from .utils import OK, FORBIDDEN, BAD_REQUEST, NOT_ALLOWED, NOT_FOUND, get_content_type

BUFFER_SIZE = 1024


def create_request(sock):
    """Create request object"""
    data = sock.recv(BUFFER_SIZE)
    return Request.parse(data)


class Request(object):
    """Request object represent parsed raw HTTP request."""

    def __init__(self, method, uri, version, headers):
        self.method = method
        self.uri = uri
        self.version = version
        self.headers = headers
        # Flag - if request valid.
        self.valid = False

    @staticmethod
    def parse(data):
        """Create Request object from raw data."""
        lines = data.splitlines()
        try:
            request_line = lines[0]
            method, uri, version = Request._parse_request_line(request_line)
            headers = {}
            for line in lines[1:]:
                if not line:
                    break
                k, v = Request._parse_header(line)
                headers[k] = v
            request = Request(method, uri, version, headers)
            request.valid = True
        except:
            request = Request(None, None, None, None)
        return request

    @staticmethod
    def _parse_request_line(line):
        """Parse request line.
        Format: Request-Line   = Method SP Request-URI SP HTTP-Version CRLF
        RFC: https://tools.ietf.org/html/rfc2616#section-5.1
        """
        parts = [el.strip() for el in line.split()]
        return parts[0], parts[1], parts[2]

    @staticmethod
    def _parse_header(line):
        """Parse header."""
        parts = [el.strip() for el in line.split(':')]
        return parts[0], parts[1]


class RequestHandler(object):
    """Class for handle requests."""
    ALLOWED_METHODS = {'GET', 'HEAD'}
    INDEX = 'index.html'

    def __init__(self, doc_root, request):
        self.request = request
        self.doc_root = doc_root
        self.filename = None

    def process(self):
        """Process request."""
        if not self.request.valid:
            return Response(None, BAD_REQUEST)
        if not self.is_method_allowed():
            return Response(self.request.method, NOT_ALLOWED)
        code = self._check_resource()
        if code != OK:
            return Response(self.request.method, code)
        data = self._read_file()
        response = Response(self.request.method, code)
        response.set_content_type(self._get_content_type())
        response.set_data(data)
        return response

    def _check_resource(self):
        """Check accessible resource in document root."""
        file_path = self.request.uri.split('?')[0].strip('/')
        file_path = urllib.unquote(file_path).decode('utf-8')
        filename = os.path.realpath(os.path.join(self.doc_root, file_path))
        longest_prefix = os.path.commonprefix([self.doc_root, filename])
        # check root escaping
        if longest_prefix != self.doc_root:
            return FORBIDDEN
        if os.path.isdir(filename):
            # if dir append index
            filename = os.path.join(filename, self.INDEX)
            possible_error = FORBIDDEN
        else:
            possible_error = NOT_FOUND
        if not os.path.exists(filename):
            return possible_error
        self.filename = filename
        return OK

    def _get_content_type(self):
        """Try detect content type."""
        return get_content_type(self.filename)

    def _read_file(self):
        """Read file."""
        with open(self.filename, mode='rb') as f:
            return f.read()

    def is_method_allowed(self):
        """Check if method is allowed."""
        return self.request.method in self.ALLOWED_METHODS

    def is_file_exists(self):
        """Check if file/dir exists."""
        return os.path.exists(self.filename)
