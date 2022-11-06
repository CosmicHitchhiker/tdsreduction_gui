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
    QFrame,
    QFormLayout,
    QDialog,
    QBoxLayout,
)
from PySide6.QtCore import Slot, QMargins
import sys
import yaml


def createHorizontalSeparator() -> QFrame:
    result = QFrame()
    result.setFrameStyle(QFrame.HLine | QFrame.Sunken)
    return result


def createVerticalSeparator() -> QFrame:
    result = QFrame()
    result.setFrameStyle(QFrame.VLine | QFrame.Sunken)
    return result


def htmlHeader(text, size=5):
    res = "<h{0}>{1}</h{0}>".format(size, text)
    return res


class YamlOpenFile(QWidget):

    def __init__(self, parent=None, text=None, tt=None):
        super().__init__(parent)

        self.yaml_box = QLineEdit()
        self.yaml_box.setToolTip(tt)
        self._open_folder_action = self.yaml_box.addAction(
            qApp.style().standardIcon(QStyle.SP_DirOpenIcon),
            QLineEdit.TrailingPosition)
        self.yaml_box.setPlaceholderText(text)
        self.files = None

        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.yaml_box)
        vlayout.setContentsMargins(0,0,0,0)
        vlayout.setSpacing(0)

        self._open_folder_action.triggered.connect(self.on_open_folder)
        self.yaml_box.editingFinished.connect(self.check_line)

    @Slot()
    def check_line(self):
        self.files = self.yaml_box.text()


    @Slot()
    def on_open_folder(self):
        files_path = QFileDialog.getSaveFileName(self, "Yaml", "/home",
            "yaml (*.yaml *.yml);;All (*)")[0]
        ext = files_path.split('.')
        if len(ext) < 2:
            files_path = files_path + '.yml'
        print(files_path)

        if files_path:
            self.files = files_path
            self.yaml_box.setText(files_path)


class FitsOpenFile(QWidget):

    def __init__(self, parent=None, text=None, tt=None, mode='n'):
        super().__init__(parent)

        self.fits_box = QLineEdit()
        self.fits_box.setToolTip(tt)
        self._open_folder_action = self.fits_box.addAction(
            qApp.style().standardIcon(QStyle.SP_DirOpenIcon),
            QLineEdit.TrailingPosition)
        self.fits_box.setPlaceholderText(text)
        self.files = None
        self.mode = mode

        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.fits_box)
        vlayout.setContentsMargins(0,0,0,0)
        vlayout.setSpacing(0)

        self._open_folder_action.triggered.connect(self.on_open_folder)
        self.fits_box.editingFinished.connect(self.check_line)

    @Slot()
    def check_line(self):
        self.files = self.fits_box.text().split(',')
        if self.mode != 'n':
            self.files = self.files[0]
        else:
            self.files = [x.strip() for x in self.files]


    @Slot()
    def on_open_folder(self):
        if self.mode == 'n':
            files_path = QFileDialog.getOpenFileNames(self, "Fits", "/home",
                "Fits (*.fits *.fts);;All (*)")[0]
        elif self.mode == 'o':
            files_path = QFileDialog.getOpenFileName(self, "Fits", "/home",
                "Fits (*.fits *.fts);;All (*)")[0]
        elif self.mode == 'w':
            files_path = QFileDialog.getSaveFileName(self, "Fits", "/home",
                "Fits (*.fits *.fts);;All (*)")[0]
            ext = files_path.split('.')
            if len(ext) < 2:
                files_path = files_path + '.fits'
            print(files_path)

        if files_path:
            if self.mode == 'n':
                self.files = files_path.copy()
                self.fits_box.setText(', '.join(files_path))
            else:
                self.files = files_path
                self.fits_box.setText(files_path)


class ChooseCalibration(QWidget):

    def __init__(self, parent=None, name=None, calibs=[]):
        super().__init__(parent)
        self.name = QLabel(htmlHeader(name))

        self.if_raw = QRadioButton('Process calibration')
        self.if_processed = QRadioButton('From file')
        self.if_processed.setChecked(True)
        self.raw_input = FitsOpenFile()
        self.raw_output = FitsOpenFile(mode='w')
        self.processed_input = FitsOpenFile(tt='Processed calibration', mode='o')
        self.calibs = SelectPerformedCalibrations(calibs=calibs)

        rawgrid = QGridLayout()
        rawgrid.addWidget(self.raw_input, 1, 1)
        rawgrid.addWidget(self.raw_output, 1, 2)
        if calibs:
            rawgrid.addWidget(self.calibs, 2, 1, 1, 2)
        rawgrid.setVerticalSpacing(0)
        rawgrid.setContentsMargins(1,1,1,1)

        self.flayout = QFormLayout(self)
        self.flayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.flayout.setContentsMargins(QMargins())
        self.flayout.addRow(self.name)
        self.flayout.addRow(self.if_raw, rawgrid)
        self.flayout.addRow(self.if_processed, self.processed_input)
        self.flayout.addRow(createHorizontalSeparator())
        self.flayout.setSpacing(1)
        self.flayout.setContentsMargins(1,1,1,1)

        self.if_raw.toggled.connect(self.enable_disable)
        self.enable_disable()

    @Slot()
    def enable_disable(self):
        set_raw = self.if_raw.isChecked()
        set_processed = self.if_processed.isChecked()
        self.raw_input.setEnabled(set_raw)
        self.raw_output.setEnabled(set_raw)
        self.calibs.setEnabled(set_raw)
        self.processed_input.setEnabled(set_processed)

    def return_dict(self):
        set_raw = self.if_raw.isChecked()
        set_processed = self.if_processed.isChecked()
        res = dict()
        if set_processed:
            res['calibration'] = self.processed_input.files
        if set_raw:
            res['calibration'] = self.raw_output.files
            res['rawfiles'] = self.raw_input.files

            add_calib = [x for x in self.calibs.checkboxes.keys() if
                         self.calibs.checkboxes[x].isChecked()]
            res['additional'] = add_calib
        return res

    def return_calib(self):
        set_raw = self.if_raw.isChecked()
        set_processed = self.if_processed.isChecked()
        if set_processed:
            return self.processed_input.files
        if set_raw:
            return self.raw_output.files




class SelectPerformedCalibrations(QWidget):

    def __init__(self, parent=None, calibs=[]):
        super().__init__(parent)

        calibs_d = {'B': 'bias', 'D': 'dark', 'F': 'flat', 'C': 'cosmics',
                    'X': 'geometry', 'W': 'wavelenghts', 'Y': 'distorsion',
                    'S': 'sky', 'T': 'standart'}
        self.calibs = calibs
        self.checkboxes = {k: QCheckBox(calibs_d[k]) for k in calibs}
        # for i in self.checkboxes.keys():
        #     if i not in calibs:
        #         self.checkboxes[i].setEnabled(False)

        hgrid = QHBoxLayout(self)
        for i in self.checkboxes.values():
            hgrid.addWidget(i)
        hgrid.setContentsMargins(0,0,0,0)
        hgrid.setSpacing(0)





class MainWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.bias = ChooseCalibration(name='Bias', calibs='')
        self.dark = ChooseCalibration(name='Dark', calibs='B')
        self.corr = ChooseCalibration(name='X-correction', calibs='BDC')
        self.flat = ChooseCalibration(name='Flat', calibs='BX')
        self.disp = ChooseCalibration(name='Wavelengths', calibs='BDCF')
        self.dist = ChooseCalibration(name='Y-correction', calibs='BDFCW')
        self.calibs = SelectPerformedCalibrations(calibs='BDFCXWYST')
        self.frames = FitsOpenFile(text='Object frames')
        self.yaml_save = YamlOpenFile(text='Yaml file to save config')
        self.start_button = QPushButton('GO!!!')
        self.result_path = FitsOpenFile(text='Result path', mode='w')
        self.load_button = QPushButton('Load config')

        vlayout = QGridLayout(self)
        vlayout.addWidget(self.bias, 1, 1)
        vlayout.addWidget(createVerticalSeparator(), 1, 2)
        vlayout.addWidget(self.dark, 1, 3)
        vlayout.addWidget(self.corr, 2, 1)
        vlayout.addWidget(createVerticalSeparator(), 2, 2)
        vlayout.addWidget(self.flat, 2, 3)
        vlayout.addWidget(self.disp, 3, 1)
        vlayout.addWidget(createVerticalSeparator(), 3, 2)
        vlayout.addWidget(self.dist, 3, 3)

        glayout = QGridLayout()
        glayout.addWidget(self.frames, 1, 1, 1, 2)
        glayout.addWidget(self.result_path, 1, 3)
        glayout.addWidget(self.yaml_save, 1, 4)
        glayout.addWidget(self.load_button, 2, 1)
        glayout.addWidget(self.calibs, 2, 2, 1, 2)
        glayout.addWidget(self.start_button, 2, 4)

        vlayout.addLayout(glayout, 4, 1, 1, 3)
        self.start_button.clicked.connect(self.generate_yaml_config)

    @Slot()
    def generate_yaml_config(self):
        res = dict()
        calibs_d = {'B': 'bias', 'D': 'dark', 'F': 'flat', 'C': 'cosmics',
                    'X': 'corr', 'W': 'disp', 'Y': 'dist',
                    'S': 'sky', 'T': 'standart'}
        res['bias'] = self.bias.return_dict()
        res['dark'] = self.dark.return_dict()
        res['corr'] = self.corr.return_dict()
        res['flat'] = self.flat.return_dict()
        res['disp'] = self.disp.return_dict()
        res['dist'] = self.dist.return_dict()
        res['cosmics'] ={'calibration': True}

        for c in res.keys():
            if 'additional' in res[c]:
                res[c]['additional'] = {k: res[calibs_d[k]]['calibration']
                                        for k in res[c]['additional']}



        yaml_name = self.yaml_save.files
        if not yaml_name:
            yaml_name = 'last_config.yaml'

        stream = open(yaml_name, 'w')
        yaml.dump(res, stream)
        stream.close()
        print(yaml.dump(res))
        # print(res)





if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())
