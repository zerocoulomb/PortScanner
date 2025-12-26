import csv
import os
import json
import curses


class PortStatus:
    def __init__(self, port_list, t, scr):
        self.TIME = t
        self.screen = scr
        self.PORT_LIST = port_list

    def write_to_file(self, output_path):
        if output_path:
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    dict_data = [{"port": port, "service": service} for port, service in
                                 sorted(self.PORT_LIST)]
                    if output_path.endswith(".txt"):
                        for port, service in sorted(self.PORT_LIST):
                            f.write(f"{port} open {service}\n")

                    elif output_path.endswith(".json"):
                        json.dump(dict_data, f)
                    elif output_path.endswith(".csv"):
                        writer = csv.DictWriter(f,fieldnames=["port", "service"])
                        writer.writeheader()
                        writer.writerows(dict_data)


                    self.screen.addstr("\n  Saved to {}\n".format(os.path.abspath(output_path)))
            except OSError:
                self.screen.addstr(" Output file not found!\n")
                self.screen.getch()
                curses.endwin()
