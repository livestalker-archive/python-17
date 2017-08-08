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

Собраный пакет уже в репозитории. Процедура сборки приведена для справки.

```bash
git clone https://github.com/LiveStalker/python-17.git
cd python-17/hw5/
chmod u+x env_build.sh env_prod.sh run_build_cont.sh run_prod_cont.sh buildrpm.sh
./env_build.sh      # собираем образ
./run_build_cont.sh # запускаем контейнер для сборки пакета

# внутри контейнера
cd hw5
# может понадобиться, если для гита не установлены данные параметры
git config --local user.name <name> 
git config --local user.email <email>
# может понадобиться, иначе ошибка Bad owner/group: /root/hw5/ip2w.spec
chown root:root ip2w.spec 
# собираем пакет
./buildrpm.sh ip2w.spec
ls -l
...
-rw-r--r-- 1 1000 1000 5840 Aug  8 07:36 ip2w-0.0.1-1.noarch.rpm
...
```
