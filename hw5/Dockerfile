FROM centos

WORKDIR /var/www

RUN mkdir -p /var/www
RUN yum clean all
RUN yum install -y\
    python-devel  \
    gcc
ADD https://bootstrap.pypa.io/get-pip.py /tmp/
RUN python /tmp/get-pip.py
RUN pip install uwsgi
COPY weather.py /var/www/
