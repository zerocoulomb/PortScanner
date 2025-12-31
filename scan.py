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
    src.add_argument("target", metavar="Target", help="Target host", type=str)
    src.add_argument("-p", "--port", metavar="Port",
                     help="You can type one port or more like p1 p2 p3..."
                          "if you want to give range you have to type like MIN_PORT-MAX_PORT",
                     type=str, nargs="+")
    src.add_argument("-t", "--thread",
                     help="Thread number you can select between 1 and 100",
                     default=50,
                     type=int)
    src.add_argument("--max-retries", metavar="Max retries", type=int, default=3)
    src.add_argument("-f", "--file", metavar="Read file", help="Read ports from file")
    output = parse.add_argument_group("Output")
    output.add_argument("-w", "--write", metavar="Write", help="Write result to .txt or .json")

    args = parse.parse_args()

    return args


def get_ports_from_file(file_name):
    with open(file_name, "r") as f:
        data = f.read().splitlines()
        return data


def check_ip_valid(host):
    ip_format = re.compile(r"^[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}$")
    host = socket.gethostbyname(host)
    return True if ip_format.match(host) else False


def parse_ports(scr, ports: list):
    if all(map(lambda x: x.isdecimal() and 0 <= int(x) <= 65535, ports)):
        return [*map(lambda x: int(x), ports)]

    elif len(ports) == 1:
        ports_range = ports[0].split("-")

        if len(ports_range) == 2 and ports_range[0].isdecimal() and ports_range[1].isdecimal() \
                and int(ports_range[0]) < int(ports_range[1]) and int(ports_range[0]) >= 0:
            return range(int(ports_range[0]), int(ports_range[1]) + 1)

    quit_with_message(scr, " Please enter valid arguments\n ")


def quit_with_message(scr, message):
    scr.addstr(message)
    scr.refresh()
    scr.getch()
    curses.endwin()
    sys.exit(1)


def main():
    args = parse_arguments()
    scr = curses.initscr()
    scr.addstr(pyfiglet.figlet_format("  PortScanner V 1.4", width=110) + "\n\n")
    scr.refresh()

    if not check_ip_valid(args.target):
        quit_with_message(scr, " Please enter valid ipv4 address\n ")

    ports = args.port

    if ports is None and args.file is None:
        quit_with_message(scr, " Ports aren't given\n ")
    if args.file:
        if args.port:
            quit_with_message(scr, " You cannot get ports from more then one options!\n ")

        else:
            ports = get_ports_from_file(args.file)
            if ports is None:
                quit_with_message(scr, " File is empty\n ")

    ports = parse_ports(scr, ports)

    if args.thread and (args.thread < 1 or args.thread > 100):
        quit_with_message(scr, " Thread count should be between 1 and 100\n ")

    if args.max_retries:
        if args.max_retries < 0:
            quit_with_message(scr, " Please enter valid max retry number\n ")

    scanner = Scanner(args.target, ports, args.thread, args.max_retries)
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
