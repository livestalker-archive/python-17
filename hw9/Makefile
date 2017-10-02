BIND_ADDRESS=127.0.0.1

.PHONY: genprotopy
genprotopy:
	protoc --python_out=. ./appsinstalled.proto

.PHONY: run_memcached
run_memcached:
	memcached -l ${BIND_ADDRESS} -p 33013 &
	memcached -l ${BIND_ADDRESS} -p 33014 &
	memcached -l ${BIND_ADDRESS} -p 33015 &
	memcached -l ${BIND_ADDRESS} -p 33016 &

.PHONY: stop_memcaced
stop_memcaced:
	kill `ps aux | grep [m]emcached | cut -f3 -d' '`