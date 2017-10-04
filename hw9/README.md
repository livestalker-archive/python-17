## Install ##

debian:

sudo apt-get install protobuf-compiler

## Lab configuration ##

*CPU*

```
processor       : 0
vendor_id       : GenuineIntel
model name      : Intel(R) Xeon(R) CPU E5-2660 v2 @ 2.20GHz
--
processor       : 1
vendor_id       : GenuineIntel
model name      : Intel(R) Xeon(R) CPU E5-2660 v2 @ 2.20GHz
--
processor       : 2
vendor_id       : GenuineIntel
model name      : Intel(R) Xeon(R) CPU E5-2660 v2 @ 2.20GHz
--
processor       : 3
vendor_id       : GenuineIntel
model name      : Intel(R) Xeon(R) CPU E5-2660 v2 @ 2.20GHz
```

*Данные для обработки*

```bash
-rw-r--r-- 1 aleksio aleksio 30M Oct  4 09:46 20170929000000.tsv.gz
-rw-r--r-- 1 aleksio aleksio 30M Oct  4 09:46 20170929000100.tsv.gz
-rw-r--r-- 1 aleksio aleksio 30M Oct  4 09:46 20170929000200.tsv.gz
```

```bash
ps aux | grep [m]emcached
aleksio   1710  0.0  0.1 319040  2124 pts/0    Sl   09:55   0:00 memcached -l 127.0.0.1 -p 33013
aleksio   1712  0.0  0.1 319040  2216 pts/0    Sl   09:55   0:00 memcached -l 127.0.0.1 -p 33014
aleksio   1714  0.0  0.1 319040  2180 pts/0    Sl   09:55   0:00 memcached -l 127.0.0.1 -p 33015
aleksio   1716  0.0  0.1 319040  2208 pts/0    Sl   09:55   0:00 memcached -l 127.0.0.1 -p 33016

# без запуска memcached (как-будто отправляем данные в никуда)
time python memc_load_lin.py --pattern './data/appsinstalled/*.tsv.gz'

real    2m39.095s
user    2m14.908s
sys     0m23.952s

# без запуска memcached (как-будто отправляем данные в никуда)
time python memc_load.py --pattern './data/appsinstalled/*.tsv.gz'
real    1m3.840s
user    2m15.492s
sys     0m25.396s
```
