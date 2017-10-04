BIND_ADDRESS=127.0.0.1

.PHONY: genprotopy
genprotopy:
	protoc --python_out=. ./appsinstalled.proto

.PHONY: prepare-ve
prepare-ve:
	virtualenv ./.hw9

.PHONY: run_memcached
run_memcached:
	memcached -l $(BIND_ADDRESS) -m 1024 -p 33013 &
	memcached -l $(BIND_ADDRESS) -m 1024 -p 33014 &
	memcached -l $(BIND_ADDRESS) -m 1024 -p 33015 &
	memcached -l $(BIND_ADDRESS) -m 1024 -p 33016 &

.PHONY: stop_memcaced
stop_memcaced:
	kill -s 9 `ps aux | grep [m]emcached | tr -s ' ' | cut -f2 -d' '`

.PHONY: reset
reset: stop_memcaced run_memcached