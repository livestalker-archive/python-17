## Домашнее задание

Дата: 04.08.2017

### Задача

Написать uWSGI демона (для CentOS 7), который по запросу на IPv4 возвращает текущую погоду в городе, 
к которому относится IP, в виде json.

* использовать сервисы: https://ipinfo.io/developers, https://openweathermap.org/current;
* запросы на демон должен проксировать nginx, демон должен запускаться sytemd;
* демон должен собираться в пакет

Результат:

1. скрипт
2. конфиг uwsgi
3. .service файл для systemd
4. .spec файл для rpm пакета
5. собранный rpm пакет
6. конфиг nginx, где описан локейшн ip2w


### Назначение файлов

| Файл | Назначение |
| ---|---|
| env_build.sh | сборка образа контейнера для сборки пакета |
| Dockerfile-build | описание контейнера для сборки пакета |
| buildrpm.sh | скрипт для сборки rpm пакета |
| env_prod.sh |  сборка образа контейнера для тестирования пакета|
| Dockerfile |  описание контейнера для тестирования пакета|
| ip2w.sepc | спецификация для сборки rpm пакета |
| ip2w.ini | конфигурация uwsgi |
| ip2w.py | скрипт ip2w |
| ip2w.service | конфигурация для systemd |
| nginx_weather.conf | конфигурация для nginx |
| nginx.repo | описание репозитория nginx |
| run_build_cont.sh | запустить контейнер для сборки |
| run_prod_cont.sh | запустить контейнер для тестирования |
| ip2w-0.0.1-1.noarch.rpm | rpm пакет |

### Сборка

```bash
git clone https://github.com/LiveStalker/python-17.git
cd python-17/hw5/
chmod u+x env_build.sh env_prod.sh run_build_cont.sh run_prod_cont.sh buildrpm.sh
```
