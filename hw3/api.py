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

FIELD_REQUIRED = 'Field {} required.'
FIELD_NULLABLE = 'Field {} can not be nullable.'
FIELD_STR = 'Field {} must be a string.'
FIELD_DICT = 'Field {} must be a dictionary.'
FIELD_EMAIL = 'Field {} must be valid email address.'
FIELD_PHONE = 'Field {} must be a string or number containing 11 digits and starting with 7.'
FIELD_DATE = 'Field {} must be in DD.MM.YYYY format.'
FIELD_BIRTHDAY = 'Age in field {} must be no more than 70 years.'
FIELD_GENDER = 'Field {} must be one of the values [0, 1, 2].'
FIELD_CLIENTID = 'Field {} must be list of numbers.'
FIELD_PAIRS = 'One of the pairs {} must not be empty.'

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
        self._error = None

    def is_valid(self, value):
        """Валидатор поля.
        В базовом классе мы проверяем только:
        1. требование к наличию поля
        2. может ли поле быть пустым"""
        if self.required and value is None:
            self._error = FIELD_REQUIRED
            return False
        if not self.nullable and not value:
            self._error = FIELD_NULLABLE
            return False
        return True

    @property
    def error(self):
        return self._error


class CharField(Field):
    """Поле - строка"""

    def is_valid(self, value):
        if not super(CharField, self).is_valid(value):
            return False
        if value is None:
            return True
        if not isinstance(value, str) and not isinstance(value, unicode):
            self._error = FIELD_STR
            return False
        return True


class ArgumentsField(Field):
    """Словарь (объект в терминах json)"""

    def is_valid(self, value):
        if not super(ArgumentsField, self).is_valid(value):
            return False
        if value is None:
            return True
        if not isinstance(value, collections.Mapping):
            self._error = FIELD_DICT
            return False
        return True


class EmailField(CharField):
    """Строка содержащая @"""

    def is_valid(self, value):
        if not super(EmailField, self).is_valid(value):
            return False
        if value is None:
            return True
        if '@' not in value:
            self._error = FIELD_EMAIL
            return False
        return True


class PhoneField(Field):
    """Поле должно быть строкой или числом.
    Длинной 11 символов, начинаться с 7.
    Опционально может быть пустым."""

    def is_valid(self, value):
        if not super(PhoneField, self).is_valid(value):
            return False
        if value is None:
            return True
        if len(str(value)) < 11 or not str(value).isdigit() or str(value)[0] != '7':
            self._error = FIELD_PHONE
            return False
        return True


class DateField(Field):
    """Дата в формате DD.MM.YYYY"""

    def is_valid(self, value):
        if not super(DateField, self).is_valid(value):
            return False
        # Проверку на нулевое значение и присутствие мы уже проверили в родительском классе.
        # Значение может быть None если поле в запросе отсутствует и ему разрешено отсутствовать.
        if value is None:
            return True
        try:
            date = datetime.datetime.strptime(value, '%d.%m.%Y')
            return True
        except ValueError:
            self._error = FIELD_DATE
            return False


class BirthDayField(DateField):
    """Дата в формате DD.MM.YYYY, с которой прошло не больше 70 лет"""

    def is_valid(self, value):
        if not super(BirthDayField, self).is_valid(value):
            return False
        if value is None:
            return True
        date = datetime.datetime.strptime(value, '%d.%m.%Y').date()
        date_today = datetime.date.today()
        td = (date_today - date).days / 365
        if not (0 < td < 70):
            self._error = FIELD_BIRTHDAY
            return False
        return True


class GenderField(Field):
    """Число 0, 1 или 2"""

    def is_valid(self, value):
        if not super(GenderField, self).is_valid(value):
            return False
        if value is None:
            return True
        if not isinstance(value, int):
            self._error = FIELD_GENDER
            return False
        if not (0 <= value < 3):
            self._error = FIELD_GENDER
            return False
        return True


class ClientIDsField(Field):
    """Поле массив чисел, обязательно не пустое."""

    def is_valid(self, value):
        if not super(ClientIDsField, self).is_valid(value):
            return False
        if value is None:
            return True
        if not isinstance(value, collections.MutableSequence):
            self._error = FIELD_CLIENTID
            return False
        for el in value:
            if not isinstance(el, int):
                self._error = FIELD_CLIENTID
                return False
        return True


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
    def __init__(self, *args, **kwargs):
        # сделаем копию списка полей
        self.request_fields = copy.deepcopy(self.request_fields)
        self.errors = []
        for k, v in kwargs.items():
            # если атрибут есть в DSL добавляем его как атрибут инстанса
            if k in self.request_fields:
                setattr(self, k, v)

    def is_valid(self):
        return self.is_all_valid()

    def is_all_valid(self):
        for name, field in self.request_fields.items():
            value = getattr(self, name, None)
            if not field.is_valid(value):
                self.errors.append(field.error.format(name))
        if len(self.errors) > 0:
            return False
        return True


class ClientsInterestsRequest(BaseRequest):
    __metaclass__ = MetaRequest
    # массив интересов, из которого будем генерировать случайные сэмплы
    _interests = ['python', 'perl', 'C', 'C++', 'C#', 'Pascal', 'Erlang', 'Lisp']
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def process(self, request, ctx):
        """Обрабатываем метод clients_interests"""
        ctx['nclients'] = len(self.client_ids)
        response = {}
        for client in self.client_ids:
            response[client] = self._gen_interests()
        return response, OK

    def _gen_interests(self):
        """Генериуем фейковые интересы для клиентов"""
        return random.sample(self._interests, 3)


class OnlineScoreRequest(BaseRequest):
    __metaclass__ = MetaRequest
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
        if not super(OnlineScoreRequest, self).is_valid():
            return False
        non_empty = set(self._get_all_non_empty())
        # для каждой пары полей, которые не должны быть пустыми
        # проверяем их наличие в множестве не пустых полей
        result = any(non_empty.issuperset(el) for el in self._pairs)
        if not result:
            self.errors.append(FIELD_PAIRS.format(self._pairs))
            return False
        return True

    def process(self, request, ctx):
        """Обработка метода online_score"""
        ctx['has'] = self._get_all_non_empty()
        if request.is_admin:
            return {'score': 42}, OK
        return {'score': random.randrange(0, 10)}, OK

    def _get_all_non_empty(self):
        """Получаем список не пустых полей"""
        return [name for name, field in self.request_fields.items()
                if getattr(self, name, None) is not None]


class MethodRequest(BaseRequest):
    __metaclass__ = MetaRequest
    # мэппинг метод-класс, отвечающий за обработку данного метода
    method_cls = {
        'online_score': OnlineScoreRequest,
        'clients_interests': ClientsInterestsRequest
    }

    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    def _get_method_instance(self):
        """Создание объекта для обработки конкретного метода"""
        return self.method_cls[self.method](**self.arguments)

    def process(self, ctx):
        """Обработка запроса"""
        method = self._get_method_instance()
        if not method.is_valid():
            return '{} {}'.format(ERRORS.get(INVALID_REQUEST), ' '.join(method.errors)), INVALID_REQUEST
        return method.process(self, ctx)


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
    body = request['body']
    request = MethodRequest(**body)
    if not request.is_valid():
        return '{} {}'.format(ERRORS.get(INVALID_REQUEST), ' '.join(request.errors)), INVALID_REQUEST
    if not check_auth(request):
        return ERRORS.get(FORBIDDEN), FORBIDDEN
    response, code = request.process(ctx)
    return response, code


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
