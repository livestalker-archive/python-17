from time import strftime, gmtime
from .utils import CRLF, STATUS_CODES


class Response(object):
    def __init__(self, version, code):
        self.version = version
        self.code = code
        self.headers = {}
        self._general_header()
        self._response_header()
        self.data = None

    def set_data(self, data):
        # https://tools.ietf.org/html/rfc2616#section-7.1
        self.data = data
        self.headers['Content-Length'] = len(data)

    def set_content_type(self, ct):
        # https://tools.ietf.org/html/rfc2616#section-7.1
        self.headers['Content-Type'] = ct

    def get_octets(self):
        return '{}{}{}{}'.format(self._get_status_line(),
                                 self._get_headers(),
                                 2 * CRLF,
                                 self.data)

    def _create_date(self):
        # TODO check format
        return strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    def _general_header(self):
        # https://tools.ietf.org/html/rfc2616#section-4.5
        self.headers['Date'] = self._create_date()
        self.headers['Connection'] = 'close'

    def _response_header(self):
        # https://tools.ietf.org/html/rfc2616#section-6.2
        self.headers['Server'] = 'OTUS Web Server'

    def _get_status_line(self):
        return '{} {} {}\r\n'.format(self.version, self.code, STATUS_CODES[self.code])

    def _get_headers(self):
        return CRLF.join('{}: {}'.format(k, v) for k, v in self.headers.items())
