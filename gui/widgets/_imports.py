# i know this is a bad way to do this, but it works for now, and i'm too lazy to figure out how python's import system works

from PySide6.QtCore import (
    Qt, QTimer, QTranslator, QThread, QObject, Signal, Slot
    )

from PySide6.QtGui import (
    QPixmap, QGuiApplication,
    )

from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QLayout,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget, QComboBox, QDialog, QTableWidget, QLineEdit, QDialogButtonBox,
    QMessageBox, QButtonGroup, QRadioButton, QProgressBar, QFileDialog, QCheckBox, QFrame,
    QScrollArea,
    )

from adb import adb
import sys, os, time, requests
from config_parser import config, firmware