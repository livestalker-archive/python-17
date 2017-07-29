#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import logging
import socket

import req


# форматы
# Request-Line   = Method SP Request-URI SP HTTP-Version CRLF


class HTTPd(object):
    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.doc_root = kwargs['doc_root']
        self.listen_socket = None

    def run_server(self):
        self.init_listen_socket()
        self.listening_loop()

    def stop_server(self):
        self.listen_socket.close()

    def listening_loop(self):
        logging.info('Start listening loop.')
        while True:
            connection, address = self.listen_socket.accept()
            logging.info('Client with address: %s connected.', address)
            req.create_request(connection)
            connection.close()

    def init_listen_socket(self):
        ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # доступные опции можно посмотреть man 7 socket
        ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ls.bind((self.host, self.port))
        ls.listen(1)
        self.listen_socket = ls
        logging.info('Init listenning socket.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web server')
    parser.add_argument('-r', required=True, dest='doc_root', help='Document root')
    parser.add_argument('-w', default=1, dest='workers', help='Worker count')
    parser.add_argument('-a', default='localhost', dest='host', help='Web server bind address')
    parser.add_argument('-p', default=8080, dest='port', help='Web server port')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    if not os.path.exists(args.doc_root):
        logging.error('Document root: {} does not exists.'.format(args.web_root))

    httpd = HTTPd(host=args.host, port=args.port, doc_root=args.doc_root)
    try:
        httpd.run_server()
    except KeyboardInterrupt:
        httpd.stop_server()
