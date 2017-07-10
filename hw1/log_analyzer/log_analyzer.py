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
        # TODO error float
        return float(m.group('rt'))
    else:
        return 0


def process_save_results(total_count, total_time, urls):
    template = {
        "count": 0,
        "time_avg": 0,
        "time_max": 0,
        "time_sum": 0,
        "url": "",
        "time_med": 0,
        "time_perc": 0,
        "count_perc":0
    }
    for url in urls:
        count = urls[url][0]
        count_perc = float(count) / total_count
        time_avg = urls[url][1] / count
        time_max = urls[url][2]
        time_med = None
        time_perc = urls[url][1] / total_time
        time_sum = urls[url][1]
        pass


def make_analyzer():
    total_count = 0
    total_time = 0
    urls = {}
    # url_count
    # url_total_time
    # url_max_time
    try:
        while True:
            url, rt = yield
            total_count += 1
            total_time += rt
            if url in urls:
                urls[url][0] += 1
                urls[url][1] += rt
                if rt > urls[url][2]:
                    urls[url][2] = rt
            else:
                urls[url] = [1, rt, rt]
    except GeneratorExit as e:
        process_save_results(total_count, total_time, urls)


def main():
    last_log = get_last_log_file(config)
    open_func = get_open_func(last_log)
    analizer = make_analyzer()
    analizer.next()
    for line in open_func(last_log, mode='r'):
        line = line.strip()
        analizer.send((get_url(line), get_request_time(line)))
    analizer.close()
    pass


if __name__ == "__main__":
    main()
