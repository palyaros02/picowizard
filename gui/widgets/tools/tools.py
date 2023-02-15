from .._imports import *
from .change_region import ChangeRegionDialog
from .flash_device import FlashDeviceDialog
from .install_app import InstallAppDialog
from .manage_apps import ManageAppsDialog
from .run_adb_command import RunAdbCommandDialog

class ToolsContentWidget(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.create_widgets()
        self.init_layout()
        self.bind_events()

    def create_widgets(self):
        self.btn_install_driver = QPushButton('Установить драйвер ADB')
        self.btn_restart_server = QPushButton('Перезапустить сервер ADB')
        self.btn_reboot_device = QPushButton('Перезагрузить шлем')
        self.btn_enable_wifi = QPushButton('USB -> WiFi (ждать)')
        self.btn_disable_wifi = QPushButton('WiFi -> USB')
        self.btn_install_app = QPushButton('Установить приложение')
        self.btn_manage_apps = QPushButton('Управление приложениями')
        self.btn_run_adb_command = QPushButton('Выполнить команду')
        self.btn_switch_region = QPushButton('Переключить регион')
        self.btn_flash_device = QPushButton('Прошить шлем')
        self.btn_usb_tethering = QPushButton('Вкл/выкл режим модема')

    def init_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn_install_driver)
        self.btn_install_driver.setToolTip('Установить драйвер ADB для подключения к шлему по USB')
        vbox.addWidget(self.btn_restart_server)
        vbox.addWidget(self.btn_reboot_device)

        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_enable_wifi)
        hbox.addWidget(self.btn_disable_wifi)
        vbox.addLayout(hbox)

        vbox.addWidget(self.btn_install_app)
        vbox.addWidget(self.btn_manage_apps)
        vbox.addWidget(self.btn_run_adb_command)
        vbox.addWidget(self.btn_switch_region)
        vbox.addWidget(self.btn_flash_device)
        vbox.addWidget(self.btn_usb_tethering)

        #disable buttons
        if adb.get_device().tags['type'] == 'PICO3':
            self.btn_switch_region.setText('Смена региона доступна только на PICO4')
            self.btn_switch_region.setEnabled(False)
        self.btn_install_app.setEnabled(False)
        self.btn_manage_apps.setEnabled(False)
        self.btn_run_adb_command.setEnabled(False)
        self.btn_usb_tethering.setEnabled(False)

        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setLayout(vbox)

    def bind_events(self):
        self.btn_install_driver.clicked.connect(adb.install_driver)
        self.btn_restart_server.clicked.connect(self.restart_server)
        self.btn_reboot_device.clicked.connect(self.reboot_device)
        self.btn_enable_wifi.clicked.connect(self.connect_wifi)
        self.btn_disable_wifi.clicked.connect(self.disconnect_wifi)
        self.btn_switch_region.clicked.connect(self.switch_region)
        self.btn_flash_device.clicked.connect(self.flash_device)
        self.btn_install_app.clicked.connect(self.install_app)
        self.btn_manage_apps.clicked.connect(self.manage_apps)
        self.btn_run_adb_command.clicked.connect(self.run_adb_command)

    def restart_server(self):
        ans = MsgConfirm(parent=self).exec()
        if ans == QMessageBox.Yes:
            self.window.restart_adb()

    def reboot_device(self):
        # FIXIT:
        ans = MsgConfirm(parent=self).exec()
        if ans == QMessageBox.Yes:
            adb.reboot_device()

    def connect_wifi(self):
        adb.connect_wifi()

    def disconnect_wifi(self):
        adb.disconnect_wifi()
        adb.connect_usb()

    def switch_region(self):
        change_region_dialog = ChangeRegionDialog(parent=self)
        change_region_dialog.setModal(True)
        change_region_dialog.exec()

    def flash_device(self):
        flash_device_dialog = FlashDeviceDialog(parent=self)
        flash_device_dialog.setModal(True)
        flash_device_dialog.exec()

    def install_app(self):
        install_app_dialog = InstallAppDialog(parent=self)
        install_app_dialog.setModal(True)
        install_app_dialog.exec()

    def manage_apps(self):
        manage_apps_dialog = ManageAppsDialog(parent=self)
        manage_apps_dialog.setModal(True)
        manage_apps_dialog.exec()

    def run_adb_command(self):
        run_adb_command_dialog = RunAdbCommandDialog(parent=self)
        run_adb_command_dialog.setModal(True)
        run_adb_command_dialog.exec()

class MsgConfirm(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Question)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)  # type: ignore
        self.setDefaultButton(QMessageBox.No)
        self.setText('Вы уверены?')
        self.setInformativeText('Не пользуйтесь инструментами, пока устройство не переподключится')
        self.setWindowTitle('Подтверждение')