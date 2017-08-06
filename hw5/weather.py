import urllib2
import json
import os
from wsgiref.simple_server import make_server

IPINFO = 'http://ipinfo.io/{ip}'
OWM = 'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&lang={lang}&APPID={app_id}'


def handle(ip):
    ip_info = get_ip_info(ip)
    app_id = os.environ.get('APPID')
    lat, lon = parse_loc(ip_info)
    weather_info = get_weather(lat, lon, 'ru', app_id)
    return service_response(ip_info, weather_info)


def get_weather(lat, lon, lang, app_id):
    req = urllib2.Request(OWM.format(lat=lat, lon=lon, lang=lang, app_id=app_id))
    req.add_header('Accept', 'application/json')
    try:
        res = urllib2.urlopen(req, None, 5)
        return json.loads(res.read())
    except urllib2.URLError as e:
        # TODO re-raise
        pass
    except ValueError as e:
        # TODO re-raise
        pass


def get_ip_info(ip):
    req = urllib2.Request(IPINFO.format(ip=ip))
    req.add_header('Accept', 'application/json')
    try:
        res = urllib2.urlopen(req, None, 5)
        return json.loads(res.read())
    except urllib2.URLError as e:
        # TODO re-raise
        pass
    except ValueError as e:
        # TODO re-raise
        pass


def parse_loc(ip_info):
    # TODO if key does not exists
    lat, lon = ip_info['loc'].split(',')
    return lat, lon


def service_response(ip_info, weather_info):
    result = {
        'city': ip_info['city'],
        'temp': weather_info['main']['temp'],
        'conditions': weather_info['weather'][0]['description']
    }
    return result


def weather_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=utf-8')]

    start_response(status, headers)
    json_result = handle('8.8.8.8')
    response = json.dumps(json_result, ensure_ascii=False).encode('utf-8')
    return [response]


if __name__ == '__main__':
    httpd = make_server('localhost', 8080, weather_app)
    print 'Start weather server...'
    httpd.serve_forever()
