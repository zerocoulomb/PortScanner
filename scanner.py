import socket
import re
import threading

from exceptions import InvalidThreadCountError
from portstatus import PortStatus
import time
from concurrent.futures import ThreadPoolExecutor


class Scanner:

    def __init__(self,host, ports,thread_count):

        self.HOST = host
        self.server = None
        self.lock = threading.Lock()
        self.ip_format = re.compile(r"^[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}$")
        if thread_count < 1 or thread_count > 200:
            raise InvalidThreadCountError("You have to select thread count between 1 and 200")
        self.THREADS = thread_count
        self.ports = ports
        self.open_ports = []


    def scan(self, scr):
        scr.addstr(f"  Scanning started on host {self.HOST}...\n")
        scr.addstr(
            "\n\n" + " " * 4 + "Port" + " " * 8 + "Status" + " " * 8 + "Service\n" + " " * 2 + "-" * 38 + "\n")
        scr.refresh()

        begin = time.time()

        with ThreadPoolExecutor(max_workers=self.THREADS) as executor:
            futures = [executor.submit(self._scan,port, scr) for port in self.ports]
            for future in futures:
                result = future.result()
                if result:
                    self.open_ports.append(result)

        end = time.time()

        scr.addstr("\n\n  Scanning completed in {:.2f} seconds".format(end-begin))
        scr.refresh()


        return PortStatus(self.open_ports, end - begin, scr)

    def _scan(self, port, scr):
        server = None
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(1.5)

            if server.connect_ex((self.HOST, port)) == 0:
                try:
                    banner = socket.getservbyport(port)
                except:
                    banner = "unknown"

                with self.lock:
                    scr.addstr(" " * 4 + str(port) + " " * 8 + "open" + " " * 10 + banner+ "\n")
                    scr.refresh()

                return (port, banner)

            return None

        except:
            return None
        finally:
            if server:
                server.close()