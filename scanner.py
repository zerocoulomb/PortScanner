import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from portstatus import PortStatus


class Scanner:

    def __init__(self, host, ports, thread_count, max_retries):

        self.HOST = host
        self.server = None
        self.lock = threading.Lock()
        self.THREADS = thread_count
        self.ports = ports
        self.max_retries = max_retries
        self.open_ports = []

    def scan(self, scr):
        scr.addstr(f"  Scanning started on host {self.HOST}...\n")
        scr.addstr(
            "\n\n" + " " * 4 + "Port" + " " * 8 + "Status" + " " * 8 + "Service\n" + " " * 2 + "-" * 38 + "\n")
        scr.refresh()

        begin = time.time()

        with ThreadPoolExecutor(max_workers=self.THREADS) as executor:
            futures = [executor.submit(self._scan, port, scr) for port in self.ports]
            for future in futures:
                result = future.result()
                if result:
                    self.open_ports.append(result)

        end = time.time()

        scr.addstr("\n\n  Scanning completed in {:.2f} seconds".format(end - begin))
        scr.refresh()

        return PortStatus(self.open_ports, end - begin, scr)

    def _scan(self, port, scr):

        for attempt in range(self.max_retries):
            server = None
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.settimeout(1.5)

                if server.connect_ex((self.HOST, port)) == 0:
                    if self.HOST in ("127.0.0.1", "localhost", "::1"):
                        local_addr = server.getsockname()
                        remote_addr = server.getpeername()

                        if local_addr[1] == remote_addr[1]:
                            server.close()
                            time.sleep(0.01 * attempt)
                            continue

                    try:
                        banner = socket.getservbyport(port)
                    except:
                        banner = "unknown"

                    with self.lock:
                        scr.addstr(" " * 4 + str(port) + " " * 8 + "open" + " " * 10 + banner + "\n")
                        scr.refresh()

                    return port, banner

                return None

            except (socket.error, socket.timeout):
                return None
            finally:
                if server:
                    server.close()
        return None
