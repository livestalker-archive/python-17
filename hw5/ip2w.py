import urllib2
import json
import os
import re
from wsgiref.simple_server import make_server
from wsgiref.util import request_uri

IPINFO = 'http://ipinfo.io/{ip}'
OWM = 'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&lang={lang}&units=metric&APPID={app_id}'


class RequestException(Exception):
    pass


def handle(ip):
    if not is_ip_valid(ip):
        raise RequestException('IP address {} format error.'.format(ip))
    ip_info = get_ip_info(ip)
    bogon = ip_info.get('bogon', False)
    if bogon:
        raise RequestException('Requested ip is bogon.')
    app_id = os.environ.get('APPID', None)
    if not app_id:
        raise RequestException('No OpenWeatherMap API key.')
    lat, lon = parse_loc(ip_info)
    weather_info = get_weather(lat, lon, 'ru', app_id)
    return service_response(ip_info, weather_info)


def is_ip_valid(ip):
    ip_t = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
    ip_re = re.compile(ip_t)
    if ip_re.match(ip):
        return True
    else:
        return False


def get_weather(lat, lon, lang, app_id):
    req = urllib2.Request(OWM.format(lat=lat, lon=lon, lang=lang, app_id=app_id))
    req.add_header('Accept', 'application/json')
    try:
        res = urllib2.urlopen(req, None, 5)
        return json.loads(res.read())
    except urllib2.URLError as e:
        raise RequestException('External service error.')
    except ValueError as e:
        raise RequestException('External service format error.')


def get_ip_info(ip):
    req = urllib2.Request(IPINFO.format(ip=ip))
    req.add_header('Accept', 'application/json')
    try:
        res = urllib2.urlopen(req, None, 5)
        return json.loads(res.read())
    except urllib2.URLError as e:
        if e.code == 404:
            raise RequestException('IP address {} not found on external service.'.format(ip))
        raise RequestException('External service error.')
    except ValueError as e:
        raise RequestException('External service format error.')


def parse_loc(ip_info):
    lat, lon = ip_info['loc'].split(',')
    return lat, lon


def service_response(ip_info, weather_info):
    result = {
        'city': ip_info['city'],
        'temp': weather_info['main']['temp'],
        'conditions': weather_info['weather'][0]['description']
    }
    return result


def gen_400(message):
    status = '400 Bad Request'
    json_result = {
        'error': message
    }
    return status, json.dumps(json_result, ensure_ascii=False).encode('utf-8')


def application(environ, start_response):
    location = 'ip2w'

    url = request_uri(environ).rstrip('/')
    if location not in url:
        status, response = gen_400('Location does not supported.')
    else:
        try:
            status = '200 OK'
            ip = url.split('/')[-1]
            json_result = handle(ip)
            response = json.dumps(json_result, ensure_ascii=False).encode('utf-8')
        except RequestException as e:
            status, response = gen_400(e.message)

    headers = [
        ('Content-type', 'application/json; charset=utf-8'),
        ('Content-Length', str(len(response)))
    ]
    start_response(status, headers)
    return [response]


if __name__ == '__main__':
    httpd = make_server('localhost', 8080, application)
    print 'Start weather server...'
    httpd.serve_forever()
