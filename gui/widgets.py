from PySide6.QtCore import (
    Qt, QTimer
    )

from PySide6.QtGui import (
    QPixmap, QGuiApplication
    )

from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QLayout,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget, QComboBox, QDialog, QTableWidget, QLineEdit, QDialogButtonBox, QMessageBox
    )

from adb import adb
import sys, os, time
from config_parser import config

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

class SettingsContentWidget(QWidget):
    def __init__(self):
        super().__init__()

class ChangeRegionDialog(QDialog):
    def __init__(self):
        super().__init__()
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



class ToolsContentWidget(QWidget):
    """
    Инструменты:

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

        Прошить шлем:
            Выбор файла прошивки
            Кнопка "скачать прошивку"
            Кнопка прошить
            ПРЕДЕПРЕЖДЕНИЕ

        Псевдо-прошивка:
            Настройки
            Кнопка "прошить"
        """
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.init_layout()
        self.bind_events()

    def create_widgets(self):
        self.btn_install_driver = QPushButton('Установить драйвер ADB')
        self.btn_restart_server = QPushButton('Перезапустить сервер ADB (ждать)')
        self.btn_reboot_device = QPushButton('Перезагрузить шлем')
        self.btn_enable_wifi = QPushButton('USB -> WiFi (ждать)')
        self.btn_disable_wifi = QPushButton('WiFi -> USB')
        self.btn_install_app = QPushButton('Установить приложение')
        self.btn_manage_apps = QPushButton('Управление приложениями')
        self.btn_run_adb_command = QPushButton('Выполнить команду')
        self.btn_switch_region = QPushButton('Переключить регион')
        self.btn_flash_device = QPushButton('Прошить шлем')
        self.btn_usb_tethering = QPushButton('Вкл/выкл режим модема')


    def init_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn_install_driver)
        self.btn_install_driver.setToolTip('Установить драйвер ADB для подключения к шлему по USB')
        vbox.addWidget(self.btn_restart_server)
        vbox.addWidget(self.btn_reboot_device)

        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_enable_wifi)
        hbox.addWidget(self.btn_disable_wifi)
        vbox.addLayout(hbox)

        vbox.addWidget(self.btn_install_app)
        vbox.addWidget(self.btn_manage_apps)
        vbox.addWidget(self.btn_run_adb_command)
        vbox.addWidget(self.btn_switch_region)
        vbox.addWidget(self.btn_flash_device)
        vbox.addWidget(self.btn_usb_tethering)

        #disable buttons
        self.btn_install_app.setEnabled(False)
        self.btn_manage_apps.setEnabled(False)
        self.btn_run_adb_command.setEnabled(False)
        # self.btn_switch_region.setEnabled(False)
        self.btn_flash_device.setEnabled(False)
        self.btn_usb_tethering.setEnabled(False)

        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setLayout(vbox)

    def bind_events(self):
        self.btn_install_driver.clicked.connect(adb.install_driver)
        self.btn_restart_server.clicked.connect(adb.restart_server)
        self.btn_reboot_device.clicked.connect(adb.reboot_device)
        self.btn_enable_wifi.clicked.connect(self.connect_wifi)
        self.btn_disable_wifi.clicked.connect(self.disconnect_wifi)
        self.btn_switch_region.clicked.connect(self.switch_region)

    def connect_wifi(self):
        adb.connect_wifi()

    def disconnect_wifi(self):
        adb.disconnect_wifi()
        adb.connect_usb()

    def switch_region(self):
        change_region_dialog = ChangeRegionDialog()
        change_region_dialog.exec()


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