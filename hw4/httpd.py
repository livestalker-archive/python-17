#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import time
import os
import logging
import socket
import threading
import Queue

from otus import request as req


class HTTPd(threading.Thread):
    """Web Server"""

    def __init__(self, host, port, doc_root, workers_count, **kwargs):
        super(HTTPd, self).__init__(**kwargs)
        self.host = host
        self.port = port
        self.doc_root = doc_root
        self.workers_count = workers_count
        self.q = Queue.Queue()
        self.listen_socket = None
        self.workers = []
        self._stop_signal = threading.Event()

    def run(self):
        """Run thread."""
        self._run_server()

    def _run_server(self):
        """Run server"""
        self.init_listen_socket()
        self._run_workers()
        self.listening_loop()

    def stop_server(self):
        """Stop Web server."""
        self._stop_signal.set()
        self.listen_socket.close()
        for w in self.workers:
            w.stop()
            w.join()

    def listening_loop(self):
        """Listening loop"""
        logging.info('Start listening loop.')
        while not self._stop_signal.is_set():
            connection, address = self.listen_socket.accept()
            logging.debug('Client with address: %s connected.', address)
            self.q.put(connection)

    def init_listen_socket(self):
        """Init listening socket."""
        ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # man 7 socket
        ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ls.bind((self.host, self.port))
        ls.listen(1)
        self.listen_socket = ls
        logging.info('Init listening socket.')

    def _run_workers(self):
        """Create and run workers."""
        for i in range(self.workers_count):
            w = Worker(self.q, self.doc_root, name='WebServer worker#{}'.format(i))
            w.start()
            self.workers.append(w)


class Worker(threading.Thread):
    # Queue.get timeout in seconds
    Q_TIMEOUT = 5

    def __init__(self, q, doc_root, **kwargs):
        super(Worker, self).__init__(**kwargs)
        self.q = q
        self._stop_event = threading.Event()
        self.doc_root = doc_root

    def process(self, connection):
        """Process connection."""
        request = req.create_request(connection)
        handler = req.RequestHandler(self.doc_root, request)
        response = handler.process()
        octets = response.get_octets()
        connection.sendall(octets)
        logging.info(self._access_log_message(request, response, len(octets)))

    def run(self):
        """Main loop of worker."""
        logging.info('%s started.', self.name)
        while not self._stop_event.is_set():
            try:
                c = self.q.get(True, self.Q_TIMEOUT)
                self.process(c)
                c.close()
            except Queue.Empty:
                # run loop again, no data in queue
                pass
        logging.info('%s stop.', self.name)

    def stop(self):
        """Set flag for stopping worker loop."""
        self._stop_event.set()

    @staticmethod
    def _access_log_message(request, response, bytes_sent):
        """Create access log message."""
        return '{} {} {}'.format(request.uri,
                                 response.code,
                                 bytes_sent)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web server')
    parser.add_argument('-r', required=True, dest='doc_root', help='Document root')
    parser.add_argument('-w', default=1, type=int, dest='workers_count', help='Worker count')
    parser.add_argument('-a', default='localhost', dest='host', help='Web server bind address')
    parser.add_argument('-p', default=8080, type=int, dest='port', help='Web server port')
    parser.add_argument('-l', default='WARN', dest='log_level', help='Log level', choices=['DEBUG', 'INFO', 'WARN', 'ERROR'])
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level, logging.WARN),
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    if not os.path.exists(args.doc_root):
        logging.error('Document root: {} does not exists.'.format(args.web_root))

    httpd = HTTPd(args.host,
                  args.port,
                  os.path.realpath(args.doc_root),
                  args.workers_count)
    httpd.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        httpd.stop_server()
