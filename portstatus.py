import csv
import curses
import json
import os

from portinfo import PortInfo


class PortStatus:
    def __init__(self, ports_info: list[PortInfo], t, scr):
        self.TIME = t
        self.screen = scr
        self.PORTS_INFO: list[PortInfo] = ports_info

    def print_status(self, scr):

        scr.addstr(
            "\n\n\n"
            + " " * 4
            + "Port"
            + " " * 8
            + "Status"
            + " " * 8
            + "Service\n"
            + " " * 2
            + "-" * 38
            + "\n"
        )
        scr.refresh()

        for port_info in sorted(self.PORTS_INFO, key=lambda x: x.port):
            self.screen.addstr(
                " " * 4
                + str(port_info.port)
                + " " * 8
                + port_info.status
                + " " * 10
                + port_info.service
                + "\n"
            )
        self.screen.refresh()

        self.screen.addstr(f"\n\n  Scanning completed in {self.TIME:.2f} seconds")

    def write_to_file(self, output_path):
        if output_path:
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    dict_data = [
                        {
                            "port": port_info.port,
                            "status": port_info.status,
                            "service": port_info.service,
                        }
                        for port_info in sorted(self.PORTS_INFO, key=lambda x: x.port)
                    ]
                    if output_path.endswith(".txt"):
                        f.writelines(
                            f"{port_info.port} {port_info.status} {port_info.service}\n"
                            for port_info in sorted(
                                self.PORTS_INFO, key=lambda x: x.port
                            )
                        )

                    elif output_path.endswith(".json"):

                        json.dump(dict_data, f)

                    elif output_path.endswith(".csv"):
                        writer = csv.DictWriter(
                            f, ["port", "status", "service"], delimiter=";"
                        )
                        writer.writeheader()
                        writer.writerows(dict_data)

                    self.screen.addstr(f"\n\n  Saved to {os.path.abspath(output_path)}")
            except OSError:
                self.screen.addstr(" Output file not found!\n")
                self.screen.getch()
                curses.endwin()
