FROM centos

WORKDIR /tmp/otus/

RUN mkdir -p /tmp/otus
RUN yum install -y \
                gcc \
				make \
				zlib-devel \
				protobuf \
				protobuf-c \
				protobuf-c-compiler \
				protobuf-c-devel \
				python-devel \
				python-setuptools \
				gdb \
				less \
				vim

COPY deviceapps.proto .
RUN protoc-c --c_out=. deviceapps.proto
COPY tests ./tests
COPY setup.py .
COPY Makefile .
COPY pb.c .
