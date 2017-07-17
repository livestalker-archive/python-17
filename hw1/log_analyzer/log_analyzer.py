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

URL_RT_REGEXP = re.compile(r'\"\w+ (?P<url>(.*?)) HTTP.* (?P<rt>[0-9.]+)$')
LOG_DATE_REGEXP = re.compile(r'(?P<full_date>(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}))')
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
    list_of_files = glob.glob(os.path.join(config['LOG_DIR'], '*'))
    list_of_logs_filtered = (el for el in list_of_files if LOG_DATE_REGEXP.search(el))
    # create generator with elements (full_date_string, log_filename)
    list_of_logs = ((LOG_DATE_REGEXP.search(el).group('full_date'), el)
                    for el in list_of_logs_filtered)
    try:
        last = max(list_of_logs, key=lambda x: x[0])
        return last[1]
    except ValueError:
        # empty sequence
        return None


def is_file_exists(filename):
    """Check if file exists."""
    return os.path.isfile(filename)


def get_open_func(filename):
    """Get open function depending on file extension."""
    _, ext = os.path.splitext(filename)
    if ext == '.gz':
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
        return os.path.join(config['REPORT_DIR'], report_filename)
    else:
        return None


def get_url_rt(line):
    m = URL_RT_REGEXP.search(line)
    if m:
        return m.group('url'), float(m.group('rt'))
    return None, 0


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
            url, rt = get_url_rt(line)
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


def main(log, report, formatter):
    data = parse_log(log)
    result = process_data(data)
    formatter(report, result)


if __name__ == "__main__":
    """Log file must be in format report-YYYYMMDD[.gz]"""
    parser = argparse.ArgumentParser(description='Parse web server logs.')
    parser.add_argument('--log_path', dest='log_path', help='path to the log file')
    parser.add_argument('--report_format', dest='report_format', default='html', choices=['html', 'json'],
                        help='report format')
    parser.add_argument('--report_size', dest='report_size', default=config['REPORT_SIZE'], help='report size in lines')
    parsed_args = parser.parse_args()

    formatter_func = get_report_formatters()[parsed_args.report_format]
    if parsed_args.report_size:
        config['REPORT_SIZE'] = parsed_args.report_size
    last_log = parsed_args.log_path if parsed_args.log_path else get_last_log_file()

    # if get_last_log_file return None
    if not last_log:
        sys.stderr.write('Can not find last log.\n')
        sys.stderr.flush()
        sys.exit(1)

    # if log_file set in args and file does not exists
    if not is_file_exists(last_log):
        sys.stderr.write('File {0} does not exist.\n'.format(last_log))
        sys.stderr.flush()
        sys.exit(1)

    report_filename = gen_report_name(last_log, parsed_args.report_format)

    # if we can not parse date from log filename
    if not report_filename:
        sys.stderr.write('Can not parse date from {0} filename.\n'.format(last_log))
        sys.stderr.flush()
        sys.exit(1)

    # if report with specific extension exists
    if is_file_exists(report_filename):
        sys.stderr.write('Report {0} already exist.\n'.format(report_filename))
        sys.stderr.flush()
        sys.exit(1)

    main(last_log, report_filename, formatter_func)
