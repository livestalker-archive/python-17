FROM centos/systemd

WORKDIR /var/www

RUN mkdir -p /var/www
COPY nginx.repo /etc/yum.repos.d/nginx.repo
RUN yum clean all
RUN yum install -y\
    python-devel  \
    gcc \
    nginx \
    vim \
    less

ADD https://bootstrap.pypa.io/get-pip.py /tmp/
RUN python /tmp/get-pip.py
RUN pip install uwsgi

# copy nginx config
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx_weather.conf /etc/nginx/conf.d/nginx_weather.conf

COPY 'ip2w-0.0.1-1.noarch.rpm' /tmp/
RUN rpm -i /tmp/ip2w-0.0.1-1.noarch.rpm

# enable services
RUN systemctl enable nginx.service
RUN systemctl enable ip2w.service

CMD ["/usr/sbin/init"]
