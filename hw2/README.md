## Домашнее задание

Дата: 14.07.2017

* Добавить новый opcode в Python
* Добавить until в Python | [пример](http://eli.thegreenplace.net/2010/06/30/python-internals-adding-a-new-statement-to-python/)
* [Опционально] Добавить инткремент и декремент | [пример](https://hackernoon.com/modifying-the-python-language-in-7-minutes-b94b0a99ce14)

### Добавить новый opcode в Python

В ходе работы над этим заданием нам нужно пропатчить следующие файлы:

* Include/opcode.h
* Lib/opcode.py
* Python/ceval.c
* Python/opcode_targets.h
* Python/peephole.c

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
make -j2
./python
```

Тестируем:
```
[root@615d6580caa5 cpython]# ./python 
Python 2.7.13+ (default, Jul 18 2017, 19:22:06) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-11)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> def fib(n): return fib(n - 1) + fib(n - 2) if n > 1 else n
... 
[44739 refs]
>>> import dis
[46031 refs]
>>> dis.dis(fib)
  1           0 LOAD_FC                  1
              3 COMPARE_OP               4 (>)
              6 POP_JUMP_IF_FALSE       31
              9 LOAD_GLOBAL              0 (fib)
             12 LOAD_FC                  1
             15 BINARY_SUBTRACT     
             16 CALL_FUNCTION            1
             19 LOAD_GLOBAL              0 (fib)
             22 LOAD_FC                  2
             25 BINARY_SUBTRACT     
             26 CALL_FUNCTION            1
             29 BINARY_ADD          
             30 RETURN_VALUE        
        >>   31 LOAD_FAST                0 (n)
             34 RETURN_VALUE        
[46058 refs]

```

### Добавить until в Python

Для выполнения используем [данную статью.](http://eli.thegreenplace.net/2010/06/30/python-internals-adding-a-new-statement-to-python/)

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
>>> num = 3
>>> until num == 0:
...   print(num)
...   num -= 1
...
3
2
1
```