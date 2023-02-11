from .._imports import *

class RunAdbCommandDialog(QDialog):
    """
    мусор от копилота
    Выполнить команду:
            Ввод команды
            Кнопка выполнить
            Вывод команды
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_widgets()
        self.init_layout()
        self.bind_events()

    def create_widgets(self):
        self.combo_commands = QComboBox()

        self.btn_run_command = QPushButton('Запустить')
        self.btn_cancel_command = QPushButton('Отмена')

        self.command_progress = QProgressBar()

    def init_layout(self):
        self.command_progress.setRange(0, 100)
        self.command_progress.setValue(0)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel('Выберите команду для запуска:'))
        hbox = QHBoxLayout()
        hbox.addWidget(self.combo_commands)
        hbox.addWidget(self.btn_run_command)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.command_progress)
        hbox.addWidget(self.btn_cancel_command)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def bind_events(self):
        pass
