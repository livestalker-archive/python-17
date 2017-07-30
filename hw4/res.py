import os
from time import strftime, gmtime

status_code = {
    '200': 'OK',
    '404': 'Not Found',
    '405': 'Method Not Allowed'
}
content_type = {
    '_text': 'text/plain',
    'html': 'text/html',
    'css': 'text/css',
    'js': 'application/javascript',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'swf': 'application/x-shockwave-flash'
}

CRLF = '\r\n'


def create_response(request, filename, data):
    return Response(request.version, '200', filename, data)


class Response(object):
    def __init__(self, version, code, filename, data):
        self.version = version
        self.code = code
        self.filename = filename
        self.data = data

    def get_status_line(self):
        return '{} {} {}\r\n'.format(self.version, self.code, status_code[self.code])

    def general_header(self):
        # https://tools.ietf.org/html/rfc2616#section-4.5
        # Date, Connection
        headers = {
            'Date': self._create_date(),
            'Connection': 'close'
        }
        return headers

    def response_header(self):
        # TODO hardcoded server name
        # https://tools.ietf.org/html/rfc2616#section-6.2
        # Server
        headers = {
            'Server': 'OTUS Web Server'
        }
        return headers

    def entity_header(self):
        # https://tools.ietf.org/html/rfc2616#section-7.1
        # Content-Length
        # Content-Type
        headers = {
            'Content-Length': len(self.data),
            'Content-Type': content_type['_text']
        }
        return headers

    def headers(self):
        result = []
        for k, v in self.general_header().items():
            result.append('{}: {}'.format(k, v))
        for k, v in self.response_header().items():
            result.append('{}: {}'.format(k, v))
        for k, v in self.entity_header().items():
            result.append('{}: {}'.format(k, v))
        return CRLF.join(result)

    def get_octets(self):
        octets = '{}{}{}{}'.format(self.get_status_line(),
                                   self.headers(),
                                   2 * CRLF,
                                   'Hello')
        return octets

    def _create_date(self):
        # TODO check format
        return strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
