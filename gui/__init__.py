from PySide6.QtCore import (
    Qt,
    )
from PySide6.QtGui import (
    QPixmap, QGuiApplication
    )
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QLayout,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget,
    )

import sys, os

"""
звездочкой помечены кнопки, по нажатию на которые открывается новое окно
Главный экран:
    Справа статус бар, отображающий шлем и статус подключения

    Кнопки:
        Инструменты
        Программы/Игры
        Фильмы/видео
        Поиск команды
        Помощь

    Область переключений в зависимости от выбранной кнопки:

        Инструменты:
            Установить драйвер
            Вкл adb по wifi
            * Установка программ
            * Управление приложениями
            * Выполнить команду
            Перезагрузить шлем

            * Переключить регион
            * Прошить шлем
            * Псевдо-прошивка

            Установка программ:
                Выбор файла apk
                Выбор файла obb
                Кнопка установить
                Прогресс бар

            Управление приложениями:
                Список установленных приложений
                Бэкап приложений
                Включение/выключение приложений
                Удаление приложений
                Управление правами

            Выполнить команду:
                Ввод команды
                Кнопка выполнить
                Вывод команды

            Переключить регион:
                Выбор региона
                Кнопка переключить

            Прошить шлем:
                Выбор файла прошивки
                Кнопка "скачать прошивку"
                Кнопка прошить
                ПРЕДЕПРЕЖДЕНИЕ

            Псевдо-прошивка:
                Настройки
                Кнопка "прошить"

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

        Поиск команды:
            (время последнего входа, статус (онлайн, оффлайн, играет в ...), если не входил неделю, то помечаем неактивным)
            Контакты для связи (телеграм, дискорд, свои контакты)
            предпочитаемый язык
            Время доступности для игр, часовой пояс
            Желаемые игры
            Текущие игры

        Помощь:
            *FAQ
            Ссылки на PicoLAND, гитхаб
            текст с просьбами донатов на игры/на сервера/на чай админу/на чай мне

            Форма сбора предложений/отзывов/пожеланий


Стили из файла style.qss
"""
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.setup_ui()
        self.init_ui()
        self.retranslate_ui()
        self.bind_events()

    def create_widgets(self):
        # left_panel
        self.btn_games = QPushButton('Игры')
        self.btn_movies = QPushButton('Фильмы')
        self.btn_community = QPushButton('Сообщество')
        self.btn_help = QPushButton('Помощь')
        self.btn_settings = QPushButton('Настройки')

        # content_widget
        self.content_widget = QWidget()

        # right_panel
        self.device_name = QLabel()
        self.device_picture = QLabel()
        self.btn_connect = QPushButton('Подключиться')
        self.btn_tools = QPushButton('Инструменты')
        self.device_status = QLabel()
        self.device_status_picture = QLabel()
        # self.device_tags = QTableWidget()
        self.btn_update_app = QPushButton('Обновления')
        self.version = QLabel('v0.0.1')

    def setup_ui(self):
        self.setWindowTitle("PicoF*cker")
        self.setMinimumSize(800, 600)
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr = self.frameGeometry()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        with open("./gui/style.qss", "r") as f:
            self.setStyleSheet(f.read())

        # disable buttons
        self.btn_games.setEnabled(False)
        self.btn_movies.setEnabled(False)
        self.btn_community.setEnabled(False)
        self.btn_help.setEnabled(False)
        self.btn_settings.setEnabled(False)


    def init_ui(self):
        self.main_layout = QHBoxLayout()

        # left_panel
        left_panel = QVBoxLayout()
        left_panel.addWidget(self.btn_games)
        left_panel.addWidget(self.btn_movies)
        left_panel.addWidget(self.btn_community)
        left_panel.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        left_panel.addWidget(self.btn_help)
        left_panel.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        left_panel.addWidget(self.btn_settings)
        self.main_layout.addLayout(left_panel)

        # content_widget
        self.main_layout.addWidget(self.content_widget)
        self.set_content_widget(DefaultContentWidget())

        # right_panel
        class BoldLabel(QLabel):
            def __init__(self, text):
                super().__init__(text)
                self.setStyleSheet('font-weight: bold;')
                self.setAlignment(Qt.AlignRight)

        right_panel = QVBoxLayout()

        hbox = QHBoxLayout()
        text = BoldLabel('Название:')
        hbox.addWidget(text)
        hbox.addWidget(self.device_name)
        right_panel.addLayout(hbox)

        self.set_device_picture('./gui/img/not_connected.png')
        self.device_picture.setAlignment(Qt.AlignCenter)
        self.device_picture.setFixedSize(250, 150)
        self.device_picture.setScaledContents(True)
        self.device_picture.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        right_panel.addWidget(self.device_picture)

        right_panel.addWidget(self.btn_connect)
        right_panel.addWidget(self.btn_tools)

        hbox = QHBoxLayout()
        text = BoldLabel('Статус:')
        hbox.addWidget(text)
        self.set_device_status_picture('./gui/img/usb.png')
        self.device_status_picture.setFixedSize(20, 20)
        self.device_status_picture.setScaledContents(True)
        self.device_status_picture.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.device_status_picture.setAlignment(Qt.AlignCenter)
        hbox.addWidget(self.device_status_picture)
        hbox.addWidget(self.device_status)
        right_panel.addLayout(hbox)

        # text = BoldLabel('Теги:')
        # text.setAlignment(Qt.AlignCenter)
        # right_panel.addWidget(text)
        # self.device_tags.setColumnCount(2)
        # self.device_tags.setRowCount(4)
        # self.device_tags.verticalHeader().setVisible(False)
        # self.device_tags.horizontalHeader().setVisible(False)
        # right_panel.addWidget(self.device_tags)


        right_panel.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_update_app)
        self.version.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        hbox.addWidget(self.version)
        right_panel.addLayout(hbox)

        self.main_layout.addLayout(right_panel)

        self.setLayout(self.main_layout)

    def set_content_widget(self, widget):
        self.main_layout.removeWidget(self.content_widget)
        self.content_widget.deleteLater()
        self.content_widget = widget
        self.main_layout.insertWidget(1, widget)

    def set_device_status_picture(self, path):
        self.device_status_picture.setPixmap(QPixmap(path))

    def set_device_picture(self, path):
        self.device_picture.setPixmap(QPixmap(path))

    def retranslate_ui(self):
        # перевод интерфейса
        pass

    def bind_events(self):
        # привязка событий к элементам интерфейса
        pass


class DefaultContentWidget(QWidget):
    def __init__(self):
        super().__init__()
        text = QLabel('Нажмите на кнопку "Инструменты" справа')
        text.setAlignment(Qt.AlignCenter)
        text.setWordWrap(True)
        hbox = QHBoxLayout()
        hbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        hbox.addWidget(text)
        hbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.setLayout(hbox)