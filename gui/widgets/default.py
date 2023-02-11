from ._imports import *

class DefaultContentWidget(QWidget):
    def __init__(self):
        super().__init__()
        text = QLabel('Нажмите на кнопку "Инструменты" справа')
        text.setAlignment(Qt.AlignCenter)
        text.setWordWrap(True)
        vbox = QVBoxLayout()
        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        vbox.addWidget(text)
        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.setLayout(vbox)