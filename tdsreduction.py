#! /usr/bin/python3

from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QLineEdit,
    QStyle,
    QVBoxLayout,
    QFileDialog,
    QPushButton,
    QCheckBox,
    QRadioButton,
    QLabel,
    QGridLayout,
    QHBoxLayout,
)
from PySide6.QtCore import Slot
import sys


class FitsOpenFile(QWidget):

    def __init__(self, parent=None, text=None, tt=None):
        super().__init__(parent)

        self.fits_box = QLineEdit()
        self.fits_box.setToolTip(tt)
        self._open_folder_action = self.fits_box.addAction(
            qApp.style().standardIcon(QStyle.SP_DirOpenIcon),
            QLineEdit.TrailingPosition)
        self._open_folder_action.triggered.connect(self.on_open_folder)
        self.fits_box.setPlaceholderText(text)
        self.files = None

        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.fits_box)

    @Slot()
    def on_open_folder(self):
        files_path = QFileDialog.getOpenFileNames(self, "Fits", "/home/asrolander/",
            "Fits (*.fits *.fts)")[0]
        print(files_path)
        if files_path:
            self.files = files_path.copy()
            self.fits_box.setText(', '.join(files_path))


class ChooseCalibration(QWidget):

    def __init__(self, parent=None, name=None, calibs=[]):
        super().__init__(parent)
        self.name = QLabel(name)

        self.if_perform = QCheckBox('Perform')
        self.if_raw = QRadioButton('Process calibration')
        self.if_processed = QRadioButton('From file')
        self.if_processed.setChecked(True)
        self.raw_input = FitsOpenFile()
        self.raw_output = FitsOpenFile()
        self.processed_input = FitsOpenFile(tt='Processed calibration')
        if calibs:
            self.calibs = SelectPerformedCalibrations(calibs=calibs)

        glayout = QGridLayout(self)
        glayout.addWidget(self.if_raw, 1, 2, 2, 1)
        glayout.addWidget(self.if_processed, 3, 2)
        glayout.addWidget(self.raw_input, 1, 3)
        glayout.addWidget(self.raw_output, 1, 4)
        if calibs:
            glayout.addWidget(self.calibs, 2, 3, 1, 2)
        glayout.addWidget(self.processed_input, 3, 3)
        glayout.addWidget(self.name, 1, 1, 3, 1)
        glayout.addWidget(self.if_perform, 1, 5, 3, 1)
        glayout.setVerticalSpacing(0)
        glayout.setContentsMargins(0, 0, 0, 0)
        glayout.setRowMinimumHeight(1, 0)

        self.if_perform.stateChanged.connect(self.enable_disable)
        self.enable_disable()
        self.setGeometry(0, 0, 10, 20)
        # self.setStyleSheet("border: 1px;")

    @Slot()
    def enable_disable(self):
        enabled = self.if_perform.isChecked()
        self.if_raw.setEnabled(enabled)
        self.if_processed.setEnabled(enabled)
        self.raw_input.setEnabled(enabled)
        self.raw_output.setEnabled(enabled)
        self.processed_input.setEnabled(enabled)


class SelectPerformedCalibrations(QWidget):

    def __init__(self, parent=None, calibs=[]):
        super().__init__(parent)

        calibs_d = {'B': 'bias', 'D': 'dark', 'F': 'flat', 'C': 'cosmics',
                    'X': 'geometry', 'W': 'wavelenghts', 'Y': 'distorsion',
                    'S': 'sky', 'T': 'standart'}
        self.calibs=calibs
        self.checkboxes = {k: QCheckBox(v) for (k, v) in calibs_d.items()}
        for i in self.checkboxes.keys():
            if i not in calibs:
                self.checkboxes[i].setEnabled(False)

        hgrid = QHBoxLayout(self)
        for i in self.checkboxes.values():
            hgrid.addWidget(i)





class MainWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.bias = ChooseCalibration(name='Bias', calibs='')
        self.dark = ChooseCalibration(name='Dark', calibs='B')
        self.flat = ChooseCalibration(name='Flat', calibs='BDX')
        self.corr = ChooseCalibration(name='X-correction', calibs='BDC')
        self.disp = ChooseCalibration(name='Wavelengths', calibs='BDCF')
        self.dist = ChooseCalibration(name='Y-correction', calibs='BDFCW')
        self.calibs = SelectPerformedCalibrations(calibs='BDFCXWYST')

        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.bias)
        vlayout.addWidget(self.dark)
        vlayout.addWidget(self.flat)
        vlayout.addWidget(self.corr)
        vlayout.addWidget(self.disp)
        vlayout.addWidget(self.dist)
        vlayout.addWidget(self.calibs)
        vlayout.setSpacing(0)
        # vlayout.setContentsMargins(0,0,0,0)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())
