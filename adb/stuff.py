from enum import Enum
from typing import NamedTuple


class Status(Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTED = "USB"
    WIFI_READY = "WIFI_READY"
    WIFI = "WIFI"
    NO_DEVICES = "NO_DEVICES"

class Device(NamedTuple):
    name: str
    tags: dict


class MetaSingleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
