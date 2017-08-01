# -*- coding: utf-8 -*-
from time import strftime, gmtime
from .utils import CRLF, STATUS_CODES


class Response(object):
    """Response class represent HTTP response."""
    def __init__(self, method, code):
        self.version = 'HTTP/1.1'
        self.method = method
        self.code = code
        self.headers = {}
        # set general headers (in hw: Date, Connection)
        # rfc: https://tools.ietf.org/html/rfc2616#section-4.5
        self._general_header()
        # set response headers (in hw: Server)
        # rfc: https://tools.ietf.org/html/rfc2616#section-6.2
        self._response_header()
        self.data = None

    def set_data(self, data):
        """Set data and set Content-Length header.
        rfc: https://tools.ietf.org/html/rfc2616#section-14.13
        """
        self.data = data
        self.headers['Content-Length'] = len(data)

    def set_content_type(self, ct):
        """Set Content-Type header.
        rfc: https://tools.ietf.org/html/rfc2616#section-14.17
        """
        self.headers['Content-Type'] = ct

    def get_octets(self):
        """Get octets of Response."""
        if self.method == 'GET':
            return '{}{}{}{}'.format(self._get_status_line(),
                                     self._get_headers(),
                                     2 * CRLF,
                                     self.data)
        else:
            return '{}{}{}'.format(self._get_status_line(),
                                   self._get_headers(),
                                   2 * CRLF)

    def _create_date(self):
        """Create Date header value.
        rfc: https://tools.ietf.org/html/rfc2616#section-3.3
        """
        return strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())

    def _general_header(self):
        """Set general headers."""
        self.headers['Date'] = self._create_date()
        self.headers['Connection'] = 'close'

    def _response_header(self):
        """Set response headers."""
        self.headers['Server'] = 'OTUS Web Server'

    def _get_status_line(self):
        """Create status line.
        rfc: https://tools.ietf.org/html/rfc2616#section-6.1
        """
        return '{} {} {}\r\n'.format(self.version, self.code, STATUS_CODES[self.code])

    def _get_headers(self):
        """Join headers."""
        return CRLF.join('{}: {}'.format(k, v) for k, v in self.headers.items())
