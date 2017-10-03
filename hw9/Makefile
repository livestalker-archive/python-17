BIND_ADDRESS=127.0.0.1

.PHONY: genprotopy
genprotopy:
	protoc --python_out=. ./appsinstalled.proto

.PHONY: prepare-ve
prepare-ve:
	virtualenv ./.hw9

.PHONY: run_memcached
run_memcached:
	memcached -l ${BIND_ADDRESS} -p 33013 &
	memcached -l ${BIND_ADDRESS} -p 33014 &
	memcached -l ${BIND_ADDRESS} -p 33015 &
	memcached -l ${BIND_ADDRESS} -p 33016 &

.PHONY: stop_memcaced
stop_memcaced:
	kill `ps aux | grep [m]emcached | cut -f3 -d' '`

.PHONY: back_rename
back_rename:
	@-mv ./data/appsinstalled/.20170929000200.tsv.gz ./data/appsinstalled/20170929000200.tsv.gz

.PHONY: reset
reset: stop_memcaced back_rename run_memcached