import time

from PySide6 import QtWidgets, QtCore

from KeyBindingsUI import Ui_Key_Bindings
from StatisticsUI import Ui_Statistics
from MainWindow import *
from ThresholdsUI import Ui_Thresholds
import KeyBindingListener


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Thread in charge of updating the image
        self.th = CameraThread(self)
        self.th.finished.connect(self.close)
        self.th.updateFrame.connect(self.set_image)

        self.main_window = Ui_MainWindow()

        self.main_window.setupUi(self)
        self.main_window.Recalibrate.clicked.connect(self.start_calibration)
        self.main_window.pushButton.clicked.connect(self.disable_inputs)
        self.main_window.actionChange_Key_Bindings.triggered.connect(self.open_key_binding)
        self.main_window.actionToggle_Wireframes.triggered.connect(self.toggle_wireframes)
        self.main_window.actionRecalibrate.triggered.connect(self.start_calibration)
        self.main_window.actionChange_Thresholds.triggered.connect(self.open_thresholds)
        self.main_window.actionStats_For_Nerds.triggered.connect(self.open_statistics)
        # Thread in charge of updating the image
        self.label = QLabel(self)
        self.label.setGeometry(QRect(10, 32, 640, 480))
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.th.start()

        app.focusChanged.connect(self.on_focus_change)

    def closeEvent(self, event):
        self.kill_thread()
        event.accept()

    @Slot()
    def kill_thread(self):
        print("Finishing...")
        self.th.cap.release()
        cv2.destroyAllWindows()
        self.status = False
        self.th.terminate()
        # Give time for the thread to finish
        time.sleep(1)

    @Slot(QImage)
    def set_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    @Slot()
    def start_calibration(self):
        self.th.cal.turn_on()

    @Slot()
    def disable_inputs(self):
        if self.main_window.pushButton.isChecked():
            self.th.inputs_are_disabled = True
        else:
            self.th.inputs_are_disabled = False

    def open_key_binding(self):
        # Key Bindings UI
        self.ui_window = QtWidgets.QDialog()
        self.key_bindings_window = Ui_Key_Bindings()
        self.key_bindings_window.setupUi(self.ui_window)
        self.get_key_bindings()
        self.key_bindings_window.buttonBox.accepted.connect(self.set_key_bindings)
        self.key_bindings_window.pushButton_15.clicked.connect(self.set_default_key_bindings)
        self.ui_window.show()

    def on_focus_change(self, widgetOld, widget):
        if widget is not None and widget.objectName().startswith("ui_lineEdit"):
            self.ui_window.setDisabled(True)
            keyBinder = KeyBindingListener.KeyboardListener()
            keyBinder.activate_listener()
            self.ui_window.setEnabled(True)
            lineEditFocused = widget
            lineEditFocused.setText(keyBinder.keys)

    def set_key_bindings(self):
        self.th.one_left_key = to_int(self.key_bindings_window.ui_lineEdit_11.text().strip('}{').split(', ')[0])
        self.th.two_left_key = to_int(self.key_bindings_window.ui_lineEdit_14.text().strip('}{').split(', ')[0])
        self.th.three_left_key = to_int(self.key_bindings_window.ui_lineEdit_10.text().strip('}{').split(', ')[0])
        self.th.one_right_key = to_int(self.key_bindings_window.ui_lineEdit_5.text().strip('}{').split(', ')[0])
        self.th.two_right_key = to_int(self.key_bindings_window.ui_lineEdit_7.text().strip('}{').split(', ')[0])
        self.th.three_right_key = to_int(self.key_bindings_window.ui_lineEdit_6.text().strip('}{').split(', ')[0])
        self.th.up_key = to_int(self.key_bindings_window.ui_lineEdit_3.text().strip('}{').split(', ')[0])
        self.th.down_key = to_int(self.key_bindings_window.ui_lineEdit_4.text().strip('}{').split(', ')[0])
        self.th.left_key = to_int(self.key_bindings_window.ui_lineEdit.text().strip('}{').split(', ')[0])
        self.th.right_key = to_int(self.key_bindings_window.ui_lineEdit_2.text().strip('}{').split(', ')[0])

    def get_key_bindings(self):
        self.key_bindings_window.ui_lineEdit_11.setText("{" + str(self.th.one_left_key) + "}")
        self.key_bindings_window.ui_lineEdit_14.setText("{" + str(self.th.two_left_key) + "}")
        self.key_bindings_window.ui_lineEdit_10.setText("{" + str(self.th.three_left_key) + "}")
        self.key_bindings_window.ui_lineEdit_5.setText("{" + str(self.th.one_right_key) + "}")
        self.key_bindings_window.ui_lineEdit_7.setText("{" + str(self.th.two_right_key) + "}")
        self.key_bindings_window.ui_lineEdit_6.setText("{" + str(self.th.three_right_key) + "}")
        self.key_bindings_window.ui_lineEdit_3.setText("{" + str(self.th.up_key) + "}")
        self.key_bindings_window.ui_lineEdit_4.setText("{" + str(self.th.down_key) + "}")
        self.key_bindings_window.ui_lineEdit.setText("{" + str(self.th.left_key) + "}")
        self.key_bindings_window.ui_lineEdit_2.setText("{" + str(self.th.right_key) + "}")

    def set_default_key_bindings(self):
        self.key_bindings_window.ui_lineEdit_11.setText("{76}")
        self.key_bindings_window.ui_lineEdit_14.setText("{8}")
        self.key_bindings_window.ui_lineEdit_10.setText("{79}")
        self.key_bindings_window.ui_lineEdit_5.setText("{75}")
        self.key_bindings_window.ui_lineEdit_7.setText("{13}")
        self.key_bindings_window.ui_lineEdit_6.setText("{73}")
        self.key_bindings_window.ui_lineEdit_3.setText("{87}")
        self.key_bindings_window.ui_lineEdit_4.setText("{83}")
        self.key_bindings_window.ui_lineEdit.setText("{65}")
        self.key_bindings_window.ui_lineEdit_2.setText("{68}")

    def open_statistics(self):
        # Statistics UI
        self.window = QtWidgets.QDialog()
        self.statistics_window = Ui_Statistics()
        self.statistics_window.setupUi(self.window)
        self.window.show()

    def open_thresholds(self):
        # Thresholds UI
        self.window = QtWidgets.QDialog()
        self.thresholds_window = Ui_Thresholds()
        self.thresholds_window.setupUi(self.window)
        self.get_thresholds()
        self.thresholds_window.buttonBox.accepted.connect(self.set_thresholds)
        self.window.show()

    def set_thresholds(self):
        up = float(self.thresholds_window.lineEdit_3.text())
        down = float(self.thresholds_window.lineEdit_4.text())
        left = float(self.thresholds_window.lineEdit.text())
        right = float(self.thresholds_window.lineEdit_2.text())
        self.th.thresholds = [up, down, left, right]  # up, down, left, right

    def get_thresholds(self):
        self.thresholds_window.lineEdit.setText(str(self.th.thresholds[2]))
        self.thresholds_window.lineEdit_2.setText(str(self.th.thresholds[3]))
        self.thresholds_window.lineEdit_3.setText(str(self.th.thresholds[0]))
        self.thresholds_window.lineEdit_4.setText(str(self.th.thresholds[1]))

    def toggle_wireframes(self):
        self.th.show_wireframes = not self.th.show_wireframes

def to_int(string):
    if string == '':
        return 0
    else:
        return int(string)

if __name__ == "__main__":
    app = QApplication()
    w = Window()
    w.show()
    sys.exit(app.exec())
