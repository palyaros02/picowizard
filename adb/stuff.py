from enum import Enum
from typing import NamedTuple
import os, subprocess, time


class Status(Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTED = "CONNECTED"
    WIFI_READY = "WIFI_READY"
    WIFI = "WIFI"
    NO_DEVICES = "NO_DEVICES"

class Device(NamedTuple):
    name: str
    tags: dict

class ADBOutput():
    def __init__(self, process: subprocess.Popen, wait: bool = True) -> None:
        self.process = process
        self.result = None
        if wait:
            self.result = _ADBTools._get_adb_process_result(self.process)
    def __getattr__(self, attr: str):
        return getattr(self.result, attr)

class MetaSingleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class _ADBTools():

    DEBUG = False

    def __init__(self) -> None:
        self._adbpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'platform-tools', 'adb.exe')
        self._device = None
        self._connected_status: Status = Status.DISCONNECTED

    def __call__(self, *args, wait: bool = True, **kwargs) -> ADBOutput:
        _process = self._create_adb_process(*args, **kwargs)
        return ADBOutput(_process, wait=wait)

    def is_connected(self) -> bool:
        return self._connected_status not in [Status.DISCONNECTED, Status.NO_DEVICES]

    def is_wifi(self) -> bool:
        return self._connected_status == Status.WIFI

    def is_wifi_ready(self) -> bool:
        return self._connected_status in (Status.WIFI_READY, Status.WIFI)

    def is_usb(self) -> bool:
        return self._connected_status == Status.CONNECTED

    def get_connection_status(self) -> str:
        return self._connected_status.value

    def _start_tcpip(self, port: int=5555) -> None:
        try:
            self(f'tcpip {port}')
            self._connected_status = Status.WIFI_READY
        except Exception as e:
            raise Exception('Failed to start tcpip!\n' + str(e))

    def _parse_ip(self) -> str:
        if self.is_wifi_ready():
            for _ in range(10):
                try:
                    adb_output = self('shell ip addr show wlan0', wait=True)
                    if adb_output:
                        adb_output = adb_output.splitlines()
                        break
                except:
                    time.sleep(0.5)
                    continue
            for line in adb_output: # type: ignore
                if 'inet ' in line:
                    return line.split()[1].split('/')[0]
            raise Exception('Ip not found in wlan0 interface. Is the device connected to a network?')
        else:
            self._start_tcpip()
            return self._parse_ip()

    def _parse_args(self, args: tuple[str]) -> list[str]:
        _args = []
        for arg in args:
            if isinstance(arg, list):
                _args.extend(arg)
            else:
                _args.extend(arg.split())
        return _args

    def _create_adb_process(self, *args, **kwargs) -> subprocess.Popen:
        args = self._parse_args(args)
        adb = fr'{self._adbpath} -s {self._device.name}'.split() if self._device else [self._adbpath]
        if self.DEBUG:
            print('command:', ' '.join(adb + args))
        process = subprocess.Popen(adb + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', **kwargs)
        return process

    @staticmethod
    def _get_adb_process_result(process: subprocess.Popen) -> str:
        process.wait()
        if process.returncode != 0:
            stderr = process.stderr.read().strip() # type: ignore
            stdout = process.stdout.read().strip() # type: ignore
            raise Exception(f"ADB command \n\t" +
                            f"{' '.join(process.args)}\n" + # type: ignore
                            f"failed with code {process.returncode}" + ('' if not stderr else f': {stderr}'))
        return process.stdout.read().strip() # type: ignore

    def _kill_process(self, process: subprocess.Popen) -> None:
        process.kill()