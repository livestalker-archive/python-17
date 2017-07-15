## Домашнее задание

Дата: 14.07.2017

* Добавить новый opcode в Python
* Добавить until в Python | [пример](http://eli.thegreenplace.net/2010/06/30/python-internals-adding-a-new-statement-to-python/)
* [Опционально] Добавить инткремент и декремент | [пример](https://hackernoon.com/modifying-the-python-language-in-7-minutes-b94b0a99ce14)

### Добавить новый opcode в Python

TODO

### Добавить until в Python

В хостовой системе:

```bash
./prepare_env.sh # подготавливаем среду
cd cpython
git apply ../until/until.patch # патчим код
cd ..
./run_cont.sh # запускаем контейнер
```
В контейнере выполняем:

```bash
./configure --with-pydebug --prefix=/tmp/python
make regen-all
make -j2
./python
```

Тестируем until:

```bash
>>> until num == 0:
...   print(num)
...   num -= 1
...
3
2
1
```