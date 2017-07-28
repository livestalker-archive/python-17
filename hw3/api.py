#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Нужно реализовать простое HTTP API сервиса скоринга. Шаблон уже есть в api.py, тесты в test.py.
# API необычно тем, что пользователь дергают методы POST запросами. Чтобы получить результат
# пользователь отправляет в POST запросе валидный JSON определенного формата на локейшн /method

# Структура json-запроса:

# {"account": "<имя компании партнера>", "login": "<имя пользователя>", "method": "<имя метода>",
#  "token": "<аутентификационный токен>", "arguments": {<словарь с аргументами вызываемого метода>}}

# account - строка, опционально, может быть пустым
# login - строка, обязательно, может быть пустым
# method - строка, обязательно, может быть пустым
# token - строка, обязательно, может быть пустым
# arguments - словарь (объект в терминах json), обязательно, может быть пустым

# Валидация:
# запрос валиден, если валидны все поля по отдельности

# Структура ответа:
# {"code": <числовой код>, "response": {<ответ вызываемого метода>}}
# {"code": <числовой код>, "error": {<сообщение об ошибке>}}

# Аутентификация:
# смотри check_auth в шаблоне. В случае если не пройдена, нужно возвращать
# {"code": 403, "error": "Forbidden"}

# Метод online_score.
# Аргументы:
# phone - строка или число, длиной 11, начинается с 7, опционально, может быть пустым
# email - строка, в которой есть @, опционально, может быть пустым
# first_name - строка, опционально, может быть пустым
# last_name - строка, опционально, может быть пустым
# birthday - дата в формате DD.MM.YYYY, с которой прошло не больше 70 лет, опционально, может быть пустым
# gender - число 0, 1 или 2, опционально, может быть пустым

# Валидация аругементов:
# аргументы валидны, если валидны все поля по отдельности и если присутсвует хоть одна пара
# phone-email, first name-last name, gender-birthday с непустыми значениями.

# Контекст
# в словарь контекста должна прописываться запись  "has" - список полей,
# которые были не пустые для данного запроса

# Ответ:
# в ответ выдается произвольное число, которое больше или равно 0
# {"score": <число>}
# или если запрос пришел от валидного пользователя admin
# {"score": 42}
# или если произошла ошибка валидации
# {"code": 422, "error": "<сообщение о том какое поле невалидно>"}

# $ curl -X POST  -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав", "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}' http://127.0.0.1:8080/method/
# -> {"code": 200, "response": {"score": 5.0}}

# Метод clients_interests.
# Аргументы:
# client_ids - массив числе, обязательно, не пустое
# date - дата в формате DD.MM.YYYY, опционально, может быть пустым

# Валидация аругементов:
# аргументы валидны, если валидны все поля по отдельности.

# Контекст
# в словарь контекста должна прописываться запись  "nclients" - количество id'шников,
# переденанных в запрос

# Ответ:
# в ответ выдается словарь <id клиента>:<список интересов>. Список генерировать произвольно.
# {"client_id1": ["interest1", "interest2" ...], "client2": [...] ...}
# или если произошла ошибка валидации
# {"code": 422, "error": "<сообщение о том какое поле невалидно>"}

# $ curl -X POST  -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "admin", "method": "clients_interests", "token": "d3573aff1555cd67dccf21b95fe8c4dc8732f33fd4e32461b7fe6a71d83c947688515e36774c00fb630b039fe2223c991f045f13f24091386050205c324687a0", "arguments": {"client_ids": [1,2,3,4], "date": "20.07.2017"}}' http://127.0.0.1:8080/method/
# -> {"code": 200, "response": {"1": ["books", "hi-tech"], "2": ["pets", "tv"], "3": ["travel", "music"], "4": ["cinema", "geek"]}}

# Требование: в результате в git должно быть только два(2!) файлика: api.py, test.py.
# Deadline: следующее занятие

import json
import random
import datetime
import logging
import hashlib
import uuid
import copy
import collections
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"

OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500

ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}

UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class Field(object):
    """Базовый класс для всех остальных полей."""

    def __init__(self, required=False, nullable=False):
        self.required, self.nullable = required, nullable

    def parse(self, value):
        # считаем, что простое поле всегда валидно
        return value


class CharField(Field):
    """Поле - строка"""
    FIELD_STR = 'must be a string'

    def parse(self, value):
        if not isinstance(value, str) and not isinstance(value, unicode):
            raise ValueError(self.FIELD_STR)
        return value


class ArgumentsField(Field):
    """Словарь (объект в терминах json)"""
    FIELD_DICT = 'must be a dictionary'

    def parse(self, value):
        if not isinstance(value, collections.Mapping):
            raise ValueError(self.FIELD_DICT)
        return value


class EmailField(CharField):
    """Строка содержащая @"""
    FIELD_EMAIL = 'must be valid email address'

    def parse(self, value):
        if '@' not in value:
            raise ValueError(self.FIELD_EMAIL)
        return value


class PhoneField(Field):
    """Поле должно быть строкой или числом.
    Длинной 11 символов, начинаться с 7.
    Опционально может быть пустым."""
    FIELD_PHONE = 'must be a string or number containing 11 digits and starting with 7'

    def parse(self, value):
        if len(str(value)) < 11 or not str(value).isdigit() or str(value)[0] != '7':
            raise ValueError(self.FIELD_PHONE)
        return value


class DateField(Field):
    """Дата в формате DD.MM.YYYY"""
    FIELD_DATE = 'must be in DD.MM.YYYY format'

    def parse(self, value):
        try:
            date = datetime.datetime.strptime(value, '%d.%m.%Y').date()
            return date
        except ValueError:
            raise ValueError(self.FIELD_DATE)


class BirthDayField(DateField):
    """Дата в формате DD.MM.YYYY, с которой прошло не больше 70 лет"""
    FIELD_BIRTHDAY = 'must be no more than 70 years'

    def parse(self, value):
        value = super(BirthDayField, self).parse(value)
        date_today = datetime.date.today()
        td = (date_today - value).days / 365
        if not (0 < td < 70):
            raise ValueError(self.FIELD_BIRTHDAY)
        return value


class GenderField(Field):
    """Число 0, 1 или 2"""
    FIELD_INT = 'must be integer'
    FIELD_GENDER = 'must be one of the values [0, 1, 2]'

    def parse(self, value):
        if not isinstance(value, int):
            raise ValueError(self.FIELD_INT)
        if not (0 <= value < 3):
            raise ValueError(self.FIELD_GENDER)
        return value


class ClientIDsField(Field):
    """Поле массив чисел, обязательно не пустое."""
    FIELD_CLIENTID = 'must be list of numbers'

    def parse(self, value):
        if not isinstance(value, collections.MutableSequence):
            raise ValueError(self.FIELD_CLIENTID)
        for el in value:
            if not isinstance(el, int):
                raise ValueError(self.FIELD_CLIENTID)
        return value


class MetaRequest(type):
    """Мета запрос.
    Данный мета-класс будем применять ко всем запросам: MethodRequest, OnlineScoreRequest, ClientsInterestsRequest.
    Перед созданием нового класса-запроса обходим все атрибуты, у которых базовый класс Field и
    создаем словарь имя атрибута-класс поле. Сохраняем словарь в атрибуте request_fields.
    """

    def __new__(cls, name, bases, attrs):
        request_fields = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                request_fields[k] = v
                attrs.pop(k)
        attrs['request_fields'] = request_fields
        new_class = super(MetaRequest, cls).__new__(cls, name, bases, attrs)
        return new_class


class BaseRequest(object):
    __metaclass__ = MetaRequest
    EMPTY_VALUES = ([], {}, '', None)
    FIELD_REQUIRED = 'Field {} required.'
    FIELD_NULLABLE = 'Field {} can not be nullable.'
    FIELD_VALIDATION = 'Field {} validation error: {}.'

    def __init__(self, **kwargs):
        # сделаем копию списка полей
        self.request_fields = copy.deepcopy(self.request_fields)
        self.errors = []
        self.request = kwargs
        self.is_parsed = False

    def is_valid(self):
        if not self.is_parsed:
            self.validate_all()
        return not self.errors

    def validate_all(self):
        for name, field in self.request_fields.items():
            value = None
            try:
                value = self.request[name]
            except (KeyError, TypeError):
                if field.required:
                    self.errors.append(self.FIELD_REQUIRED.format(name))
                    continue
            if value in self.EMPTY_VALUES:
                if field.nullable:
                    setattr(self, name, value)
                else:
                    self.errors.append(self.FIELD_NULLABLE.format(name))
                continue
            try:
                setattr(self, name, field.parse(value))
            except ValueError, e:
                self.errors.append(self.FIELD_VALIDATION.format(name, e))
        self.is_parsed = True

    def _get_non_empty_request_fields(self):
        """Получаем генератор списока не пустых полей реального запроса"""
        existing_fields = (name for name, field in self.request_fields.items()
                           if getattr(self, name, None) is not None)
        non_empty_fields = (name for name in existing_fields if getattr(self, name) not in ([], {}, ''))
        return non_empty_fields


class ClientsInterestsRequest(BaseRequest):
    # массив интересов, из которого будем генерировать случайные сэмплы
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(BaseRequest):
    FIELD_PAIRS = 'One of the pairs {} must not be empty.'
    # пары полей, хотябы одна из пар не должна быть пустой
    _pairs = (
        ('phone', 'email'),
        ('first_name', 'last_name'),
        ('gender', 'birthday')
    )
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def is_valid(self):
        pre_check = super(OnlineScoreRequest, self).is_valid()
        if not pre_check:
            return pre_check
        non_empty = set(self._get_non_empty_request_fields())
        # для каждой пары полей, которые не должны быть пустыми
        # проверяем их наличие в множестве не пустых полей
        result = any(non_empty.issuperset(el) for el in self._pairs)
        if not result:
            self.errors.append(self.FIELD_PAIRS.format(self._pairs))
            return False
        return True


class MethodRequest(BaseRequest):
    NOT_EXISTS = 'Method {} does not exists.'
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class ApiHandler(object):
    def validate_process(self, request, method_data, ctx):
        if not method_data.is_valid():
            return join_errors(INVALID_REQUEST, request.errors)
        return self.process(request, method_data, ctx)


class ClientsInterestsHandler(ApiHandler):
    request_cls = ClientsInterestsRequest
    _interests = ['python', 'perl', 'C', 'C++', 'C#', 'Pascal', 'Erlang', 'Lisp']

    def process(self, request, method_data, ctx):
        """Обрабатываем метод clients_interests"""
        ctx['nclients'] = len(method_data.client_ids)
        response = {}
        for client in method_data.client_ids:
            response[client] = self._gen_interests()
        return response, OK

    def _gen_interests(self):
        """Генериуем фейковые интересы для клиентов"""
        return random.sample(self._interests, 3)


class OnlineScoreHandler(ApiHandler):
    request_cls = OnlineScoreRequest

    def process(self, request, method_data, ctx):
        """Обработка метода online_score"""
        ctx['has'] = list(method_data._get_non_empty_request_fields())
        if request.is_admin:
            return {'score': 42}, OK
        return {'score': random.randrange(0, 10)}, OK


def check_auth(request):
    if request.login == ADMIN_LOGIN:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        if not hasattr(request, 'account') or request.account is None:
            return False
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx):
    # мэппинг метод-класс, отвечающих за обработку конкретных методов
    handler_cls = {
        'online_score': OnlineScoreHandler,
        'clients_interests': ClientsInterestsHandler
    }
    body = request['body']
    if not isinstance(body, collections.Mapping):
        return None, INVALID_REQUEST
    request = MethodRequest(**body)
    if not request.is_valid():
        return join_errors(INVALID_REQUEST, request.errors)
    if not check_auth(request):
        return None, FORBIDDEN
    handler = handler_cls.get(request.method)
    if handler is None:
        return "Method Not Found", NOT_FOUND
    arguments = request.arguments
    method_data = handler.request_cls(**arguments)
    return handler().validate_process(request, method_data, ctx)


def join_errors(error_code, errors):
    return '{} - {}'.format(ERRORS.get(error_code, "Unknown Error"), ' '.join(errors)), error_code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context)
                except Exception, e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
