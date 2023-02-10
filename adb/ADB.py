import os

from stuff import MetaSingleton, Status, Device
import os, subprocess, time

class ADBOutput():
        def __init__(self, process: subprocess.Popen, wait: bool = True) -> None:
            self.process = process
            self.result = None
            if wait:
                self.result = ADB.__get_adb_process_result(self.process)
        def __getattr__(self, attr: str):
            return getattr(self.result, attr)

class ADB(metaclass=MetaSingleton):
    DEBUG = False
    """
    TODO:
        [*] __call__ for custom adb commands
        [*] get_devices() for getting devices
        [*] finding PICO device and setting it as default
        [*] device info
        [*] connect_wifi() for connecting to wifi
        [*] disconnect_wifi() for disconnecting from wifi
        [*] start and kill adb server
        [*] install driver
        [] enable usb tethering via `adb shell am start -n com.android.settings/.TetherSettings && adb shell input keyevent 20 && adb shell input keyevent 20 && adb shell input keyevent KEYCODE_ENTER && sleep 2 && adb shell input keyevent 4` -- does not work
        [] file transfer with returning progress
        [] apk installation/uninstallation/launching/disabling/enabling
            [] do not forget obb files
        [*] reboot
        [] shell
        [] apps management:
            [] list with getting pictures
            [] file backup
    """

    def __init__(self) -> None:
        self._adbpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'platform-tools', 'adb.exe')
        self._device = None
        self._connected_status: Status = Status.DISCONNECTED

    def __call__(self, *args, wait: bool = True, **kwargs) -> ADBOutput:
        _process = self.__create_adb_process(*args, **kwargs)
        return ADBOutput(_process, wait=wait)

    @staticmethod
    def install_driver() -> None:
        os.startfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'driver', 'driver.exe'))

    def get_devices_list(self) -> list[Device]:
        adb_output = self('devices -l').splitlines()
        devices_lines_list = [line.split() for line in adb_output if line.split().count('device') == 1]
        # ['ID device product:Phoenix_ovs model:A8110 device:PICOA8110 transport_id:4', ...]
        if not devices_lines_list:
            self._connected_status = Status.NO_DEVICES
            raise Exception('No devices found')
        else:
            self._connected_status = Status.DISCONNECTED if not self.is_connected() else self._connected_status
        devices = []
        for device_line in devices_lines_list:
            device_name = device_line[0]
            device_tags = dict([tag.split(':') for tag in device_line[2:]])
            devices.append(Device(device_name, device_tags))
        return devices

    def get_device(self) -> Device:
        if not self._device:
            self._connected_status = Status.DISCONNECTED
            raise Exception('PICO is not connected')
        return self._device

    def connect(self) -> None:
        devices = self.get_devices_list()
        for device in devices:
            if device.tags['device'].startswith('PICO'):
                self._device = device
                if device.name.endswith('5555'):
                    self._connected_status = Status.WIFI
                    break
                self._connected_status = Status.CONNECTED if not self.is_wifi_ready() else Status.WIFI_READY

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

    def start_server(self) -> None:
        self('start-server')
        print('Server started')
        self.connect_usb()

    def kill_server(self) -> None:
        print('Killing server')
        self('kill-server')
        self._connected_status = Status.NO_DEVICES
        self._device = None

    def restart_server(self) -> None:
        self.kill_server()
        self.start_server()

    def reboot_device(self) -> None:
        print('Rebooting device, please wait...')
        self('reboot')

    def connect_usb(self) -> None:
        self('connect usb')

    def connect_wifi(self, port: int=5555) -> None:
        if self.is_wifi():
            print('Already connected to wifi')
            return
        if not self.is_wifi_ready():
            self.__start_tcpip(port)
            # time.sleep(2)
        self(f'connect {self.__parse_ip()}:{port}')
        self.connect()

    def disconnect_wifi(self) -> None:
        if self.is_wifi():
            self('disconnect')
            self.connect()


    def install_apk(self):
        """
        adb shell pm install [-lrtsfdgw] [-i PACKAGE] [--user USER_ID|all|current]
        [-p INHERIT_PACKAGE] [--install-location 0/1/2]
        [--install-reason 0/1/2/3/4] [--originating-uri URI]
        [--referrer URI] [--abi ABI_NAME] [--force-sdk]
        [--preload] [--instantapp] [--full] [--dont-kill]
        [--enable-rollback]
        [--force-uuid internal|UUID] [--pkg PACKAGE] [-S BYTES] [--apex]
        [PATH|-]
        Install an application.  Must provide the apk data to install, either as a
        file path or '-' to read from stdin.  Options are:
        -l: forward lock application
        -R: disallow replacement of existing application
        -t: allow test packages
        -i: specify package name of installer owning the app
        -s: install application on sdcard
        -f: install application on internal flash
        -d: allow version code downgrade (debuggable packages only)
        -p: partial application install (new split on top of existing pkg)
        -g: grant all runtime permissions
        -S: size in bytes of package, required for stdin
        --user: install under the given user.
        --dont-kill: installing a new feature split, don't kill running app
        --restrict-permissions: don't whitelist restricted permissions at install
        --originating-uri: set URI where app was downloaded from
        --referrer: set URI that instigated the install of the app
        --pkg: specify expected package name of app being installed
        --abi: override the default ABI of the platform
        --instantapp: cause the app to be installed as an ephemeral install app
        --full: cause the app to be installed as a non-ephemeral full app
        --install-location: force the install location:
            0=auto, 1=internal only, 2=prefer external
        --install-reason: indicates why the app is being installed:
            0=unknown, 1=admin policy, 2=device restore,
            3=device setup, 4=user request
        --force-uuid: force install on to disk volume with given UUID
        --apex: install an .apex file, not an .apk


        adb push apk.apk /data/local/tmp
        adb shell pm install /data/local/tmp/apk.apk
        adb shell rm /data/local/tmp/apk.apk


    def execute(cmd):
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for line in popen.stdout:
            print(line.decode(), end='')
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    # Example
    for path in execute(["locate", "a"]):
        print(path, end="")




    def execute(command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Poll process for new output until finished
        while True:
            nextline = process.stdout.readline()
            if nextline == '' and process.poll() is not None:
                break
            sys.stdout.write(nextline)
            sys.stdout.flush()

        output = process.communicate()[0]
        exitCode = process.returncode

        if (exitCode == 0):
            return output
        else:
            raise ProcessException(command, exitCode, output)
        """
        pass

    def uninstall_app(self):
        """
        pm uninstall [-k] [--user USER_ID] [--versionCode VERSION_CODE] PACKAGE [SPLIT]
        Remove the given package name from the system.  May remove an entire app
        if no SPLIT name is specified, otherwise will remove only the split of the
        given app.  Options are:
        -k: keep the data and cache directories around after package removal.
        --user: remove the app from the given user.
        --versionCode: only uninstall if the app has the given version code.
        """
        pass

    def push(self):
        """
        adb push [-a] [-p] [-r] [-t DATE] [-T DATE] [-v] LOCAL... REMOTE
        Copy files/directories to device.  If LOCAL is a directory, it will be
        copied recursively.  Use -a to copy file permissions.  Use -p to preserve
        file modification times.  Use -r to copy directories recursively.  Use -v
        to see the names of files as they are being copied.  Use -t to specify
        the time of the file on the device.  Use -T to specify the time of the file
        on the host.  If -t and -T are not specified, the current time will be used.
        """
        pass

    def pull(self):
        pass

    def get_apps(self):
        pass

    #=== Private Methods ===#

    def __start_tcpip(self, port: int=5555) -> None:
        try:
            self(f'tcpip {port}')
            self._connected_status = Status.WIFI_READY
        except Exception as e:
            raise Exception('Failed to start tcpip!\n' + str(e))

    def __parse_ip(self) -> str:
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
            self.__start_tcpip()
            return self.__parse_ip()

    def __parse_args(self, args: tuple[str]) -> list[str]:
        _args = []
        for arg in args:
            if isinstance(arg, list):
                _args.extend(arg)
            else:
                _args.extend(arg.split())
        return _args

    def __create_adb_process(self, *args, **kwargs) -> subprocess.Popen:
        args = self.__parse_args(args)
        adb = fr'{self._adbpath} -s {self._device.name}'.split() if self._device else [self._adbpath]
        if self.DEBUG:
            print('command:', ' '.join(adb + args))
        process = subprocess.Popen(adb + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', **kwargs)
        return process

    @staticmethod
    def __get_adb_process_result(process: subprocess.Popen) -> str:
        process.wait()
        if process.returncode != 0:
            stderr = process.stderr.read().strip() # type: ignore
            stdout = process.stdout.read().strip() # type: ignore
            raise Exception(f"ADB command \n\t" +
                            f"{' '.join(process.args)}\n" + # type: ignore
                            f"failed with code {process.returncode}" + ('' if not stderr else f': {stderr}'))
        return process.stdout.read().strip() # type: ignore

    @staticmethod
    def kill_process(process: subprocess.Popen) -> None:
        process.kill()