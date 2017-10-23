FROM centos

WORKDIR /tmp/otus/

RUN mkdir -p /tmp/otus
RUN yum clean all
RUN yum install -y \
                gcc \
				make \
				zlib-devel \
				protobuf \
				protobuf-c \
				protobuf-c-compiler \
				protobuf-c-devel \
				protobuf-python \
				python-devel \
				python-setuptools \
				gdb \
				less \
				vim
RUN yum clean all

COPY deviceapps.proto .
RUN protoc-c --c_out=. deviceapps.proto
RUN protoc --python_out=. deviceapps.proto
COPY tests ./tests
COPY setup.py .
COPY Makefile .
COPY pb.c .
