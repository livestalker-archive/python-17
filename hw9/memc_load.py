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
import Queue

NORMAL_ERR_RATE = 0.01
AppsInstalled = collections.namedtuple("AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"])


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


def file_handler(q, res_q, device_memc, options):
    memc_pool = {}
    for d in device_memc:
        memc_pool[d] = memcache.Client([device_memc[d]])
    try:
        while True:
            seq, fn = q.get(True, 10)
            logging.info('Processing %s (seq: %s)' % (fn, seq))
            processed = errors = 0
            with gzip.open(fn) as fd:
                for line in fd:
                    line = line.strip()
                    if not line:
                        continue
                    appsinstalled = parse_appsinstalled(line)
                    if not appsinstalled:
                        errors += 1
                        continue
                    memc = memc_pool.get(appsinstalled.dev_type)
                    if not memc:
                        errors += 1
                        logging.error("Unknow device type: %s" % appsinstalled.dev_type)
                        continue
                    ok = insert_appsinstalled(memc, appsinstalled, options.dry)
                    if ok:
                        processed += 1
                    else:
                        errors += 1
            res_q.put((seq, fn, processed, errors))
    except Queue.Empty:
        logging.info('%s - queue empty.' % mp.current_process().name)


def res_handler(res_q):
    logging.info('Start results worker')
    current_seq = 0
    while True:
        try:
            res = res_q.get(True, 10)
            if res == 'STOP':
                if res_q.qsize() == 0:
                    break
                else:
                    res_q.put('STOP')
            seq, fn, processed, errors = res
            if current_seq == seq:
                if processed:
                    err_rate = float(errors) / processed
                    if err_rate < NORMAL_ERR_RATE:
                        logging.info("Acceptable error rate (%s). Successfull load" % err_rate)
                    else:
                        logging.error("High error rate (%s > %s). Failed load" % (err_rate, NORMAL_ERR_RATE))
                dot_rename(fn)
                logging.info('Rename %s (seq: %s)' % (fn, seq))
                current_seq += 1
            else:
                res_q.put(res)
        except Queue.Empty:
            continue


def main(options):
    device_memc = {
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
    }
    q = mp.Queue()
    res_q = mp.Queue()
    proc_args = (q, res_q, device_memc, options)
    seq = 0
    for fn in glob.iglob(options.pattern):
        q.put((seq, fn))
        seq += 1
    logging.info("Worker count: %s." % mp.cpu_count())
    proc_pool = [mp.Process(target=file_handler, args=proc_args) for _ in range(mp.cpu_count())]
    res_proc = mp.Process(target=res_handler, args=(res_q,))
    res_proc.daemon = True
    res_proc.start()
    for p in proc_pool:
        p.daemon = True
        p.start()

    for p in proc_pool:
        p.join()

    res_q.put('STOP')
    res_proc.join(10)
    if res_proc.is_alive():
        res_proc.terminate()


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
