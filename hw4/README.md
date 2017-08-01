## Домашнее задание

Дата: 28.07.2017

### Задача

Задание: Разработать веб-сервер. Разрешается использовать библиотеки помогающие 
реализовать асинхронную обработку соединений, запрещается использовать библиотеки 
реализующие какую-либо часть обработки HTTP. Провести нагрузочное тестирование, 
проверку стабильности и корректности работы. Если сервер асинхронный, то 
обязательно использовать [epoll](https://github.com/m13253/python-asyncore-epoll).

Веб-сервер должен уметь:

* Масштабироваться на несколько worker'ов
* Числов worker'ов задается аргументом командной строки -w
* Отвечать 200 или 404 на GET-запросы и HEAD-запросы
* Отвечать 405 на прочие запросы
* Возвращать файлы по произвольному пути в DOCUMENT_ROOT.
* Вызов /.html должен возвращать содердимое DOCUMENT_ROOT/.html
* DOCUMENT_ROOT задается аргументом командной строки -r
* Возвращать index.html как индекс директории
* Вызов // должен возвращать DOCUMENT_ROOT//index.html
* Отвечать следующими заголовками для успешных GET-запросов: 
  Date, Server, Content-Length, Content-Type, Connection
* Корректный Content-Type для: .html, .css, .js, .jpg, .jpeg, .png, .gif, .swf
* Понимать пробелы и %XX в именах файлов
* Опционально: демонизироваться через init-скрипт. init-скрипт должен 
  поддерживать команды start, stop, restart, status. При вызове без 
  параметров init-скрипт должен выводить список доступных команд


### Что проверять?

* [Проходят тестыr](https://github.com/s-stupnikov/http-test-suite).
* http://localhost/httptest/wikipedia_russia.html корректно показывается в браузере.
* Нагрузочное тестирование: запускаем ab -n 50000 -c 100 -r http://localhost:8080/ 
  и смотрим результат (опционально: вместо ab воспользоваться wrk)

### Что на выходе?

* сам сервер в httpd.py. Это точка входа (т.е. этот файлик обязательно 
  должен быть), можно разбить на модули.
* опциональный init-скрипт
* README.md с описанием использованной архитектуры (в двух словах: 
  asynchronous/thread pool/prefork/...) и результатами нагрузочного тестирования
  
## Описание решения

### Необходимая литература

* [Hypertext Transfer Protocol -- HTTP/1.0](https://tools.ietf.org/html/rfc1945)
* [Hypertext Transfer Protocol -- HTTP/1.1](https://tools.ietf.org/html/rfc2616)

## Результаты

### Однопоточный без использования неблокирующих сокетов

```
ab -n 50000 -c 100 -r -s 60 http://localhost:8080/
```

> Дополнительно выставил параметр -s (timeout), по умолчанию он равен 30 секунд, в данной
  версии сервер не укладывался в 30 секунд и сокет отваливался по таймауту.
  
```
This is ApacheBench, Version 2.3 <$Revision: 1706008 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        OTUS
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        4 bytes

Concurrency Level:      100
Time taken for tests:   81.230 seconds
Complete requests:      50000
Failed requests:        255
   (Connect: 0, Receive: 85, Length: 85, Exceptions: 85)
Non-2xx responses:      49915
Total transferred:      5640395 bytes
HTML transferred:       199660 bytes
Requests per second:    615.54 [#/sec] (mean)
Time per request:       162.460 [ms] (mean)
Time per request:       1.625 [ms] (mean, across all concurrent requests)
Transfer rate:          67.81 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   7.7      0    1001
Processing:     0  144 3364.4      0   81228
Waiting:        0    6 351.4      0   40396
Total:          0  144 3364.7      0   81229

Percentage of the requests served within a certain time (ms)
  50%      0
  66%      0
  75%      0
  80%      0
  90%      0
  95%      0
  98%      0
  99%      0
 100%  81229 (longest request)
```
