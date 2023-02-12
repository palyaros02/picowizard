from .._imports import *

class FlashDeviceDialog(QDialog):
    """
    vbox:
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
        self.firmware_path = ''

        self.setWindowTitle('Прошивка шлема')

        self.create_widgets()
        self.init_layout()
        self.bind_events()

    @Slot(int)
    def get_speed(self, speed: int):
        self.download_speed = int(speed)

    @Slot(int)
    def get_wrote(self, wrote: int):
        self.download_wrote = int(wrote)

    @Slot(int)
    def get_size(self, size: int):
        self.download_size = int(size)

    @Slot(int)
    def get_progress(self, progress: int):
        self.download_progress = progress

    def create_widgets(self):
        self.radio_cn = QRadioButton('cn')
        self.radio_gl = QRadioButton('gl')
        self.combo_firmwares = QComboBox()
        self.btn_download = QPushButton('Скачать')
        self.download_progressbar = QProgressBar()
        self.download_progress_label = QLabel('', alignment=Qt.AlignCenter) # type: ignore
        self.btn_cancel_download = QPushButton('Отмена')
        self.btn_select_firmware = QPushButton('Выбрать свою прошивку')
        self.btn_push = QPushButton('Прошить')
        self.push_progress = QProgressBar()
        self.btn_cancel_push = QPushButton('Отмена')

        self.downloader_signals = DownloaderSignals()
        self.download_speed = 0
        self.download_wrote = 0
        self.download_size = 0
        self.download_progress = 0
        self.download_timer = QTimer()

    def init_layout(self):
        self.radio_region = QButtonGroup()
        self.radio_region.addButton(self.radio_cn)
        self.radio_region.addButton(self.radio_gl)
        self.radio_region.setExclusive(True)
        self.radio_gl.setChecked(True)
        self.push_progress.setRange(0, 100)
        self.push_progress.setValue(0)
        self.download_progressbar.setRange(0, 100)
        self.download_progressbar.setValue(0)

        vbox = QVBoxLayout()
        if adb.get_device().tags['type'] == 'pico4':
            vbox.addWidget(QLabel('Ваш ro.oem.state: ' + str(self.oem_state)), alignment=Qt.AlignCenter) # type: ignore
            vbox.addWidget(QLabel('Версию прошивки понизить нельзя!', wordWrap=True, alignment=Qt.AlignCenter, styleSheet='color: red;')) # type: ignore

        vbox.addWidget(QLabel('Выберите прошивку для скачивания. Загрузка начинается не сразу, нужно немного подождать.', wordWrap=True, alignment=Qt.AlignCenter)) # type: ignore

        hbox = QHBoxLayout()
        frame = QFrame()
        frame_hbox = QHBoxLayout()
        frame_hbox.addWidget(self.radio_cn)
        frame_hbox.addWidget(self.radio_gl)
        frame_hbox.setContentsMargins(2, 2, 2, 2)
        frame.setLayout(frame_hbox)
        frame.setFixedWidth(80)
        hbox.addWidget(frame)

        hbox.addWidget(self.combo_firmwares)
        hbox.addWidget(self.btn_download)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.download_progressbar)
        hbox.addWidget(self.btn_cancel_download)
        vbox.addLayout(hbox)
        vbox.addWidget(self.download_progress_label)
        vbox.addWidget(self.btn_select_firmware)

        vbox.addWidget(self.btn_push)
        hbox = QHBoxLayout()
        hbox.addWidget(self.push_progress)
        hbox.addWidget(self.btn_cancel_push)
        vbox.addLayout(hbox)
        text = QLabel('Если процент загрузки файла на шлем не меняется, то попробуйте перезагрузить шлем. Кнопка есть в "Инструментах"', wordWrap=True, alignment=Qt.AlignCenter, styleSheet='color: red;') # type: ignore
        vbox.addWidget(text)
        vbox.addWidget(QLabel('_' * 60))

        vbox.addWidget(QLabel('Псевдо-прошивка'))

        self.setLayout(vbox)

    def bind_events(self):
        self.update_firmwares()
        self.radio_region.buttonClicked.connect(self.update_firmwares)
        self.btn_download.clicked.connect(self.download_firmware)
        self.btn_cancel_download.clicked.connect(self.cancel_download)
        self.btn_select_firmware.clicked.connect(self.select_firmware)
        self.btn_push.clicked.connect(self.push_firmware)
        self.btn_cancel_push.clicked.connect(self.cancel_push)
        self.downloader_signals.download_progress.connect(self.get_progress)
        self.downloader_signals.download_finished.connect(self.download_finished)
        self.downloader_signals.download_error.connect(self.download_error)
        self.downloader_signals.download_started.connect(self.download_started)
        self.downloader_signals.download_cancelled.connect(self.download_cancelled)
        self.downloader_signals.download_wrote.connect(self.get_wrote)
        self.downloader_signals.download_speed.connect(self.get_speed)
        self.downloader_signals.download_size.connect(self.get_size)

    def get_firmwares(self) -> dict[str, str]:
        self.device_type = adb.get_device().tags['type']
        self.oem_state_str = 'oem' if self.oem_state else 'non_oem'
        self.region = self.radio_region.checkedButton().text()
        if self.device_type == 'pico4':
            return firmware[self.device_type][self.oem_state_str][self.region]
        else:
            return firmware[self.device_type][self.region]

    def update_firmwares(self):
        self.combo_firmwares.clear()
        firmwares = self.get_firmwares()
        self.combo_firmwares.addItems(firmwares.keys()) # type: ignore
        self.combo_firmwares.setCurrentIndex(0)
        for i in range(self.combo_firmwares.count()):
            self.combo_firmwares.setItemData(i, firmwares[self.combo_firmwares.itemText(i)])

    def get_firmware_url(self) -> str:
        data = self.combo_firmwares.currentData()
        return data

    def download_firmware(self):
        url = self.get_firmware_url()
        if url:
            self.download_progress_label.setText('Подготовка к скачиванию...')
            file_name = url.split('/')[-1]
            dir = f"{config.get_root()}/downloads/firmwares/{self.device_type}/{self.oem_state_str}/{self.region}"
            if not os.path.exists(dir):
                os.makedirs(dir)
            path = f"{dir}/{file_name}"
            self.downloader = Downloader(url, path, self.downloader_signals)
            if os.path.exists(path):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle('Внимание')
                msg.setText('Файл уже существует')
                msg.setInformativeText('Хотите перезаписать или использовать его?')
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Apply | QMessageBox.Cancel) # type: ignore
                msg.button(QMessageBox.Yes).setText('Перезаписать')
                msg.button(QMessageBox.Apply).setText('Использовать')
                msg.button(QMessageBox.Cancel).setText('Отмена')
                msg.setDefaultButton(QMessageBox.Cancel)
                res = msg.exec_()
                if res == QMessageBox.Yes:
                    self.downloader.delete_file(path)
                    self.downloader.start()
                elif res == QMessageBox.Apply:
                    self.firmware_path = path
                    self.download_progress_label.setText('Выбран скачанный файл')
            else:
                self.downloader.start()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Прошивка не найдена')
            msg.setInformativeText('Попробуйте выбрать другую прошивку')
            msg.setWindowTitle('Ошибка')
            msg.exec_()

    def select_firmware(self):
        file = QFileDialog.getOpenFileName(self, 'Выберите прошивку', f"{config.get_root()}/downloads/firmwares/", '*.zip')[0]
        self.firmware_path = file
        self.download_progress_label.setText('Выбран пользовательский файл')
        self.download_progressbar.setValue(0)
        self.download_progressbar.setEnabled(False)
        self.radio_cn.setEnabled(False)
        self.radio_gl.setEnabled(False)
        self.combo_firmwares.setEnabled(False)
        self.btn_download.setEnabled(False)

    def cancel_download(self):
        try:
            self.downloader.cancel()
        except AttributeError:
            self.radio_cn.setEnabled(True)
            self.radio_gl.setEnabled(True)
            self.combo_firmwares.setEnabled(True)
            self.btn_download.setEnabled(True)
            self.download_progressbar.setEnabled(True)
            self.firmware_path = ''
            self.download_progress_label.setText('')

    def download_started(self, started: bool):
        self.btn_cancel_download.setEnabled(True)
        self.btn_download.setEnabled(False)
        self.radio_cn.setEnabled(False)
        self.radio_gl.setEnabled(False)
        self.combo_firmwares.setEnabled(False)
        self.btn_select_firmware.setEnabled(False)
        self.download_progressbar.setValue(0)
        self.update_download_progress()
        self.download_timer = QTimer()
        self.download_timer.timeout.connect(self.update_download_progress)
        self.download_timer.start(1000)

    def download_cancelled(self, cancelled: bool):
        self.btn_cancel_download.setEnabled(False)
        self.btn_download.setEnabled(True)
        self.radio_cn.setEnabled(True)
        self.radio_gl.setEnabled(True)
        self.combo_firmwares.setEnabled(True)
        self.btn_select_firmware.setEnabled(True)
        self.download_progress_label.setText('Отменено')
        self.download_timer.stop()

    def download_finished(self, path: str):
        self.btn_cancel_download.setEnabled(False)
        self.btn_download.setEnabled(True)
        self.radio_cn.setEnabled(True)
        self.radio_gl.setEnabled(True)
        self.combo_firmwares.setEnabled(True)
        self.btn_select_firmware.setEnabled(True)
        self.download_progressbar.setValue(100)
        self.download_progress_label.setText('Завершено')
        self.firmware_path = path
        self.download_timer.stop()

    def download_error(self, error: str):
        self.btn_cancel_download.setEnabled(False)
        self.btn_download.setEnabled(True)
        self.radio_cn.setEnabled(True)
        self.radio_gl.setEnabled(True)
        self.combo_firmwares.setEnabled(True)
        self.btn_select_firmware.setEnabled(True)
        self.download_progress_label.setText('Ошибка')
        self.download_timer.stop()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle('Ошибка')
        msg.setText('Ошибка при загрузке')
        msg.setInformativeText(error)
        msg.exec_()

    def update_download_progress(self):
        self.download_progressbar.setValue(self.download_progress)
        total_size = round(self.download_size / 1024 / 1024, 2)
        wrote = round(self.download_wrote / 1024 / 1024, 2)
        speed = round(self.download_speed / 1024 / 1024, 2)
        eta = round((total_size - wrote) / speed / 60, 1) if speed > 0 else '∞'
        text = f'{wrote} / {total_size} Mб, ({speed} Mб/с), ост. {eta} мин.'
        self.download_progress_label.setText(text)
        # print(self.download_progress, self.download_wrote, self.download_size, self.download_speed)


    def push_firmware(self):
        pass

    def cancel_push(self):
        pass

class DownloaderSignals(QObject):
    download_progress = Signal(int)
    download_error = Signal(str)
    download_finished = Signal(str)
    download_started = Signal(bool)
    download_cancelled = Signal(bool)
    download_wrote = Signal(object) # Mb
    download_size = Signal(object) # Mb
    download_speed = Signal(object) # Mb/s

class Downloader(QThread):
    def __init__(self,url: str, path: str, signals: DownloaderSignals):
        QThread.__init__(self)
        self.cancelled = False
        self.signals = signals
        self.url = url
        self.path = path

    def run(self) -> None:
        response = requests.get(self.url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024 # 10 Mb
        wrote = 0
        start_time = int(time.time())
        try:
            with open(self.path, 'wb') as f:
                self.signals.download_started.emit(True)
                self.signals.download_size.emit(total_size)
                for data in response.iter_content(block_size):
                    if self.cancelled:
                        self.signals.download_cancelled.emit(True)
                        break
                    wrote = wrote + len(data)
                    f.write(data)
                    percent = int(wrote * 100 / total_size)
                    time_diff = int(time.time() - start_time)
                    speed = int(wrote // time_diff)
                    self.signals.download_progress.emit(percent)
                    self.signals.download_wrote.emit(wrote)
                    self.signals.download_speed.emit(speed)
                else:
                    self.delete_file()
            if not self.cancelled:
                self.signals.download_finished.emit(self.path)
        except Exception as e:
            if wrote != total_size:
                self.signals.download_error.emit(str(e))
            else:
                self.signals.download_finished.emit(self.path)

    def cancel(self) -> None:
        self.cancelled = True

    def delete_file(self, path=None) -> None:
        if path:
            os.remove(path)
        else:
            os.remove(self.path)
