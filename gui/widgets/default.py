from ._imports import *

class DefaultContentWidget(QWidget):
    def __init__(self):
        super().__init__()
        text = QLabel('Перед началом работы необходимо включить режим разработичка и установить ADB драйвер (драйвер в Инструментах)')
        text.setAlignment(Qt.AlignHCenter)
        text.setWordWrap(True)
        vbox = QVBoxLayout()
        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        vbox.addWidget(text)
        btn = QPushButton('Как включить режим разработчика?')
        btn.clicked.connect(self.developer_mode)
        vbox.addWidget(btn)
        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setLayout(vbox)

    def developer_mode(self):
        dialog = DeveloperModeDialog(parent=self)
        dialog.exec()

class DeveloperModeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Как включить режим разработчика?')
        self.setFixedSize(700, 800)
        self.setModal(True)

        INSTRUCTIONS = [
            'Чтобы получить возможность устанавливать пиратки, прошивать шлем и т.д., нужно включить режим разработчика.\nДля этого\n\n'+
            'Нажмите на часы в правом нижнем углу\n'+
            '1. Зайдите в Настройки',

            '2. Нажмите на "Основные"\n'+
            '3. Нажмите на "Информация"',

            '4. Пролистайте вниз до "Версия ПО". Нажмите на нее 7 раз.\n'+
            'Появится вкладка "Разработчик"',

            '5. Зайдите в неё"\n'+
            'Включите отладку по USB.\nТеперь можно пользоваться программой.'
        ]

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignHCenter)

        for i, text in enumerate(INSTRUCTIONS):
            label = QLabel(text)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignHCenter)
            vbox.addWidget(label)

            pixmap = QPixmap(f'{config.get_root()}/gui/img/dev{i+1}.jpg')
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