#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import gzip
import re
import json
import argparse
import sys
from datetime import date

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

GZIP_EXT = '.gz'
HTML_EXT = '.html'
JSON_EXT = '.json'
URL_REGEXP = re.compile(r'\"\w+ (?P<url>(.*?)) HTTP')
RT_REGEXP = re.compile(r' (?P<rt>[0-9.]+)$')
LOG_DATE_REGEXP = re.compile(r'(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})')
MARKER = '$table_json'

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TEMPLATE": "./report.html",
    "FP_DIGITS": 3  # digits after the decimal point
}


def get_last_log_file():
    """Find last log file."""
    list_of_logs = glob.glob(os.path.join(config['LOG_DIR'], '*'))
    return max(list_of_logs, key=os.path.getmtime)


def is_file_exists(filename):
    """Check if file exists."""
    return os.path.isfile(filename)


def get_open_func(filename):
    """Get open function depending on file extension."""
    _, ext = os.path.splitext(filename)
    if ext == GZIP_EXT:
        return gzip.open
    else:
        return open


def gen_report_name(log_filename, report_format):
    """Generate report name."""
    m = LOG_DATE_REGEXP.search(log_filename)
    if m:
        report_filename = 'report-{0}.{1}.{2}.{3}'.format(m.group('year'),
                                                          m.group('month'),
                                                          m.group('day'),
                                                          report_format)
    else:
        # if can  not parse date from log filename, let's save results with current file name and prefix unmatched
        current_date = date.today()
        report_filename = 'unmatched-report-{0}.{1:02}.{2:02}.{3}'.format(current_date.year,
                                                                          current_date.month,
                                                                          current_date.day,
                                                                          report_format)
    return os.path.join(config['REPORT_DIR'], report_filename)


def get_url(line):
    """Parse url from the log line."""
    m = URL_REGEXP.search(line)
    if m:
        return m.group('url')
    else:
        return None


def get_request_time(line):
    """Parse request time from the log line."""
    m = RT_REGEXP.search(line)
    if m:
        # TODO error float
        return float(m.group('rt'))
    else:
        return 0


def median(values):
    """Compute median."""
    if len(values) % 2 == 0:
        return (values[(len(values) / 2) - 1] + values[len(values) / 2]) / 2.0

    elif len(values) % 2 != 0:
        return values[int((len(values) / 2))]


def parse_log(filename):
    """Parse log file and fill dict url->list(request_time1, request_time2...)."""
    urls = {}
    total_count = 0
    total_time = 0
    open_func = get_open_func(filename)
    with open_func(filename, mode='r') as log:
        for line in log:
            line = line.strip()
            url = get_url(line)
            rt = get_request_time(line)
            total_count += 1
            total_time += rt
            if url not in urls:
                urls[url] = [rt]
            else:
                urls[url].append(rt)
    return total_count, total_time, urls


def process_data(data):
    """Process data."""
    ndigits = config['FP_DIGITS']
    total_count, total_time, urls = data
    result = []
    for url in urls:
        count = len(urls[url])
        count_perc = round(100 * float(count) / total_count, ndigits)
        time_avg = round(sum(urls[url]) / count, ndigits)
        time_max = round(max(urls[url]), ndigits)
        time_med = round(median(sorted(urls[url])), ndigits)
        time_sum = round(sum(urls[url]), ndigits)
        time_perc = round(100 * time_sum / total_time, ndigits)
        result.append({
            "url": url,
            "count": count,
            "count_perc": count_perc,
            "time_avg": time_avg,
            "time_max": time_max,
            "time_med": time_med,
            "time_perc": time_perc,
            "time_sum": time_sum,
        })
    result.sort(key=lambda x: x['time_sum'], reverse=True)
    return result


def save_to_html(filename, data):
    """Save report in html format."""
    with open(config['TEMPLATE'], mode='r') as template:
        with open(filename, mode='w') as report:
            for line in template:
                if MARKER in line:
                    report.write(line.replace(MARKER, json.dumps(data)))
                else:
                    report.write(line)


def save_to_json(filename, data):
    """Save report in json format"""
    with open(filename, mode='w') as report:
        report.write(json.dumps(data))


def get_report_formatters():
    """Get list of report formatters."""
    return {
        'json': save_to_json,
        'html': save_to_html
    }


def main():
    """Log file must be in format report-YYYYMMDD[.gz]"""
    parser = argparse.ArgumentParser(description='Parse web server logs.')
    parser.add_argument('--log_path', dest='log_path', help='path to the log file')
    parser.add_argument('--report_format', dest='report_format', default='html', choices=['html', 'json'],
                        help='report format')
    parser.add_argument('--report_size', dest='report_size', default=config['REPORT_SIZE'], help='report size in lines')
    parsed_args = parser.parse_args()

    last_log = parsed_args.log_path if parsed_args.log_path else get_last_log_file()
    if parsed_args.report_size:
        config['REPORT_SIZE'] = parsed_args.report_size

    if not is_file_exists(last_log):
        sys.stderr.write('File {0} does not exist.\n'.format(last_log))
        sys.stderr.flush()
        sys.exit(1)

    report_filename = gen_report_name(last_log, parsed_args.report_format)
    if is_file_exists(report_filename):
        sys.stderr.write('Report {0} already exist.\n'.format(report_filename))
        sys.stderr.flush()
        sys.exit(1)

    data = parse_log(last_log)
    result = process_data(data)
    formatter = get_report_formatters()[parsed_args.report_format]
    formatter(report_filename, result)
    pass


if __name__ == "__main__":
    main()
