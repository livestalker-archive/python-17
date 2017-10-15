.PHONY: build-cont
build-cont:
	docker build -t hw10 .

.PHONY: run-cont
run-cont: build-cont
	docker run --rm -it --name hw10-cont hw10 /bin/bash

.PHONY: test
test: clean
	python setup.py test

.PHONY: clean
clean:
	-rm -fr ./build
	-rm -fr ./pb.egg-info

.PHONY: gen
gen:
	protoc --python_out=. deviceapps.proto
	protoc-c --c_out=. deviceapps.proto