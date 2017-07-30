import os
from .response import Response
from .utils import OK, NOT_ALLOWED, NOT_FOUND, get_content_type

BUFFER_SIZE = 4096


def create_request(sock):
    data = sock.recv(BUFFER_SIZE)
    return Request.parse(data)


class Request(object):
    def __init__(self, method, uri, version, headers):
        self.method = method
        self.uri = uri
        self.version = version
        self.headers = headers

    @staticmethod
    def parse(data):
        lines = data.splitlines()
        # TODO IndexError
        request_line = lines[0]
        method, uri, version = Request._parse_request_line(request_line)
        headers = {}
        for line in lines[1:]:
            if not line:
                break
            k, v = Request._parse_header(line)
            headers[k] = v
        return Request(method, uri, version, headers)

    @staticmethod
    def _parse_request_line(line):
        # TODO invalid request line
        parts = [el.strip() for el in line.split()]
        return parts[0], parts[1], parts[2]

    @staticmethod
    def _parse_header(line):
        # TODO invalid headers
        parts = [el.strip() for el in line.split(':')]
        return parts[0], parts[1]


class RequestHandler(object):
    ALLOWED_METHODS = {'GET', 'HEAD'}
    INDEX = 'index.html'

    def __init__(self, doc_root, request):
        self.request = request
        self.doc_root = doc_root
        self.filename = self._get_filename()

    def process(self):
        if not self.is_method_allowed():
            return Response(self.request.version, NOT_ALLOWED)
        if not self.is_file_exists():
            return Response(self.request.version, NOT_FOUND)
        data = self._read_file()
        response = Response(self.request.version, OK)
        response.set_content_type(self._get_content_type())
        response.set_data(data)
        return response

    def _get_filename(self):
        # Improve security
        filename = os.path.join(self.doc_root, self.request.uri.strip('/'))
        if os.path.isdir(filename):
            filename = os.path.join(filename, self.INDEX)
        return filename

    def _get_content_type(self):
        return get_content_type(self.filename)

    def _read_file(self):
        with open(self.filename, mode='rb') as f:
            return f.read()

    def is_method_allowed(self):
        return self.request.method in self.ALLOWED_METHODS

    def is_file_exists(self):
        return os.path.exists(self.filename)
