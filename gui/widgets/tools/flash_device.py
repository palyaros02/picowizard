from .._imports import *

class FlashDeviceDialog(QDialog):
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

        self.create_widgets()
        self.init_layout()
        self.setup_ui()
        self.bind_events()

    def setup_ui(self):
        self.setWindowTitle('Прошивка шлема')
        self.setModal(False)
        self.update_firmwares()

    def create_widgets(self):
        self.radio_cn = QRadioButton('cn')
        self.radio_gl = QRadioButton('gl')
        self.combo_firmwares = QComboBox()
        self.btn_download = QPushButton('Скачать')
        self.download_progressbar = QProgressBar()
        self.download_progress_label = QLabel('', alignment=Qt.AlignCenter)
        self.btn_cancel_download = QPushButton('Отмена')
        self.btn_select_firmware = QPushButton('Выбрать свою прошивку')
        self.btn_push = QPushButton('Прошить (залить на шлем)')
        self.push_progressbar = QProgressBar()
        self.push_progress_label = QLabel('', alignment=Qt.AlignCenter)
        self.btn_cancel_push = QPushButton('Отмена')
        self.btn_instructions = QPushButton('Инструкция')

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
        self.push_progressbar.setRange(0, 100)
        self.push_progressbar.setValue(0)
        self.download_progressbar.setRange(0, 100)
        self.download_progressbar.setValue(0)

        self.__set_push_widgets_enabled(False)

        vbox = QVBoxLayout()
        if adb.get_device().tags['type'] == 'pico4':
            vbox.addWidget(QLabel('Ваш ro.oem.state: ' + str(self.oem_state)), alignment=Qt.AlignCenter)
            vbox.addWidget(QLabel('Версию прошивки понизить нельзя!', wordWrap=True, alignment=Qt.AlignCenter, styleSheet='color: red;'))

        vbox.addWidget(QLabel('Выберите прошивку для скачивания. Загрузка начинается не сразу, нужно немного подождать.', wordWrap=True, alignment=Qt.AlignCenter))

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
        hbox.addWidget(self.push_progressbar)
        hbox.addWidget(self.btn_cancel_push)
        vbox.addLayout(hbox)
        vbox.addWidget(self.push_progress_label)
        vbox.addWidget(self.btn_instructions)
        vbox.addWidget(QLabel('_' * 60))

        vbox.addWidget(QLabel('Псевдо-прошивка'))

        self.setLayout(vbox)

    def bind_events(self):
        self.radio_region.buttonClicked.connect(self.update_firmwares)
        self.btn_download.clicked.connect(self.download_firmware)
        self.btn_cancel_download.clicked.connect(self.cancel_download)
        self.btn_select_firmware.clicked.connect(self.select_firmware)
        self.btn_push.clicked.connect(self.push_firmware)
        self.btn_cancel_push.clicked.connect(self.cancel_push)
        self.btn_instructions.clicked.connect(self.show_instructions)

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
        self.combo_firmwares.addItems(list(firmwares.keys()))
        self.combo_firmwares.setCurrentIndex(0)
        for i in range(self.combo_firmwares.count()):
            self.combo_firmwares.setItemData(i, firmwares[self.combo_firmwares.itemText(i)])

    def get_firmware_url(self) -> str:
        data = self.combo_firmwares.currentData()
        return data

    def download_firmware(self):
        url = self.get_firmware_url()
        if url:
            file_name = url.split('/')[-1]
            dir = f"{config.get_root()}/downloads/firmwares/{self.device_type}/{self.oem_state_str}/{self.region}/{self.combo_firmwares.currentText()}"

            if not os.path.exists(dir):
                os.makedirs(dir)

            path = f"{dir}/{file_name}"

            self.downloader = Downloader(url, path)
            self.downloader.download_update_progress.connect(self.download_update_progress)
            self.downloader.download_update_label.connect(self.download_update_label)
            self.downloader.download_started.connect(self.download_started)
            self.downloader.download_cancelled.connect(self.download_cancelled)
            self.downloader.download_finished.connect(self.download_finished)
            self.downloader.download_error.connect(self.download_error)

            if os.path.exists(path):
                msg = QMessageBox()
                msg.setWindowTitle('Внимание')
                msg.setIcon(QMessageBox.Information)
                msg.setText('Файл уже существует')
                msg.setInformativeText('Хотите перезаписать или использовать его?')
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Apply | QMessageBox.Cancel)
                msg.button(QMessageBox.Yes).setText('Перезаписать')
                msg.button(QMessageBox.Apply).setText('Использовать')
                msg.button(QMessageBox.Cancel).setText('Отмена')
                msg.setDefaultButton(QMessageBox.Cancel)
                res = msg.exec_()
                if res == QMessageBox.Yes:
                    os.remove(path)
                    self.downloader.start()
                elif res == QMessageBox.Apply:
                    self.firmware_path = path
                    self.__set_download_widgets_enabled(False, 'Выбран скачанный ранее файл')
                    self.btn_cancel_download.setEnabled(True)
                    self.__set_push_widgets_enabled(True)
            else:
                self.downloader.start()
        else:
            msg = QMessageBox()
            msg.setWindowTitle('Ошибка')
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Прошивка не найдена')
            msg.setInformativeText('Попробуйте выбрать другую прошивку')
            msg.exec_()

    def cancel_download(self):
        self.__set_download_widgets_enabled(True)
        self.download_progressbar.setValue(0)
        if getattr(self, 'downloader', False):
            self.downloader.cancel()

    def __set_download_widgets_enabled(self, flag: bool, label_text: str = ''):
        self.radio_cn.setEnabled(flag)
        self.radio_gl.setEnabled(flag)
        self.combo_firmwares.setEnabled(flag)
        self.btn_download.setEnabled(flag)
        self.btn_cancel_download.setEnabled(flag)
        self.download_progressbar.setEnabled(flag)
        self.download_progress_label.setText(label_text)

    def __set_push_widgets_enabled(self, flag: bool, label_text: str = ''):
        self.btn_push.setEnabled(flag)
        self.btn_cancel_push.setEnabled(flag)
        self.push_progressbar.setEnabled(flag)
        self.push_progress_label.setEnabled(flag)
        self.push_progress_label.setText(label_text)

    def download_started(self):
        self.__set_download_widgets_enabled(False, 'Подготовка к скачиванию...')
        self.btn_cancel_download.setEnabled(True)
        self.btn_select_firmware.setEnabled(False)
        self.download_progressbar.setEnabled(True)
        self.download_progressbar.setValue(0)

    def download_cancelled(self):
        self.__set_download_widgets_enabled(True, 'Отменено')

    def download_finished(self):
        self.__set_download_widgets_enabled(True, 'Скачивание успешно завершено :)')
        self.btn_cancel_download.setEnabled(False)
        self.download_progressbar.setValue(100)
        self.firmware_path = self.downloader.path
        self.__set_push_widgets_enabled(True)

    def download_error(self, error: str):
        self.__set_download_widgets_enabled(True, 'Ошибка при загрузке :(')
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle('Ошибка')
        msg.setText('Ошибка при загрузке')
        msg.setInformativeText(error)
        msg.exec_()

    def download_update_progress(self, progress: int):
        self.download_progressbar.setValue(progress)

    def download_update_label(self, text: str):
        self.download_progress_label.setText(text)

    def select_firmware(self):
        path = f"{config.get_root()}/downloads/firmwares/"
        check_firmware = f'{self.device_type}/{self.oem_state_str}/{self.region}/{self.combo_firmwares.currentText()}'
        if os.path.exists(path + check_firmware):
            path += check_firmware
        file = str(QFileDialog.getOpenFileName(self, 'Выберите прошивку', path, '*.zip')[0])
        if not file:
            return
        self.firmware_path = file
        self.__set_download_widgets_enabled(False, 'Выбран пользовательский файл')
        self.btn_cancel_download.setEnabled(True)
        self.__set_push_widgets_enabled(True)

    def push_firmware(self):
        filename = self.firmware_path.split('/')[-1]
        local = self.firmware_path
        remote = '/storage/self/primary/dload/' + filename

        msg = QMessageBox()
        msg.setWindowTitle('Внимание')
        msg.setIcon(QMessageBox.Information)
        msg.setText('Подтверждение')
        msg.setInformativeText(f'Вы уверены, что хотите загрузить прошивку {filename} на устройство? \n\nЭто не приведет к непосредственной установке прошивки, а лишь загрузит ее на устройство. \n\nПосле загрузки прошивки на устройство, выведется дальнейшая инструкция по установке прошивки.')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.button(QMessageBox.Yes).setText('Да')
        msg.button(QMessageBox.Cancel).setText('Нет')
        msg.setDefaultButton(QMessageBox.Cancel)
        res = msg.exec_()
        if res == QMessageBox.Yes:
            self.pusher = Pusher(local, remote)
            self.pusher.push_started.connect(self.push_started)
            self.pusher.push_cancelled.connect(self.push_cancelled)
            self.pusher.push_finished.connect(self.push_finished)
            self.pusher.push_error.connect(self.push_error)
            self.pusher.push_update_progress.connect(self.push_update_progress)
            self.pusher.push_update_label.connect(self.push_update_label)
            self.pusher.start()

    def push_started(self):
        self.__set_push_widgets_enabled(True)
        self.push_progressbar.setValue(0)
        self.push_progress_label.setText('Начало загрузки...')
        self.btn_push.setEnabled(False)
        self.btn_cancel_download.setEnabled(False)
        self.btn_select_firmware.setEnabled(False)

    def push_cancelled(self):
        self.push_progressbar.setValue(0)
        self.__set_push_widgets_enabled(True, 'Отменено')

    def push_finished(self):
        self.__set_push_widgets_enabled(True, 'Завершено :)')
        self.push_progressbar.setValue(100)
        self.show_instructions()

    def show_instructions(self):
        dialog = FinishDialog(self)
        dialog.exec()

    def push_error(self, error: str):
        self.push_progressbar.setValue(0)
        self.__set_push_widgets_enabled(True, 'Ошибка :(')
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle('Ошибка')
        msg.setText('Ошибка при загрузке')
        msg.setInformativeText(error)
        msg.exec_()

    def push_update_progress(self, progress: int):
        self.push_progressbar.setValue(progress)

    def push_update_label(self, text: str):
        self.push_progress_label.setText(text)

    def cancel_push(self):
        self.pusher.cancel()

class FinishDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Инструкция по прошивке')
        self.setFixedSize(700, 800)
        self.setModal(True)

        INSTRUCTIONS = [
            'Поздравляем! Вы успешно загрузили прошивку на устройство. \nДля установки прошивки, выполните следующие действия:\n\n'+
            '1. Зайдите в Диспетчер файлов на устройстве\n'+
            '2. Перейдите в папку dload\n'+
            '3. Проверьте, что файл на месте. Если нет, то скачайте заново.',

            '4. Нажмите на часы в правом нижнем углу\n'+
            '5. Зайдите в Настройки\n',

            '6. Выберите вкладку Основные\n'+
            '7. Выберите пункт Версия системы',

            '8. Нажмите "Обновить в автономном режиме"\n\n'+
            'После этого прошивка начнет устанавливаться. Шлем несколько раз перезагрузится. \nПосле перезагрузки крайне рекомендуется сбросить настройки шлема до заводских, чтобы вычистить весь китайский мусор.\n\n' +
            'Поздравляю, теперь у вас глобалка/китаец (смотря что выбрали)!'
        ]

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignHCenter)

        for i, text in enumerate(INSTRUCTIONS):
            label = QLabel(text)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignHCenter)
            vbox.addWidget(label)

            pixmap = QPixmap(f'{config.get_root()}/gui/img/flashing{i+1}.jpg')
            pixmap = pixmap.scaledToWidth(630, Qt.SmoothTransformation)
            img = QLabel()
            img.setPixmap(pixmap)
            img.setAlignment(Qt.AlignHCenter)
            vbox.addWidget(img)

        self.btn_ok = QPushButton('Закрыть')
        self.btn_ok.clicked.connect(self.close)
        vbox.addWidget(self.btn_ok)

        widget = QWidget()
        widget.setLayout(vbox)
        scrollArea = QScrollArea()
        scrollArea.setWidget(widget)
        scrollArea.setWidgetResizable(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(scrollArea)
        self.setLayout(mainLayout)


class Downloader(QTimer):
    download_started = Signal()
    download_cancelled = Signal()
    download_finished = Signal()
    download_error = Signal(str)

    download_update_progress = Signal(int)
    download_update_label = Signal(str)

    def __init__(self, url: str, path: str):
        QTimer.__init__(self)
        self.setInterval(1000)
        self.timeout.connect(self.poll_download)

        self.url = url
        self.path = path
        self.cancelled = False

        self.total_size = 0
        self.wrote = 0

        self.download_thread = DownloaderThread(self.url, self.path, self.download_error)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.finished.connect(self.stop)
        self.download_thread.total_size_signal.connect(self.set_total_size)
        self.download_thread.wrote_signal.connect(self.set_wrote)

    def set_total_size(self, total_size: int):
        self.total_size = total_size

    def set_wrote(self, wrote: int):
        self.wrote = wrote

    def start(self) -> None:
        self.download_thread.start()
        self.download_started.emit()
        self.start_time = time.time()
        super().start()

    def cancel(self) -> None:
        super().stop()
        self.cancelled = True
        self.download_thread.cancel()
        self.download_cancelled.emit()

    def poll_download(self):
        total_size = self.total_size
        wrote = self.wrote
        percent = int(wrote * 100 / total_size) if total_size > 0 else 0

        time_diff = time.time() - self.start_time
        wrote = int(wrote / 1024 / 1024)
        total_size = round(total_size / 1024 / 1024, 2)
        speed = round(wrote / time_diff, 2) if time_diff > 0 else 0.01
        eta = (total_size - wrote) / speed if speed > 0 else 0

        label_text = f'{wrote} / {total_size} Mб, ({speed} Mб/с), ост. {int(eta // 60)} мин. {int(eta % 60)} сек.'
        if eta > 0:
            self.download_update_progress.emit(percent)
            self.download_update_label.emit(label_text)

class DownloaderThread(QThread):
    total_size_signal = Signal(object)
    wrote_signal = Signal(object)
    def __init__(self, url: str, path: str, download_error: Signal):
        QThread.__init__(self)
        self.url = url
        self.path = path
        self.download_error = download_error
        self.cancelled = False

    def run(self) -> None:
        response = requests.get(self.url, stream=True)
        self.total_size = int(response.headers.get('content-length', 0))
        self.total_size_signal.emit(self.total_size)
        block_size = 1024 * 1024 # 10 Mb
        self.wrote = 0
        try:
            if self.total_size == 0:
                raise Exception('Не удалось получить размер файла. Попробуйте скачать его вручную и выбрать.')
            with open(self.path, 'wb') as f:
                for data in response.iter_content(block_size):
                    if self.cancelled:
                        raise Exception('Отменено пользователем')
                    self.wrote += len(data)
                    f.write(data)
                    self.wrote_signal.emit(self.wrote)
        except Exception as e:
            if self.wrote != self.total_size:
                self.download_error.emit(str(e))
                os.remove(self.path)
        finally:
            self.finished.emit()

    def cancel(self) -> None:
        self.cancelled = True
        self.terminate()

class Pusher(QTimer):
    push_started = Signal()
    push_cancelled = Signal()
    push_finished = Signal()
    push_error = Signal(str)

    push_update_progress = Signal(int)
    push_update_label = Signal(str)

    def __init__(self, local: str, remote: str):
        QTimer.__init__(self)
        self.setInterval(1000)
        self.timeout.connect(self.poll_remote_size)

        self.local = local
        self.remote = remote
        self.cancelled = False
        self.error = None

        self.pusher_thread = PusherThread(self.local, self.remote, self.push_error)
        self.pusher_thread.push_error.connect(self.finisher)
        self.pusher_thread.finished.connect(self.finisher)


    def start(self) -> None:
        self.pusher_thread.start()
        self.push_started.emit()
        self.start_time = time.time()
        super().start()

    def cancel(self) -> None:
        self.pusher_thread.cancel()
        self.push_cancelled.emit()
        self.cancelled = True
        super().stop()

    def finisher(self):
        if self.cancelled:
            self.push_cancelled.emit()
        elif self.error:
            self.push_error.emit(self.error)
        else:
            self.push_finished.emit()
        self.stop()

    def poll_remote_size(self) -> None:
        ls_output = adb(f"shell ls -l {self.remote} | grep {self.remote.split('/')[-1]}")
        remote_size = int(ls_output.split()[4])
        local_size = os.path.getsize(self.local)
        percent = int(remote_size * 100 / local_size)

        time_diff = time.time() - self.start_time
        remote_size = round(remote_size / 1024 / 1024, 2)
        local_size = round(local_size / 1024 / 1024, 2)
        speed = round(remote_size / time_diff, 2) if time_diff > 0 else 0.01
        eta = (local_size - remote_size) / speed if speed > 0 else 0

        label_text = f'{remote_size} / {local_size} Mб, ({speed} Mб/с), ост. {int(eta // 60)} мин. {int(eta % 60)} сек.'

        self.push_update_progress.emit(percent)
        self.push_update_label.emit(label_text)


class PusherThread(QThread):
    def __init__(self, local: str, remote: str, push_error: Signal):
        QThread.__init__(self)
        self.local = local
        self.remote = remote
        self.push_error = push_error
        self.cancelled = False

    def run(self) -> None:
        try:
            if not self.local:
                print('Не выбран файл для загрузки')
                raise Exception('Не выбран файл для загрузки')
            self.push_process = adb.push(self.local, self.remote)
            self.push_process.wait()
        except Exception as e:
            self.push_error.emit(str(e))

    def cancel(self) -> None:
        self.cancelled = True
        if self.push_process:
            self.push_process.terminate()