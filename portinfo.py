from dataclasses import dataclass


@dataclass
class PortInfo:
    port: int
    service: str
    status: str
