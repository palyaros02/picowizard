from ._imports import *

class GamesContentWidget(QWidget):
    """
    Программы/Игры:
    Поиск по названию/тегам/для какой прошивки/PCVR
    Список программ/игр:
        Картинка (меняются по таймеру при наведении)
        Название
        Вес
        Оценка
        Теги
        Для какой прошивки
        Версия игры
        Кнопка "установить"/"обновить"/"удалить"/ссылка для PCVR

    По нажатию на элемент списка открывается окно с подробной информацией:
        название
        Крупная картинка/видео
        карусель с картинками
        Описание
        Теги
        Вес
        Оценка
        Оценить
        Теги
        Для какой прошивки
        Версия игры
        Кнопка "установить"/"обновить"/"удалить"/ссылка для PCVR
        Отзывы
        Кол-во скачиваний и установок
        Оставить отзыв
        когда загружено/обновлено
        Кнопка "Поиск команды"
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