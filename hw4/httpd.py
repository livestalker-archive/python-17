#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import logging
import socket
import StringIO
from multiprocessing import Process as P, Queue as Q
from multiprocessing.reduction import ForkingPickler

from otus import request as req


def forking_dumps(obj):
    buf = StringIO.StringIO()
    ForkingPickler(buf).dump(obj)
    return buf.getvalue()


class HTTPd(object):
    """Web Server"""

    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.doc_root = kwargs['doc_root']
        self.workers_count = kwargs['workers_count']
        self.listen_socket = None
        self.clients = Q()
        self.workers = None

    def run_server(self):
        """Run server"""
        self.init_listen_socket()
        self.listening_loop()

    def stop_server(self):
        self.listen_socket.close()

    def listening_loop(self):
        """Listening loop"""
        logging.info('Start listening loop.')
        while True:
            connection, address = self.listen_socket.accept()
            logging.debug('Client with address: %s connected.', address)
            self.clients.put(forking_dumps(connection))
            self.process(connection)
            connection.close()

    def process(self, connection):
        """Process connection."""
        request = req.create_request(connection)
        handler = req.RequestHandler(self.doc_root, request)
        response = handler.process()
        octets = response.get_octets()
        connection.sendall(octets)
        logging.info(self._access_log_message(request, response, len(octets)))

    def init_listen_socket(self):
        """Init listening socket."""
        ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # man 7 socket
        ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ls.bind((self.host, self.port))
        ls.listen(1)
        self.listen_socket = ls
        logging.info('Init listening socket.')

    def worker_loop(self):
        print os.getpid()
        pass

    @staticmethod
    def _access_log_message(request, response, bytes_sent):
        """Create access log message."""
        return '{} {} {}'.format(request.uri,
                                 response.code,
                                 bytes_sent)


def test():
    print os.getpid()
    pass


def _run_workers():
    workers = [P(target=test) for _ in range(3)]
    map(lambda x: x.start(), workers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web server')
    parser.add_argument('-r', required=True, dest='doc_root', help='Document root')
    parser.add_argument('-w', default=1, dest='workers_count', help='Worker count')
    parser.add_argument('-a', default='localhost', dest='host', help='Web server bind address')
    parser.add_argument('-p', default=8080, dest='port', help='Web server port')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    if not os.path.exists(args.doc_root):
        logging.error('Document root: {} does not exists.'.format(args.web_root))

    httpd = HTTPd(host=args.host,
                  port=args.port,
                  doc_root=os.path.realpath(args.doc_root),
                  workers_count=args.workers_count)
    try:
        _run_workers()
        httpd.run_server()
    except KeyboardInterrupt:
        httpd.stop_server()
