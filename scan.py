#!/usr/bin/env python3

import curses
import argparse
import socket
import sys
import pyfiglet
import re
from scanner import Scanner


def parse_arguments():
    parse = argparse.ArgumentParser(
        description="You can scan your given ports and you can see ports status and service names")

    src = parse.add_argument_group("Input")
    src.add_argument("-t", "--target", metavar="Target", help="Target host", required=True)
    src.add_argument("-p", "--port", metavar="Port",
                     help="You can type one port or more like p1,p2,p3... "
                          "if you want to give range you have to type like MIN_PORT MAX_PORT ",
                     type=str, nargs="+")
    src.add_argument("--thread",
                     help="Thread number you can select between 1 and 200 if you don't select default is 100",
                     default=50,
                     type=int)
    src.add_argument("-f", "--file", metavar="Read file", help="Read ports from file")
    output = parse.add_argument_group("Output")
    output.add_argument("-w", "--write", metavar="Write", help="Write result to .txt or .json")

    args = parse.parse_args()

    return args


def get_ports_from_file(file_name):
    with open(file_name, "r") as f:
        data = f.read().splitlines()
        data = ",".join(data)
        if data:
            return data
        else:
            return None


def check_ip_valid(host):
    ip_format = re.compile(r"^[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}$")
    host = socket.gethostbyname(host)
    return True if ip_format.match(host) else False


def parse_ports(scr, ports: list):
    if len(ports) == 2 and all(map(lambda x: x.isdecimal() and 0 <= int(x) <= 65535, ports)):
        isrange = True
    elif all(map(lambda x: x.isdecimal() and 0 <= int(x) <= 65535, "".join(ports).replace(" ", "").split(","))):
        isrange = False
    else:
        scr.addstr(" Please enter valid arguments\n ")
        scr.refresh()
        scr.getch()
        curses.endwin()
        sys.exit(1)

    port_list = [*map(lambda x: int(x), "".join(ports).split(","))] if not isrange else range(int(ports[0]),
                                                                                              int(ports[1]) + 1)

    return port_list


def main():
    args = parse_arguments()
    scr = curses.initscr()
    scr.addstr(pyfiglet.figlet_format("  PortScanner V 1.4", width=110) + "\n\n")
    scr.refresh()

    if not check_ip_valid(args.target):
        scr.addstr(" Please enter valid ipv4 address\n ")
        scr.refresh()
        scr.getch()
        curses.endwin()
        sys.exit(1)

    ports = args.port

    if ports is None and args.file is None:
        scr.addstr(" Please add give ports!\n ")
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
            ports = get_ports_from_file(args.file)
            if ports is None:
                scr.addstr(" File is empty\n ")
                scr.refresh()
                scr.getch()
                curses.endwin()
                sys.exit(1)

    ports = parse_ports(scr, ports)
    scanner = Scanner(args.target, ports, args.thread)
    result = scanner.scan(scr)

    if args.write:
        result.write_to_file(args.write)

    scr.getch()
    curses.endwin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        curses.endwin()
