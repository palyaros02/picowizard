from ._imports import *

class ToolsContentWidget(QWidget):
    """
    Инструменты:

        Установка программ:
            Выбор файла apk
            Выбор файла obb
            Кнопка установить
            Прогресс бар

        Управление приложениями:
            Список установленных приложений
            Бэкап приложений
            Включение/выключение приложений
            Удаление приложений
            Управление правами

        Выполнить команду:
            Ввод команды
            Кнопка выполнить
            Вывод команды
        """
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.init_layout()
        self.bind_events()

    def create_widgets(self):
        self.btn_install_driver = QPushButton('Установить драйвер ADB')
        self.btn_restart_server = QPushButton('Перезапустить сервер ADB (ждать)')
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
        # self.btn_switch_region.setEnabled(False)
        # self.btn_flash_device.setEnabled(False)
        self.btn_usb_tethering.setEnabled(False)

        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setLayout(vbox)

    def bind_events(self):
        self.btn_install_driver.clicked.connect(adb.install_driver)
        self.btn_restart_server.clicked.connect(adb.restart_server)
        self.btn_reboot_device.clicked.connect(adb.reboot_device)
        self.btn_enable_wifi.clicked.connect(self.connect_wifi)
        self.btn_disable_wifi.clicked.connect(self.disconnect_wifi)
        self.btn_switch_region.clicked.connect(self.switch_region)
        self.btn_flash_device.clicked.connect(self.on_flash_device)

    def connect_wifi(self):
        adb.connect_wifi()

    def disconnect_wifi(self):
        adb.disconnect_wifi()
        adb.connect_usb()

    def switch_region(self):
        change_region_dialog = ChangeRegionDialog(parent=self)
        change_region_dialog.setModal(True)
        change_region_dialog.exec()

    def on_flash_device(self):
        flash_device_dialog = FlashDeviceDialog(parent=self)
        flash_device_dialog.setModal(True)
        flash_device_dialog.exec()


class ChangeRegionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_widgets()
        self.init_layout()
        self.bind_events()

    def create_widgets(self):
        self.setWindowTitle('Изменение региона')
        self.current_region = QLabel('Текущий регион: ' + adb.get_region())
        self.new_region = QLabel('Введите новый регион:')
        self.new_region_input = QLineEdit()
        self.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel) # type: ignore

    def init_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.current_region)
        vbox.addWidget(self.new_region)
        vbox.addWidget(self.new_region_input)
        vbox.addWidget(self.btns)
        self.setLayout(vbox)

    def bind_events(self):
        self.btns.accepted.connect(self.on_ok)
        self.btns.rejected.connect(self.reject)

    def on_ok(self):
        if len(self.new_region_input.text()) != 2:
            message = QMessageBox(self)
            message.setText('Регион должен состоять из 2 символов')
            message.setIcon(QMessageBox.Warning)
            message.setWindowTitle('Ошибка')
            return message.exec()
        adb.set_region(self.new_region_input.text().upper())
        if adb.get_region() == self.new_region_input.text():
            message = QMessageBox(self)
            message.setText('Регион успешно изменен')
            message.setIcon(QMessageBox.Information)
            message.setWindowTitle('Успех')
            message.exec()
            self.accept()
        else:
            message = QMessageBox(self)
            message.setText('Ошибка при установке региона')
            message.setIcon(QMessageBox.Critical)
            message.setWindowTitle('Ошибка')
            return message.exec()

class FlashDeviceDialog(QDialog):
    """
    vbox:
        Label: ваш ro.oem.state : {adb.get_oem_state()}
        Выберите прошивку для скачивания:
        hbox:
            radio: cn, gl
            Список прошивок из firmware для pico4 согласно oem.state и региона, должен обновляться при изменении региона
            кнопка "скачать"
        Файлы скачиваются в папку downloads/firmware/pico4/{oem.state}/{region}/{version}
        Прогрессбар скачивания, кнопка отмены. Во время скачивания переключение региона и выбор прошивки недоступны
        Кнопка "Выбрать свою прошивку" - открывает диалог выбора файла. Если файл выбран, то кнопка "скачать" становится неактивной, кнопка "Выбрать свою прошивку" изменяется на "Сбросить выбор"
        Кнопка "Прошить". При нажатии открывается диалог подтверждения. При подтверждении происходит adb.push(путь к файлу прошивки, /storage/self/primary/dload). adb.push() возвращает subprocess.Popen. На основании процентов выполнения команды обновляется прогрессбар. После успешного выполнения команды открывается всплывающее окно с инструкциями.
        Прогрессбар загрузки файла, кнопка отмены. Во время загрузки все кнопки кроме отмены недоступны.
        Линия разделитель
        label "Псевдо-прошивка"
    """
    def __init__(self, parent=None):
        # super().__init__(parent) # TODO update style.qss
        super().__init__()
        oem_state = adb.get_oem_state()
        if oem_state == '':
            oem_state = False
        else:
            oem_state = True
        self.oem_state = oem_state

        self.create_widgets()
        self.init_layout()
        self.bind_events()

    def create_widgets(self):
        self.radio_cn = QRadioButton('cn')
        self.radio_gl = QRadioButton('gl')

        self.combo_firmwares = QComboBox()

        self.btn_download = QPushButton('Скачать')
        self.btn_flash = QPushButton('Прошить')
        self.btn_select_firmware = QPushButton('Выбрать свою прошивку')
        self.btn_cancel_download = QPushButton('Отмена')
        self.btn_cancel_push = QPushButton('Отмена')

        self.download_progress = QProgressBar()
        self.push_progress = QProgressBar()


    def init_layout(self):
        self.radio_region = QButtonGroup()
        self.radio_region.addButton(self.radio_cn)
        self.radio_region.addButton(self.radio_gl)
        self.radio_region.setExclusive(True)
        self.radio_gl.setChecked(True)
        self.push_progress.setRange(0, 100)
        self.push_progress.setValue(0)
        self.download_progress.setRange(0, 100)
        self.download_progress.setValue(0)

        vbox = QVBoxLayout()
        text = 'Ваш ro.oem.state: ' + str(self.oem_state)
        vbox.addWidget(QLabel(text))
        vbox.addWidget(QLabel('Выберите прошивку для скачивания:'))
        hbox = QHBoxLayout()
        # create a frame to hold the radio buttons
        frame = QFrame()
        frame_hbox = QHBoxLayout()
        # frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        # create a horizontal box layout and add the radio buttons
        frame_hbox.addWidget(self.radio_cn)
        frame_hbox.addWidget(self.radio_gl)
        # make frame fit the radio buttons
        frame_hbox.setContentsMargins(2, 2, 2, 2)
        frame.setLayout(frame_hbox)
        frame.setFixedWidth(80)
        hbox.addWidget(frame)
        hbox.addWidget(self.combo_firmwares)
        hbox.addWidget(self.btn_download)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.download_progress)
        hbox.addWidget(self.btn_cancel_download)
        vbox.addLayout(hbox)
        vbox.addWidget(self.btn_select_firmware)

        vbox.addWidget(self.btn_flash)
        hbox = QHBoxLayout()
        hbox.addWidget(self.push_progress)
        hbox.addWidget(self.btn_cancel_push)
        vbox.addLayout(hbox)
        text = QLabel('Если процент загрузки файла на шлем не меняется, то попробуйте перезагрузить шлем. Кнопка есть в "Инструментах"', wordWrap=True, alignment=Qt.AlignCenter, styleSheet='color: red;') # type: ignore
        vbox.addWidget(text)
        vbox.addWidget(QLabel('_' * 50))

        vbox.addWidget(QLabel('Псевдо-прошивка'))

        self.setLayout(vbox)

    def bind_events(self):
        pass

    def get_oem_state(self):
        pass

    def get_firmwares(self):
        pass

    def download_firmware(self):
        pass