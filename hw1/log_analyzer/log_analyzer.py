#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import gzip
import re
import json

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

GZIP_EXT = '.gz'
URL_REGEXP = re.compile(r'\"\w+ (?P<url>(.*)) HTTP')
RT_REGEXP = re.compile(r' (?P<rt>[0-9.]+)$')
MARKER = '$table_json'

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TEMPLATE": "./report.html"
}


def get_last_log_file():
    list_of_logs = glob.glob(os.path.join(config['LOG_DIR'], '*'))
    return max(list_of_logs, key=os.path.getmtime)


def get_open_func(filename):
    _, ext = os.path.splitext(filename)
    if ext == GZIP_EXT:
        return gzip.open
    else:
        return open


def get_report_name():
    return os.path.join(config['REPORT_DIR'], 'report-2017.06.30.html')


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


def median(values):
    if len(values) % 2 == 0:
        return (values[(len(values) / 2) - 1] + values[len(values) / 2]) / 2.0

    elif len(values) % 2 != 0:
        return values[int((len(values) / 2))]


def gen_report(data):
    report_name = get_report_name()
    with open(config['TEMPLATE'], mode='r') as template:
        with open(report_name, mode='w') as report:
            for line in template:
                if MARKER in line:
                    report.write(line.replace(MARKER, json.dumps(data)))
                else:
                    report.write(line)



def process_save_results(total_count, total_time, urls):
    data = []
    for url in urls:
        count = len(urls[url])
        count_perc = float(count) / total_count
        time_avg = sum(urls[url]) / count
        time_max = max(urls[url])
        time_med = median(sorted(urls[url]))
        time_sum = sum(urls[url])
        time_perc = time_sum / total_time
        data.append({
            "url": url,
            "count": count,
            "count_perc": count_perc,
            "time_avg": time_avg,
            "time_max": time_max,
            "time_med": time_med,
            "time_perc": time_perc,
            "time_sum": time_sum,
        })
    gen_report(data)


def make_analyzer():
    total_count = 0
    total_time = 0
    urls = {}
    try:
        while True:
            url, rt = yield
            total_count += 1
            total_time += rt
            if url in urls:
                urls[url].append(rt)
            else:
                urls[url] = [rt]
    except GeneratorExit as e:
        process_save_results(total_count, total_time, urls)


def main():
    last_log = get_last_log_file()
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
