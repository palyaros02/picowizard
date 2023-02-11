from .._imports import *

class InstallAppDialog(QDialog):
    """
    мусор от копилота
    Установка программ:
            Выбор файла apk
            Выбор файла obb
            Кнопка установить
            Прогресс бар
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_widgets()
        self.init_layout()
        self.bind_events()

    def create_widgets(self):
        self.combo_apps = QComboBox()

        self.btn_install = QPushButton('Установить')
        self.btn_select_app = QPushButton('Выбрать своё приложение')
        self.btn_cancel_install = QPushButton('Отмена')

        self.install_progress = QProgressBar()

    def init_layout(self):
        self.install_progress.setRange(0, 100)
        self.install_progress.setValue(0)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel('Выберите приложение для установки:'))
        hbox = QHBoxLayout()
        hbox.addWidget(self.combo_apps)
        hbox.addWidget(self.btn_install)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.install_progress)
        hbox.addWidget(self.btn_cancel_install)
        vbox.addLayout(hbox)

        vbox.addWidget(self.btn_select_app)

        self.setLayout(vbox)

    def bind_events(self):
        pass

    def get_apps(self):
        pass

    def install_app(self):
        pass