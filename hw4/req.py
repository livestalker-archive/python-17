def create_request(s):
    # TODO small buffer recv in loop
    # man recv
    data = s.recv(4096)
    return parse_data(data)


def parse_data(data):
    # Request = Request - Line;
    #          *(general - header;
    #           |request - header;
    #           |entity - header );
    #           CRLF
    #           [message - body];
    # Request-Line   = Method SP Request-URI SP HTTP-Version CRLF
    lines = data.splitlines()
    # TODO IndexError
    request_line = lines[0]
    method, uri, version = parse_request_line(request_line)
    headers = {}
    for line in lines[1:]:
        if not line:
            break
        k, v = parse_header(line)
        headers[k] = v
    return Request(method, uri, version, headers)


def parse_request_line(line):
    # TODO invalid request line
    parts = [el.strip() for el in line.split()]
    return parts[0], parts[1], parts[2]


def parse_header(line):
    # TODO invalid headers
    parts = [el.strip() for el in line.split(':')]
    return parts[0], parts[1]


class Request(object):
    def __init__(self, method, uri, version, headers):
        self.method = method
        self.uri = uri
        self.version = version
        self.headers = headers
