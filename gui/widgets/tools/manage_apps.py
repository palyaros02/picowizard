from .._imports import *

class ManageAppsDialog(QDialog):
    """
    мусор от копилота
    Управление приложениями:
            Список установленных приложений
            Бэкап приложений
            Включение/выключение приложений
            Удаление приложений
            Управление правами
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_widgets()
        self.init_layout()
        self.bind_events()

    def create_widgets(self):
        self.combo_apps = QComboBox()

        self.btn_uninstall = QPushButton('Удалить')
        self.btn_select_app = QPushButton('Выбрать своё приложение')
        self.btn_cancel_uninstall = QPushButton('Отмена')

        self.uninstall_progress = QProgressBar()

    def init_layout(self):
        self.uninstall_progress.setRange(0, 100)
        self.uninstall_progress.setValue(0)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel('Выберите приложение для удаления:'))
        hbox = QHBoxLayout()
        hbox.addWidget(self.combo_apps)
        hbox.addWidget(self.btn_uninstall)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.uninstall_progress)
        hbox.addWidget(self.btn_cancel_uninstall)
        vbox.addLayout(hbox)

        vbox.addWidget(self.btn_select_app)

        self.setLayout(vbox)

    def bind_events(self):
        pass

    def get_apps(self):
        pass

    def uninstall_app(self):
        pass