#!/usr/bin/env python3

import argparse
import curses
import re
import socket
import sys

import pyfiglet

from scanner import Scanner


def parse_arguments():
    parse = argparse.ArgumentParser(
        description="You can scan your given ports and see ports status and service names"
    )

    src = parse.add_argument_group("Input")
    src.add_argument(
        "-t", "--target", metavar="Target", help="Target host", required=True
    )
    src.add_argument(
        "-p",
        "--port",
        metavar="Port",
        help="Multiple ports PORT1,PORT2,PORT3... or port range MIN_PORT MAX_PORT",
        type=str,
        nargs="+",
    )
    src.add_argument(
        "--max-connections",
        type=int,
        default=100,
        help="Maximum number of concurrent connections",
    )

    src.add_argument("-f", "--file", metavar="Read", help="Read ports from file")
    output = parse.add_argument_group("Output")
    output.add_argument(
        "-w", "--write", metavar="Write", help="Write result to *.txt, *.json or *.csv"
    )

    args = parse.parse_args()

    return args


def read_ports_from_file(file_name):

    with open(file_name, "r") as f:
        data = f.read().splitlines()
        data = ",".join(data)
        if data:
            return data
        else:
            return None


def parse_target(host):
    ip_format = re.compile(r"^[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}$")
    host = socket.gethostbyname(host)

    if ip_format.match(host):
        return host
    return None


def parse_ports(ports: list):

    port_list = None

    if len(ports) == 1 and ports[0] == "-":
        port_list = range(65536)
    elif len(ports) == 2 and all(x.isdecimal() and 0 <= int(x) <= 65535 for x in ports):
        port_list = range(int(ports[0]), int(ports[1]) + 1)

    elif all(x.isdecimal() and 0 <= int(x) <= 65535 for x in "".join(ports).split(",")):
        port_list = (int(x) for x in "".join(ports).split(","))

    return port_list


def main():
    args = parse_arguments()
    scr = curses.initscr()
    scr.addstr(pyfiglet.figlet_format("  PortScanner V 1.4", width=110) + "\n\n")
    scr.refresh()

    host = parse_target(args.target)

    if host is None:

        scr.addstr(" Please enter valid host\n ")
        scr.refresh()
        scr.getch()
        curses.endwin()
        sys.exit(1)

    ports = args.port

    if ports is None and args.file is None:
        scr.addstr(" Please add ports!\n ")
        scr.refresh()
        scr.getch()
        curses.endwin()
        sys.exit(1)

    if args.file:
        if args.port:
            scr.addstr(" You cannot get ports from more then one options!\n ")
            scr.refresh()
            scr.getch()
            curses.endwin()
            sys.exit(1)
        else:
            ports = read_ports_from_file(args.file)
            if ports is None:
                scr.addstr(" File is empty\n ")
                scr.refresh()
                scr.getch()
                curses.endwin()
                sys.exit(1)

    ports = parse_ports(ports)

    if ports is None:
        scr.addstr(" Please enter valid ports\n ")
        scr.refresh()
        scr.getch()
        curses.endwin()
        sys.exit(1)

    scanner = Scanner(args.max_connections)
    result = scanner.scan(scr, host, ports)

    result.print_status(scr)

    if args.write:
        result.write_to_file(args.write)

    scr.getch()
    curses.endwin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        curses.endwin()
