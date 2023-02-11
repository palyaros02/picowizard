from ._imports import *

class SettingsContentWidget(QWidget):
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

        res = os.system('notepad config.cfg')
        if res == 0:
            config.read('config.cfg')