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

Mem: 16GB
```

*Данные для обработки*

```bash
aleksio@nginx:~/hw9/data/appsinstalled$ ls -lh
total 1.5G
-rw-r--r-- 1 aleksio aleksio 507M Oct  3 15:41 20170929000000.tsv.gz
-rw-r--r-- 1 aleksio aleksio 507M Oct  4 09:26 20170929000100.tsv.gz
-rw-r--r-- 1 aleksio aleksio 507M Oct  4 14:17 20170929000200.tsv.gz

# 4 мемкэша
aleksio@nginx:~$ ps aux | grep [m]emcached
aleksio   3046  0.0  0.0 319040  2180 pts/0    Sl   14:09   0:00 memcached -l 127.0.0.1 -m 1024 -p 33013
aleksio   3048  0.0  0.0 319040  2264 pts/0    Sl   14:09   0:00 memcached -l 127.0.0.1 -m 1024 -p 33014
aleksio   3055  0.0  0.0 319040  2168 pts/0    Sl   14:09   0:00 memcached -l 127.0.0.1 -m 1024 -p 33015
aleksio   3062  0.0  0.0 319040  2084 pts/0    Sl   14:09   0:00 memcached -l 127.0.0.1 -m 1024 -p 33016
```

Один процесс

```bash
(.hw9) aleksio@nginx:~/hw9$ time python memc_load_lin.py --pattern './data/appsinstalled/*.tsv.gz'
[2017.10.04 14:48:01] I Memc loader started with options: {'dry': False, 'log': None, 'pattern': './data/appsinstalled/*.tsv.gz', 'idfa': '127.0.0.1:33013', 'dvid': '127.0.0.1:33016', 'test': False, 'adid': '127.0.0.1:33015', 'gaid': '127.0.0.1:33014'}
[2017.10.04 14:48:01] I Processing ./data/appsinstalled/20170929000200.tsv.gz
[2017.10.04 14:59:20] I Acceptable error rate (0.0). Successfull load
[2017.10.04 14:59:20] I Processing ./data/appsinstalled/20170929000100.tsv.gz
[2017.10.04 15:10:40] I Acceptable error rate (0.0). Successfull load
[2017.10.04 15:10:40] I Processing ./data/appsinstalled/20170929000000.tsv.gz
[2017.10.04 15:22:05] I Acceptable error rate (0.0). Successfull load

real    34m3.538s
user    24m30.116s
sys     5m52.516s
```

N процессов, в данном случае 4, задействовано 3 (т.к. три файла с даннаыми)

```bash
(.hw9) aleksio@nginx:~/hw9$ time python memc_load.py --pattern './data/appsinstalled/*.tsv.gz'
[2017.10.04 14:20:17] I Memc loader started with options: {'dry': False, 'log': None, 'pattern': './data/appsinstalled/*.tsv.gz', 'idfa': '127.0.0.1:33013', 'dvid': '127.0.0.1:33016', 'test': False, 'adid': '127.0.0.1:33015', 'gaid': '127.0.0.1:33014'}
[2017.10.04 14:20:17] I Worker count: 4.
[2017.10.04 14:20:17] I Start results worker
[2017.10.04 14:20:17] I Processing ./data/appsinstalled/20170929000200.tsv.gz (seq: 0)
[2017.10.04 14:20:17] I Processing ./data/appsinstalled/20170929000100.tsv.gz (seq: 1)
[2017.10.04 14:20:17] I Processing ./data/appsinstalled/20170929000000.tsv.gz (seq: 2)
[2017.10.04 14:20:27] I Process-4 - queue empty.
[2017.10.04 14:33:07] I Acceptable error rate (0.0). Successfull load
[2017.10.04 14:33:07] I Rename ./data/appsinstalled/20170929000200.tsv.gz (seq: 0)
[2017.10.04 14:33:07] I Acceptable error rate (0.0). Successfull load
[2017.10.04 14:33:07] I Rename ./data/appsinstalled/20170929000100.tsv.gz (seq: 1)
[2017.10.04 14:33:07] I Acceptable error rate (0.0). Successfull load
[2017.10.04 14:33:07] I Rename ./data/appsinstalled/20170929000000.tsv.gz (seq: 2)
[2017.10.04 14:33:14] I Process-3 - queue empty.
[2017.10.04 14:33:14] I Process-2 - queue empty.
[2017.10.04 14:33:17] I Process-1 - queue empty.

real    13m0.162s
user    24m9.420s
sys     5m9.492s
```
