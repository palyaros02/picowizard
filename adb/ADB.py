import os

from stuff import _ADBTools, MetaSingleton, Status, Device, ADBOutput

class ADB(_ADBTools, metaclass=MetaSingleton):
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
        super().__init__()

    def __call__(self, *args, wait: bool = True, **kwargs) -> ADBOutput:
        return super().__call__(*args, wait=wait, **kwargs)

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
            self._start_tcpip(port)
            # time.sleep(2)
        self(f'connect {self._parse_ip()}:{port}')
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