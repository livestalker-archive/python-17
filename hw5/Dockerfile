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

# create config directory
RUN mkdir -p /usr/local/etc/
COPY weather.ini /usr/local/etc/

# copy systemd config
COPY ip2w.service /etc/systemd/system/

# enable services
RUN systemctl enable nginx.service
RUN systemctl enable weather.service

# copy application script
COPY weather.py /var/www/

CMD ["/usr/sbin/init"]
