import asyncio
import socket
import time

from portinfo import PortInfo
from portstatus import PortStatus


class Scanner:
    def __init__(self, max_connections):
        self.max_connections = max_connections

    def scan(self, scr, host, ports):

        scr.addstr(f"  Scanning started on host {host}...")
        scr.refresh()

        begin = time.time()

        ports_info = asyncio.run(self._scanner(host, ports))

        end = time.time()

        ports_info = list(filter(lambda x: x is not None, ports_info))

        return PortStatus(ports_info, end - begin, scr)

    async def _scan(self, sem, host, port):
        async with sem:
            try:

                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port), timeout=2
                )

                laddr = writer.get_extra_info("sockname")
                raddr = writer.get_extra_info("peername")

                writer.close()
                await writer.wait_closed()

                if laddr and raddr and laddr[0] == raddr[0] and raddr[1] == laddr[1]:
                    return None

                status = "open"

            except asyncio.TimeoutError:
                status = "closed|filtered"

            except (ConnectionRefusedError, OSError):
                return None

        try:
            service = socket.getservbyport(port) + " (guess)"
        except OSError:
            service = "Unknown"

        return PortInfo(port, service, status)

    async def _scanner(self, host, ports):

        sem = asyncio.Semaphore(self.max_connections)

        results = await asyncio.gather(*[self._scan(sem, host, port) for port in ports])

        return results
