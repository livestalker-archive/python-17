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

### Архитектура

ThreadPool с N воркерами.

### Параметры сервера

```
usage: httpd.py [-h] -r DOC_ROOT [-w WORKERS_COUNT] [-a HOST] [-p PORT]
                [-l {DEBUG,INFO,WARN,ERROR}]

Web server

optional arguments:
  -h, --help            show this help message and exit
  -r DOC_ROOT           Document root
  -w WORKERS_COUNT      Worker count
  -a HOST               Web server bind address
  -p PORT               Web server port
  -l {DEBUG,INFO,WARN,ERROR}
                        Log level
```

### Однопоточный (tag: [single_thread](https://github.com/LiveStalker/python-17/tree/single_thread))

```bash
ab -n 50000 -c 100 -r -s 60 http://127.0.0.1:8080/test.html
```

```
Server Software:        OTUS
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /test.html
Document Length:        85 bytes

Concurrency Level:      100
Time taken for tests:   110.693 seconds
Complete requests:      50000
Failed requests:        270
   (Connect: 0, Receive: 90, Length: 90, Exceptions: 90)
Total transferred:      11479300 bytes
HTML transferred:       4242350 bytes
Requests per second:    451.70 [#/sec] (mean)
Time per request:       221.386 [ms] (mean)
Time per request:       2.214 [ms] (mean, across all concurrent requests)
Transfer rate:          101.27 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0   10 311.0      0   31048
Processing:     0   20 669.4      1  106672
Waiting:        0    7 208.9      1   13088
Total:          0   30 783.2      1  106672

Percentage of the requests served within a certain time (ms)
  50%      1
  66%      1
  75%      1
  80%      1
  90%      1
  95%      1
  98%      1
  99%      1
 100%  106672 (longest request)
```

###Сервер с использованием threading.Thread

```bash
ab -n 50000 -c 100 -r -s 60 http://127.0.0.1:8080/test.html
```

```
Server Software:        OTUS
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /test.html
Document Length:        85 bytes

Concurrency Level:      100
Time taken for tests:   18.588 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      11500000 bytes
HTML transferred:       4250000 bytes
Requests per second:    2689.90 [#/sec] (mean)
Time per request:       37.176 [ms] (mean)
Time per request:       0.372 [ms] (mean, across all concurrent requests)
Transfer rate:          604.18 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0  11.0      0    1000
Processing:    16   37   3.8     36     436
Waiting:       16   37   3.8     36     436
Total:         28   37  12.9     37    1435

Percentage of the requests served within a certain time (ms)
  50%     37
  66%     37
  75%     37
  80%     37
  90%     38
  95%     39
  98%     47
  99%     54
 100%   1435 (longest request)
```