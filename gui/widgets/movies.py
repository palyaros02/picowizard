from ._imports import *

class MoviesContentWidget(QWidget):
    """
    Фильмы/Видео:
    Поиск по названию/тегам
    *ссылка на FAQ как смотреть
    Список фильмов/видео:
        Картинка (меняются по таймеру при наведении)
        Название
        Вес
        Оценка
        Теги
        Кнопка "скачать на шлем"/"скачать на комп"/ссылка на скачивание

        окошко аналогично программам/играм
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