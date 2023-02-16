from gui.widgets._imports import *

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