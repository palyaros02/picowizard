from .widgets import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.setup_ui()
        self.init_ui()
        self.retranslate_ui()
        self.bind_events()
        # self.restart_adb()
        self.start_polling()

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
        self.btn_tools = QPushButton('Инструменты')
        self.device_status = QLabel()
        self.device_usb_status_picture = QLabel()
        self.device_wifi_status_picture = QLabel()
        # self.device_tags = QTableWidget()
        self.btn_update_app = QPushButton('Обновления')
        self.version = QLabel('v' + config.get('DO_NOT_MODIFY', 'version'))

        # timer
        self.timer = QTimer()

    def setup_ui(self):
        self.setWindowTitle("PicoF*cker")
        self.setMinimumSize(800, 600)
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr = self.frameGeometry()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        with open("./gui/style.qss", "r") as f:
            self.setStyleSheet(f.read())

        # # disable buttons
        # self.btn_games.setEnabled(False)
        # self.btn_movies.setEnabled(False)
        # self.btn_community.setEnabled(False)
        # self.btn_help.setEnabled(False)
        # self.btn_settings.setEnabled(False)


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

        # # right_panel
        right_panel = QVBoxLayout()

        hbox = QHBoxLayout()
        text = QLabel('Название:')
        text.setStyleSheet('font-weight: bold;')
        text.setAlignment(Qt.AlignRight)
        hbox.addWidget(text)
        hbox.addWidget(self.device_name)
        right_panel.addLayout(hbox)

        self.set_device_picture('./gui/img/not_connected.png')
        self.device_picture.setAlignment(Qt.AlignCenter)
        self.device_picture.setFixedSize(250, 150)
        self.device_picture.setScaledContents(True)
        self.device_picture.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        right_panel.addWidget(self.device_picture)

        right_panel.addWidget(self.btn_tools)

        hbox = QHBoxLayout()
        text = QLabel('Статус:')
        text.setStyleSheet('font-weight: bold;')
        text.setAlignment(Qt.AlignRight)
        hbox.addWidget(text)
        self.update_device_status_picture()
        self.device_usb_status_picture.setFixedSize(20, 20)
        self.device_usb_status_picture.setScaledContents(True)
        self.device_usb_status_picture.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.device_usb_status_picture.setAlignment(Qt.AlignCenter)
        hbox.addWidget(self.device_usb_status_picture)
        self.device_wifi_status_picture.setFixedSize(20, 20)
        self.device_wifi_status_picture.setScaledContents(True)
        self.device_wifi_status_picture.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.device_wifi_status_picture.setAlignment(Qt.AlignCenter)
        hbox.addWidget(self.device_wifi_status_picture)
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
        self.version.setAlignment(Qt.AlignRight|Qt.AlignBottom) # type: ignore
        hbox.addWidget(self.version)
        right_panel.addLayout(hbox)

        self.main_layout.addLayout(right_panel)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def set_content_widget(self, widget):
        self.main_layout.removeWidget(self.content_widget)
        self.content_widget.deleteLater()
        self.content_widget = widget
        self.content_widget.setMinimumSize(300, self.minimumHeight())
        self.main_layout.insertWidget(1, widget)

    def update_device_status_picture(self):
        try:
            status = adb.get_connection_status()
        except:
            self.device_usb_status_picture.setPixmap(QPixmap('./gui/img/disconnected.png'))
            self.device_wifi_status_picture.hide()
            self.device_usb_status_picture.show()
            self.device_name.setText('Не подключено')
            self.device_status.setText('Отключено')
            self.set_device_picture('./gui/img/not_connected.png')
        else:
            match status:
                case 'NO_DEVICES':
                    self.device_usb_status_picture.setPixmap(QPixmap('./gui/img/disconnected.png'))
                    self.device_wifi_status_picture.hide()
                case 'DISCONNECTED':
                    self.device_usb_status_picture.setPixmap(QPixmap('./gui/img/usb_ready.png'))
                    self.device_wifi_status_picture.hide()
                case 'USB':
                    self.device_usb_status_picture.setPixmap(QPixmap('./gui/img/usb.png'))
                    self.device_wifi_status_picture.hide()
                case 'WIFI_READY':
                    self.device_usb_status_picture.setPixmap(QPixmap('./gui/img/usb.png'))
                    self.device_wifi_status_picture.setPixmap(QPixmap('./gui/img/wifi_ready.png'))
                    self.device_wifi_status_picture.show()
                    self.device_usb_status_picture.show()
                case 'WIFI':
                    self.device_usb_status_picture.hide()
                    self.device_wifi_status_picture.setPixmap(QPixmap('./gui/img/wifi.png'))
                    self.device_wifi_status_picture.show()

    def set_device_picture(self, path):
        self.device_picture.setPixmap(QPixmap(path))

    def retranslate_ui(self):
        # перевод интерфейса
        pass

    def bind_events(self):
        self.btn_tools.clicked.connect(lambda: self.set_content_widget(ToolsContentWidget()))
        self.btn_games.clicked.connect(lambda: self.set_content_widget(GamesContentWidget()))
        self.btn_movies.clicked.connect(lambda: self.set_content_widget(MoviesContentWidget()))
        self.btn_help.clicked.connect(lambda: self.set_content_widget(HelpContentWidget()))
        self.btn_community.clicked.connect(lambda: self.set_content_widget(CommunityContentWidget()))
        # self.btn_settings.clicked.connect(lambda: self.set_content_widget(SettingsContentWidget()))
        self.btn_settings.clicked.connect(self.__TODO_open_settings) # TODO: make normal settings widget

    def __TODO_open_settings(self):
        res = os.system('notepad config.cfg')
        if res == 0:
            config.read('config.cfg')

    def start_polling(self, interval=config.getint('DO_NOT_MODIFY', 'polling_interval')):
        self.timer.timeout.connect(self.update_device)
        self.timer.start(interval)

    def pause_polling(self):
        self.timer.stop()

    def resume_polling(self):
        self.timer.start()

    def update_device(self):
        try:
            adb.connect()
            device = adb.get_device()
            status = adb.get_connection_status()
        except:
            pass
        else:
            self.device_name.setText(device.name)
            self.device_status.setText(status)
            if device.tags['type'] == 'PICO4':
                self.set_device_picture('./gui/img/pico4.png')
            else:
                self.set_device_picture('./gui/img/pico3.png')
        finally:
            self.update_device_status_picture()


    def restart_adb(self):
        adb.restart_server()