# -*- coding: utf-8 -*-
import os
import sys

from PySide6 import QtGui
################################################################################
## Form generated from reading UI file 'Stats For NerdscJlsCT.ui'
##
## Created by: Qt User Interface Compiler version 6.1.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_Statistics(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(339, 340)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(140, 290, 171, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(50, 10, 121, 16))
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(50, 40, 121, 16))
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(30, 70, 141, 16))
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 190, 161, 16))
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 100, 161, 16))
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_6 = QLabel(Dialog)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 160, 161, 16))
        self.label_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_7 = QLabel(Dialog)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 130, 161, 16))
        self.label_7.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_8 = QLabel(Dialog)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(10, 250, 161, 20))
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_9 = QLabel(Dialog)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(10, 220, 161, 20))
        self.label_9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_10 = QLabel(Dialog)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(180, 10, 51, 16))
        self.label_11 = QLabel(Dialog)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(180, 40, 51, 16))
        self.label_12 = QLabel(Dialog)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(180, 70, 51, 16))
        self.label_13 = QLabel(Dialog)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(180, 100, 51, 16))
        self.label_14 = QLabel(Dialog)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(180, 130, 51, 16))
        self.label_15 = QLabel(Dialog)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(180, 160, 51, 16))
        self.label_16 = QLabel(Dialog)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setGeometry(QRect(180, 190, 51, 16))
        self.label_17 = QLabel(Dialog)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(180, 220, 51, 16))
        self.label_18 = QLabel(Dialog)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(180, 250, 51, 16))

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowIcon(QtGui.QIcon(resource_path("joystick_icon.png")))
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Stats For Nerds", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Left Eyebrow Score:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Right Eyebrow Score:", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Up/Down Eyebrow Score:", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Furrowed Eyebrow Threshold:", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"Left Eyebrow Threshold:", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"Raised Eyebrow Threshold:", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"Right Eyebrow Threshold:", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"Fingers Raised on Right Hand:", None))
        self.label_9.setText(QCoreApplication.translate("Dialog", u"Fingers Raised on Left Hand:", None))
        self.label_10.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.label_11.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.label_12.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.label_13.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.label_14.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.label_15.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.label_16.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.label_17.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.label_18.setText(QCoreApplication.translate("Dialog", u"0", None))
    # retranslateUi


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
