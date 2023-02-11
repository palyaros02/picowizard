from ._imports import *

class HelpContentWidget(QWidget):
    """
    Помощь:
    *FAQ
    Ссылки на PicoLAND, гитхаб
    текст с просьбами донатов на игры/на сервера/на чай админу/на чай мне

    Форма сбора предложений/отзывов/пожеланий
    """
    def __init__(self):
        super().__init__()
        text = QLabel('В разработке')
        text.setAlignment(Qt.AlignCenter)
        text.setWordWrap(True)
        vbox = QVBoxLayout()
        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        vbox.addWidget(text)
        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.setLayout(vbox)