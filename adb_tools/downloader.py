from gui.widgets._imports import *

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