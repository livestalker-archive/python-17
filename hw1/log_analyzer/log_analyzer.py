#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import gzip
import re

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

GZIP_EXT = '.gz'
URL_REGEXP = re.compile(r'\"\w+ (?P<url>(.*)) HTTP')
RT_REGEXP = re.compile(r' (?P<rt>[0-9.]+)$')

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def get_last_log_file(config):
    list_of_logs = glob.glob(os.path.join(config['LOG_DIR'], '*'))
    return max(list_of_logs, key=os.path.getmtime)


def get_open_func(filename):
    _, ext = os.path.splitext(filename)
    if ext == GZIP_EXT:
        return gzip.open
    else:
        return open


def get_url(line):
    m = URL_REGEXP.search(line)
    if m:
        return m.group('url')
    else:
        return None


def get_request_time(line):
    m = RT_REGEXP.search(line)
    if m:
        return m.group('rt')
    else:
        return 0


def analyzer():
    pass


def main():
    last_log = get_last_log_file(config)
    open_func = get_open_func(last_log)
    for line in open_func(last_log, mode='r'):
        line = line.strip()
        print get_url(line) + ' ' + get_request_time(line)
    pass


if __name__ == "__main__":
    main()
