from ._imports import *

class CommunityContentWidget(QWidget):
    """
        Сообщество:
            (время последнего входа, статус (онлайн, оффлайн, играет в ...), если не входил неделю, то помечаем неактивным)
            Контакты для связи (телеграм, дискорд, свои контакты)
            предпочитаемый язык
            Время доступности для игр, часовой пояс
            Желаемые игры
            Текущие игры
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