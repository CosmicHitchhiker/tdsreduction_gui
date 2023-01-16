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
)
from PySide6.QtCore import Slot, QMargins, Signal
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


def getCalibDict(short=False):
    if short:
        res = {'B': 'bias', 'D': 'dark', 'F': 'flat', 'C': 'cosmics',
               'X': 'corr', 'W': 'disp', 'Y': 'dist',
               'S': 'sky', 'T': 'standart', 'U': 'summ'}

    else:
        res = {'B': 'bias', 'D': 'dark', 'F': 'flat', 'C': 'cosmics',
               'X': 'geometry', 'W': 'wavelenghts', 'Y': 'distorsion',
               'S': 'sky', 'T': 'standart', 'U': 'summ'}
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
        vlayout.setContentsMargins(0, 0, 0, 0)
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
        # print(files_path)

        if files_path:
            self.files = files_path
            self.yaml_box.setText(files_path)


class FitsOpenFile(QWidget):
    changed_path = Signal(str)

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
        self.dir = "/home/astrolander/Documents/Work/DATA"

        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.fits_box)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(0)

        self._open_folder_action.triggered.connect(self.on_open_folder)
        self.fits_box.editingFinished.connect(self.check_line)

    @Slot()
    def check_line(self):
        self.files = self.fits_box.text().split(',')
        if self.mode != 'n':
            self.files = self.files[0]
            self.dir = "/".join(self.files.split('/')[:-1])
            self.changed_path.emit(self.dir)
        else:
            self.files = [x.strip() for x in self.files]
            self.dir = "/".join(self.files[0].split('/')[:-1])
            self.changed_path.emit(self.dir)

    @Slot()
    def on_open_folder(self):
        regexps = "Fits (*.fits *.fts);;All (*);;" \
                  + "Fits R (*R*.fits);;Fits B (*B*.fits)"
        if self.mode == 'n':
            files_path = QFileDialog.getOpenFileNames(self, "Fits", self.dir,
                regexps)[0]
            self.dir = "/".join(files_path[0].split('/')[:-1])
            self.changed_path.emit(self.dir)
        elif self.mode == 'o':
            files_path = QFileDialog.getOpenFileName(self, "Fits", self.dir,
                regexps)[0]
            self.dir = "/".join(files_path.split('/')[:-1])
            self.changed_path.emit(self.dir)
        elif self.mode == 'w':
            files_path = QFileDialog.getSaveFileName(self, "Fits", self.dir,
                regexps)[0]
            self.dir = "/".join(files_path.split('/')[:-1])
            self.changed_path.emit(self.dir)
            ext = files_path.split('.')
            if len(ext) < 2:
                files_path = files_path + '.fits'
            # print(files_path)

        if files_path:
            if self.mode == 'n':
                self.files = files_path.copy()
                self.fits_box.setText(', '.join(files_path))
            else:
                self.files = files_path
                self.fits_box.setText(files_path)

    def fill_string(self, string):
        self.fits_box.setText(string)
        self.check_line()


class ChooseCalibration(QWidget):
    changed_path = Signal(str)

    def __init__(self, parent=None, name=None, calibs=[]):
        super().__init__(parent)
        self.name = QLabel(htmlHeader(name))

        self.if_raw = QRadioButton('Process calibration')
        self.if_processed = QRadioButton('From file')
        self.if_processed.setChecked(True)
        self.raw_input = FitsOpenFile()
        self.raw_output = FitsOpenFile(mode='w')
        self.processed_input = FitsOpenFile(tt='Processed calibration',
                                            mode='o')
        self.calibs = SelectPerformedCalibrations(calibs=calibs)

        self.rawgrid = QGridLayout()
        self.rawgrid.addWidget(self.raw_input, 1, 1)
        self.rawgrid.addWidget(self.raw_output, 1, 2)
        if calibs:
            self.rawgrid.addWidget(self.calibs, 2, 1, 1, 2)
        self.rawgrid.setVerticalSpacing(0)
        self.rawgrid.setContentsMargins(1, 1, 1, 1)

        self.flayout = QFormLayout(self)
        self.flayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.flayout.setContentsMargins(QMargins())
        self.flayout.addRow(self.name)
        self.flayout.addRow(self.if_raw, self.rawgrid)
        self.flayout.addRow(self.if_processed, self.processed_input)
        self.flayout.addRow(createHorizontalSeparator())
        self.flayout.setSpacing(1)
        self.flayout.setContentsMargins(1, 1, 1, 1)

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

    def read_dict(self, yml_dict):
        if 'calibration' in yml_dict:
            self.raw_output.fill_string(yml_dict['calibration'])
            self.processed_input.fill_string(yml_dict['calibration'])
        if 'rawfiles' in yml_dict:
            self.raw_input.fill_string(', '.join(yml_dict['rawfiles']))
        if 'additional' in yml_dict:
            self.calibs.fill_boxes(''.join(yml_dict['additional'].keys()))

    def fill_processed(self, processed_name):
        self.processed_input.fill_string(processed_name)

    def return_calib(self):
        set_raw = self.if_raw.isChecked()
        set_processed = self.if_processed.isChecked()
        if set_processed:
            return self.processed_input.files
        if set_raw:
            return self.raw_output.files


class DispersionWidget(ChooseCalibration):

    def __init__(self, parent=None, name=None, calibs=[]):
        self.ref_file = FitsOpenFile(mode='o', text='Reference')
        super().__init__(parent, name, calibs)
        # self.ref_file = FitsOpenFile()
        # self.ref_file.setEnabled(False)
        self.rawgrid.addWidget(self.ref_file, 1, 3)
        self.rawgrid.addWidget(self.calibs, 2, 1, 1, 3)
        self.enable_disable()

    @Slot()
    def enable_disable(self):
        set_raw = self.if_raw.isChecked()
        set_processed = self.if_processed.isChecked()
        self.raw_input.setEnabled(set_raw)
        self.raw_output.setEnabled(set_raw)
        self.calibs.setEnabled(set_raw)
        self.ref_file.setEnabled(set_raw)
        self.processed_input.setEnabled(set_processed)
        # self.flayout.addRow(self.ref_file)

    def return_dict(self):
        set_raw = self.if_raw.isChecked()
        set_processed = self.if_processed.isChecked()
        res = dict()
        if set_processed:
            res['calibration'] = self.processed_input.files
        if set_raw:
            res['calibration'] = self.raw_output.files
            res['rawfiles'] = self.raw_input.files
            res['rawfiles'].append(self.ref_file.files)

            add_calib = [x for x in self.calibs.checkboxes.keys() if
                         self.calibs.checkboxes[x].isChecked()]
            res['additional'] = add_calib
        return res


class SelectPerformedCalibrations(QWidget):

    def __init__(self, parent=None, calibs=[]):
        super().__init__(parent)

        calibs_d = getCalibDict()
        self.calibs = calibs
        self.checkboxes = {k: QCheckBox(calibs_d[k]) for k in calibs}
        # for i in self.checkboxes.keys():
        #     if i not in calibs:
        #         self.checkboxes[i].setEnabled(False)

        hgrid = QHBoxLayout(self)
        for i in self.checkboxes.values():
            hgrid.addWidget(i)
        hgrid.setContentsMargins(0, 0, 0, 0)
        hgrid.setSpacing(0)

    def fill_boxes(self, string):
        for i in string:
            if i in self.checkboxes:
                self.checkboxes[i].setChecked(True)


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.bias = ChooseCalibration(name='Bias', calibs='')
        self.dark = ChooseCalibration(name='Dark', calibs='B')
        self.corr = ChooseCalibration(name='X-correction', calibs='BDC')
        self.flat = ChooseCalibration(name='Flat', calibs='BX')
        self.disp = DispersionWidget(name='Wavelengths', calibs='BDCF')
        self.dist = ChooseCalibration(name='Y-correction', calibs='BDFCW')
        self.calibs = SelectPerformedCalibrations(calibs='BDFCXWYU')
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
        glayout.addWidget(self.frames, 1, 2)
        glayout.addWidget(self.result_path, 1, 1)
        glayout.addWidget(self.yaml_save, 1, 3)
        glayout.addWidget(self.load_button, 2, 1)
        glayout.addWidget(self.calibs, 2, 2)
        glayout.addWidget(self.start_button, 2, 3)

        vlayout.addLayout(glayout, 4, 1, 1, 3)
        self.start_button.clicked.connect(self.generate_yaml_config)
        self.load_button.clicked.connect(self.read_yaml_config)

    @Slot()
    def generate_yaml_config(self):
        res = dict()
        calibs_d = getCalibDict(short=True)
        # "Вложенные" списки калибровок
        res['bias'] = self.bias.return_dict()
        res['dark'] = self.dark.return_dict()
        res['corr'] = self.corr.return_dict()
        res['flat'] = self.flat.return_dict()
        res['disp'] = self.disp.return_dict()
        res['dist'] = self.dist.return_dict()
        # "Да/Нет" калибровки
        res['cosmics'] = {'calibration': True}
        res['summ'] = {'calibration': True}

        if self.frames.files:
            res['object'] = dict()
            res['object']['filenames'] = self.frames.files
            res['object']['output'] = self.result_path.files
            obj_cals = [x for x in self.calibs.checkboxes.keys()
                        if self.calibs.checkboxes[x].isChecked()]
            res['object']['additional'] = obj_cals

        # Пути к дополнительным калибровкам для калибровок
        for c in res.keys():
            if 'additional' in res[c]:
                res[c]['additional'] = {k: res[calibs_d[k]]['calibration']
                                        for k in res[c]['additional']}
        # Космики и суммирование не самостоятельные калибровки
        del res['cosmics']
        del res['summ']

        yaml_name = self.yaml_save.files
        if not yaml_name:
            yaml_name = 'last_config.yaml'

        stream = open(yaml_name, 'w')
        yaml.dump(res, stream)
        stream.close()
        # print(yaml.dump(res))
        # print(res)

    @Slot()
    def read_yaml_config(self):
        file_path = QFileDialog.getOpenFileName(self, "Yaml", "/home/",
                "YAML (*.yaml *.yml);;All (*)")[0]
        file = open(file_path, 'r')
        config = yaml.load(file, Loader=yaml.SafeLoader)
        file.close()

        if 'bias' in config:
            self.bias.read_dict(config['bias'])
        if 'dark' in config:
            self.dark.read_dict(config['dark'])
        if 'corr' in config:
            self.corr.read_dict(config['corr'])
        if 'flat' in config:
            self.flat.read_dict(config['flat'])
        if 'disp' in config:
            self.disp.read_dict(config['disp'])
        if 'dist' in config:
            self.dist.read_dict(config['dist'])

        if 'object' in config:
            if 'output' in config['object']:
                self.result_path.fill_string(config['object']['output'])
            if 'filenames' in config['object']:
                fnames = ', '.join(config['object']['filenames'])
                self.frames.fill_string(fnames)
            if 'additional' in config['object']:
                cal = ''.join(config['object']['additional'].keys())
                self.calibs.fill_boxes(cal)
                for letter in cal:
                    proc_name = config['object']['additional'][letter]
                    if letter == 'B':
                        self.bias.fill_processed(proc_name)
                    if letter == 'D':
                        self.dark.fill_processed(proc_name)
                    if letter == 'X':
                        self.corr.fill_processed(proc_name)
                    if letter == 'F':
                        self.flat.fill_processed(proc_name)
                    if letter == 'W':
                        self.disp.fill_processed(proc_name)
                    if letter == 'Y':
                        self.dist.fill_processed(proc_name)

    @Slot()
    def test_print(self):
        print('test')


if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())
