from .._imports import *

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
