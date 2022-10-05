"""
This module is based upon virtualsmartcard/VirtualSmartcard.py
and is a wrapper for the communications protocoll in use by
the daemon.
"""

import socket
import errno
import struct
import logging

_Csizeof_short = len(struct.pack('h', 0))

def vpc_connect(host, port):
    """Connect to vpcd"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock


def vpc_send(sock, msg):
    """ Send a message to the vpcd """
    if isinstance(msg, str):
        sock.sendall(struct.pack('!H', len(msg)) + bytes(map(ord,msg)))
    else:
        sock.sendall(struct.pack('!H', len(msg)) + msg)


def vpc_recv(sock):
    """ Receive a message from the vpcd """
    # receive message size
    while True:
        try:
            sizestr = sock.recv(_Csizeof_short)
        except socket.error as err:
            if err.errno == errno.EINTR:
                continue
        break

    if len(sizestr) == 0:
        logging.error("Virtual PCD shut down")
        raise socket.error

    size = struct.unpack('!H', sizestr)[0]

    # receive and return message
    if size:
        while True:
            try:
                msg = sock.recv(size)
            except socket.error as err:
                if err.errno == errno.EINTR:
                    continue
            break
        if len(msg) == 0:
            logging.error("Virtual PCD shut down")
            raise socket.error
    else:
        msg = None

    return size, msg
