#!/usr/bin/env python3

from os.path import dirname, realpath
import os
import sys
import socket
import errno
import struct
import logging
from argparse import ArgumentParser

sys.path.append(dirname(realpath(__file__)))

from virtualsmartcard.utils import inttostring, hexdump
from patch_card.vpc import (
    vpc_connect,
    vpc_send,
    vpc_recv,
)

def parse_args():
    """Parse commandline arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "-H", "--host", default="localhost")
    parser.add_argument(
        "-p", "--port", type=int, default=35963)
    parser.add_argument(
        "-s", "--pcsc-sock-name",
        default="/var/run/old_pcscd.comm")
    parser.add_argument(
        "-r", "--reader-num", type=int, default=0)
    return parser.parse_args()


# From VirtualSmartcard.py
VPCD_CTRL_LEN = 1
VPCD_CTRL_OFF = 0
VPCD_CTRL_ON = 1
VPCD_CTRL_RESET = 2
VPCD_CTRL_ATR = 4

def main(args):
    """Simulate Virtual SC Card"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  [%(levelname)s] %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S")

    # Patch environment
    os.environ["PCSCLITE_CSOCK_NAME"] = args.pcsc_sock_name

    # Connect to virtual card server
    sock = vpc_connect(args.host, args.port)

    # Import here, so the environment is patched before
    # loading the python `smartcard` package
    from patch_card.cards import PatchCard, SimulCard
    # card_os = PatchCard(args.reader_num)
    card_os = SimulCard()

    while True:
        try:
            (size, msg) = vpc_recv(sock)
        except socket.error as err:
            logging.info(err)
            sys.exit()

        if not size:
            logging.error(
                "error in communication protocol (missing size parameter)")
        elif size == VPCD_CTRL_LEN:
            if msg == inttostring(VPCD_CTRL_OFF):
                logging.info("power down")
                card_os.powerDown()
            elif msg == inttostring(VPCD_CTRL_ON):
                logging.info("power up")
                card_os.powerUp()
            elif msg == inttostring(VPCD_CTRL_RESET):
                logging.info("reset")
                card_os.reset()
            elif msg == inttostring(VPCD_CTRL_ATR):
                vpc_send(sock, card_os.getATR())
            else:
                logging.info("unknown control command")
        else:
            if size != len(msg):
                logging.error(
                    "expected %u bytes, but received only %u",
                    size, len(msg))

            answer = card_os.execute(msg)
            logging.info("response APDU (%d bytes):\n  %s\n",
                len(answer), hexdump(answer, indent=2))
            vpc_send(sock, answer)


if __name__ == "__main__":
    args = parse_args()
    main(args)
