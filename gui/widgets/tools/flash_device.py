from .._imports import *

class FlashDeviceDialog(QDialog):
    """
    vbox:
        Label: ваш ro.oem.state : {adb.get_oem_state()}
        Выберите прошивку для скачивания:
        hbox:
            radio: cn, gl
            Список прошивок из firmware для pico4 согласно oem.state и региона, должен обновляться при изменении региона
            кнопка "скачать"
        Файлы скачиваются в папку downloads/firmware/pico4/{oem.state}/{region}/{version}
        Прогрессбар скачивания, кнопка отмены. Во время скачивания переключение региона и выбор прошивки недоступны
        Кнопка "Выбрать свою прошивку" - открывает диалог выбора файла. Если файл выбран, то кнопка "скачать" становится неактивной, кнопка "Выбрать свою прошивку" изменяется на "Сбросить выбор"
        Кнопка "Прошить". При нажатии открывается диалог подтверждения. При подтверждении происходит adb.push(путь к файлу прошивки, /storage/self/primary/dload). adb.push() возвращает subprocess.Popen. На основании процентов выполнения команды обновляется прогрессбар. После успешного выполнения команды открывается всплывающее окно с инструкциями.
        Прогрессбар загрузки файла, кнопка отмены. Во время загрузки все кнопки кроме отмены недоступны.
        Линия разделитель
        label "Псевдо-прошивка"
    """
    def __init__(self, parent=None):
        # super().__init__(parent) # TODO update style.qss
        super().__init__()
        oem_state = adb.get_oem_state()
        if oem_state == '':
            oem_state = False
        else:
            oem_state = True
        self.oem_state = oem_state

        self.create_widgets()
        self.init_layout()
        self.bind_events()

    def create_widgets(self):
        self.radio_cn = QRadioButton('cn')
        self.radio_gl = QRadioButton('gl')

        self.combo_firmwares = QComboBox()

        self.btn_download = QPushButton('Скачать')
        self.btn_flash = QPushButton('Прошить')
        self.btn_select_firmware = QPushButton('Выбрать свою прошивку')
        self.btn_cancel_download = QPushButton('Отмена')
        self.btn_cancel_push = QPushButton('Отмена')

        self.download_progress = QProgressBar()
        self.push_progress = QProgressBar()


    def init_layout(self):
        self.radio_region = QButtonGroup()
        self.radio_region.addButton(self.radio_cn)
        self.radio_region.addButton(self.radio_gl)
        self.radio_region.setExclusive(True)
        self.radio_gl.setChecked(True)
        self.push_progress.setRange(0, 100)
        self.push_progress.setValue(0)
        self.download_progress.setRange(0, 100)
        self.download_progress.setValue(0)

        vbox = QVBoxLayout()
        text = 'Ваш ro.oem.state: ' + str(self.oem_state)
        vbox.addWidget(QLabel(text))
        vbox.addWidget(QLabel('Выберите прошивку для скачивания:'))
        hbox = QHBoxLayout()
        # create a frame to hold the radio buttons
        frame = QFrame()
        frame_hbox = QHBoxLayout()
        # frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        # create a horizontal box layout and add the radio buttons
        frame_hbox.addWidget(self.radio_cn)
        frame_hbox.addWidget(self.radio_gl)
        # make frame fit the radio buttons
        frame_hbox.setContentsMargins(2, 2, 2, 2)
        frame.setLayout(frame_hbox)
        frame.setFixedWidth(80)
        hbox.addWidget(frame)
        hbox.addWidget(self.combo_firmwares)
        hbox.addWidget(self.btn_download)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.download_progress)
        hbox.addWidget(self.btn_cancel_download)
        vbox.addLayout(hbox)
        vbox.addWidget(self.btn_select_firmware)

        vbox.addWidget(self.btn_flash)
        hbox = QHBoxLayout()
        hbox.addWidget(self.push_progress)
        hbox.addWidget(self.btn_cancel_push)
        vbox.addLayout(hbox)
        text = QLabel('Если процент загрузки файла на шлем не меняется, то попробуйте перезагрузить шлем. Кнопка есть в "Инструментах"', wordWrap=True, alignment=Qt.AlignCenter, styleSheet='color: red;') # type: ignore
        vbox.addWidget(text)
        vbox.addWidget(QLabel('_' * 50))

        vbox.addWidget(QLabel('Псевдо-прошивка'))

        self.setLayout(vbox)

    def bind_events(self):
        pass

    def get_oem_state(self):
        pass

    def get_firmwares(self):
        pass

    def download_firmware(self):
        pass