#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import gzip
import sys
import glob
import logging
import collections
import time
from optparse import OptionParser
# brew install protobuf
# protoc  --python_out=. ./appsinstalled.proto
# pip install protobuf
import appsinstalled_pb2
# pip install python-memcached
import memcache
import multiprocessing as mp
import threading
import Queue

SENTINEL = object()
NORMAL_ERR_RATE = 0.01
AppsInstalled = collections.namedtuple("AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"])


class Worker(threading.Thread):
    def __init__(self, q, rq, m, dry=False):
        threading.Thread.__init__(self)
        self.daemon = True
        self.q = q
        self.rq = rq
        self.m = m
        self.dry = dry

    def run(self):
        logging.info('%s: Start thread %s.' % (os.getpid(), self.name))
        processed = errors = 0
        while True:
            try:
                line = self.q.get(timeout=0.1)
                if line == SENTINEL:
                    logging.info('%s: Stop thread %s.' % (os.getpid(), self.name))
                    self.rq.put((processed, errors))
                    break
                else:
                    appsinstalled = parse_appsinstalled(line)
                    if not appsinstalled:
                        errors += 1
                        continue
                    ok = insert_appsinstalled(self.m, appsinstalled, self.dry)
                    if ok:
                        processed += 1
                    else:
                        errors += 1
            except Queue.Empty:
                continue


def dot_rename(path):
    head, fn = os.path.split(path)
    # atomic in most cases
    os.rename(path, os.path.join(head, "." + fn))


def insert_appsinstalled(memc, appsinstalled, dry_run=False):
    tries = 3
    delay = 0.1
    ua = appsinstalled_pb2.UserApps()
    ua.lat = appsinstalled.lat
    ua.lon = appsinstalled.lon
    key = "%s:%s" % (appsinstalled.dev_type, appsinstalled.dev_id)
    ua.apps.extend(appsinstalled.apps)
    packed = ua.SerializeToString()
    try:
        if dry_run:
            logging.debug("%s - %s -> %s" % (memc.servers[0], key, str(ua).replace("\n", " ")))
        else:
            res = memc.set(key, packed)
            while not res and tries > 0:
                time.sleep(delay)
                res = memc.set(key, packed)
                tries -= 1
            return res != 0
    except Exception, e:
        logging.exception("Cannot write to memc %s: %s" % (memc.servers[0], e))
        return False


def parse_appsinstalled(line):
    line_parts = line.strip().split("\t")
    if len(line_parts) < 5:
        return
    dev_type, dev_id, lat, lon, raw_apps = line_parts
    if not dev_type or not dev_id:
        return
    try:
        apps = [int(a.strip()) for a in raw_apps.split(",")]
    except ValueError:
        apps = [int(a.strip()) for a in raw_apps.split(",") if a.isidigit()]
        logging.info("Not all user apps are digits: `%s`" % line)
    try:
        lat, lon = float(lat), float(lon)
    except ValueError:
        logging.info("Invalid geo coords: `%s`" % line)
    return AppsInstalled(dev_type, dev_id, lat, lon, apps)


def file_handler(options):
    fn, device_memc, options = options
    thread_pool = {}
    q_pool = {}
    results = Queue.Queue()

    # start threads
    for d in device_memc:
        m = memcache.Client([device_memc[d]])
        q = Queue.Queue()
        worker = Worker(q, results, m, options.dry)
        thread_pool[d] = worker
        q_pool[d] = q
        worker.start()

    logging.info('Processing %s.' % fn)
    processed = errors = 0
    with gzip.open(fn) as fd:
        for line in fd:
            line = line.strip()
            if not line:
                continue
            try:
                device_type = line.split()[0]
                if device_type not in device_memc.keys():
                    errors += 1
                    logging.error("Unknown device type: %s" % device_type)
                    continue
                q_pool[device_type].put(line)
            except IndexError:
                continue
    # stop threads
    for q in q_pool.values():
        q.put(SENTINEL)
    for t in thread_pool.values():
        t.join()
    while not results.empty():
        worker_processed, worker_errors = results.get(timeout=0.1)
        processed += worker_processed
        errors += worker_errors
    if not processed:
        fd.close()
        return fn

    err_rate = float(errors) / processed
    if err_rate < NORMAL_ERR_RATE:
        logging.info("Acceptable error rate (%s). Successfull load" % err_rate)
    else:
        logging.error("High error rate (%s > %s). Failed load" % (err_rate, NORMAL_ERR_RATE))
    fd.close()
    return fn


def main(options):
    device_memc = {
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
    }
    proc_pool = mp.Pool(int(options.workers))
    proc_args = sorted([(fn, device_memc, options) for fn in glob.iglob(options.pattern)],
                       key=lambda x: x[0])
    logging.info("Worker count: %s." % options.workers)
    for fn in proc_pool.imap(file_handler, proc_args):
        dot_rename(fn)
        logging.info('Rename %s.' % fn)


def prototest():
    sample = "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for line in sample.splitlines():
        dev_type, dev_id, lat, lon, raw_apps = line.strip().split("\t")
        apps = [int(a) for a in raw_apps.split(",") if a.isdigit()]
        lat, lon = float(lat), float(lon)
        ua = appsinstalled_pb2.UserApps()
        ua.lat = lat
        ua.lon = lon
        ua.apps.extend(apps)
        packed = ua.SerializeToString()
        unpacked = appsinstalled_pb2.UserApps()
        unpacked.ParseFromString(packed)
        assert ua == unpacked


if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-t", "--test", action="store_true", default=False)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--pattern", action="store", default="/data/appsinstalled/*.tsv.gz")
    op.add_option("--idfa", action="store", default="127.0.0.1:33013")
    op.add_option("--gaid", action="store", default="127.0.0.1:33014")
    op.add_option("--adid", action="store", default="127.0.0.1:33015")
    op.add_option("--dvid", action="store", default="127.0.0.1:33016")
    op.add_option("-w", "--workers", action="store", default=mp.cpu_count())
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    if opts.test:
        prototest()
        sys.exit(0)

    logging.info("Memc loader started with options: %s" % opts)
    try:
        main(opts)
    except Exception, e:
        logging.exception("Unexpected error: %s" % e)
        sys.exit(1)
