#!/usr/bin/env python3

from seamcarver import SeamCarver
from PIL import Image
import sys, os, traceback

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QPushButton, QHBoxLayout,
    QVBoxLayout, QSpinBox, QFileDialog, QGridLayout, QRadioButton
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class SeamCarverGui(QMainWindow):
    image = None
    seam_v = None
    seam_h = None
    is_vertical = True

    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()

        self.setWindowTitle('CSCI 30 Seam Carving')
        self.setFixedSize(540, 150)
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        self.generalLayout = QVBoxLayout()

        self.btns = QGridLayout()
        open = QPushButton('Open image')
        open.clicked.connect(self.open_image)
        self.btns.addWidget(open, 0, 0)
        save = QPushButton('Save image')
        save.clicked.connect(self.save_image)
        self.btns.addWidget(save, 1, 0)

        show_seam = QPushButton('Show seam')
        show_seam.clicked.connect(self.show_seam)
        self.btns.addWidget(show_seam, 0, 1)
        remove_seam = QPushButton('Remove seam')
        remove_seam.clicked.connect(self.remove_seam)
        self.btns.addWidget(remove_seam, 1, 1)

        orient = QHBoxLayout()
        orient.addWidget(QLabel('Seam:'))
        self.toggle_v = QRadioButton('&Vertical', self)
        self.toggle_v.toggle()
        self.toggle_v.toggled.connect(self.toggle_orientation)
        orient.addWidget(self.toggle_v)
        self.toggle_h = QRadioButton('&Horizontal', self)
        self.toggle_h.toggled.connect(self.toggle_orientation)
        orient.addWidget(self.toggle_h)
        self.btns.addLayout(orient, 0, 2)

        rep_grp = QHBoxLayout()
        rep_grp.addWidget(QLabel('Repeat:'))

        self.repeat = QSpinBox()
        self.repeat.setMinimum(1)
        self.repeat.setMaximum(100)
        rep_grp.addWidget(self.repeat)
        self.btns.addLayout(rep_grp, 1, 2)

        self.imgview = QLabel()
        #self.imgview.setScaledContents(True)

        self.status = QLabel('Please open an image.')

        self.generalLayout.addLayout(self.btns)
        self.generalLayout.addWidget(self.imgview)
        self.generalLayout.addWidget(self.status)
        centralWidget.setLayout(self.generalLayout)

    def open_image(self):
        fname = QFileDialog.getOpenFileName(self, 'Open image', '.', 'Image files (*.jpg *.png)')[0]
        if not fname or fname[0] is None: return
        self.update_status(f'Loading {os.path.basename(fname)}...')
        try:
            self.image = SeamCarver(Image.open(fname))
            self.update_display()
        except:
            self.update_status(f'Error loading {os.path.basename(fname)}!')
            raise
        self.seam_v = None
        self.seam_h = None
        self.update_status(f'Loaded {os.path.basename(fname)}. Now compute or remove seam.')

    def save_image(self):
        if self.image is None: return
        fname = QFileDialog.getSaveFileName(self, 'Save image', '.', 'Image files (*.jpg *.png)')[0]
        if not fname or fname[0] is None: return
        self.update_status(f'Saving {os.path.basename(fname)}...')
        try:
            self.image.picture().save(fname)
        except:
            self.update_status(f'Error saving {os.path.basename(fname)}!')
            raise
        self.seam_v = None
        self.seam_h = None
        self.update_status(f'Saved {os.path.basename(fname)}.')

    def compute_vertical_seam(self, count=0):
        if self.seam_v is None:
            if count:
                self.update_status(f'Computing vertical seam {count+1}...')
            else:
                self.update_status(f'Computing vertical seam...')
            self.seam_v = self.image.find_vertical_seam()
            if count:
                self.update_status(f'Computed vertical seam {count+1}.')
            else:
                self.update_status(f'Computed vertical seam.')

    def compute_horizontal_seam(self, count=0):
        if self.seam_h is None:
            if count:
                self.update_status(f'Computing horizontal seam {count+1}...')
            else:
                self.update_status(f'Computing horizontal seam...')
            self.seam_h = self.image.find_horizontal_seam()
            if count:
                self.update_status(f'Computed horizontal seam {count+1}.')
            else:
                self.update_status(f'Computed horizontal seam.')

    def _show_seam(self):
        seam_type = 'vertical' if self.is_vertical else 'horizontal'
        if self.image is None: return
        if self.is_vertical:
            self.compute_vertical_seam()
        else:
            self.compute_horizontal_seam()

    def _color_seam(self):
        seam_type = 'vertical' if self.is_vertical else 'horizontal'
        if self.is_vertical:
            self.image.color_seam(self.seam_v)
        else:
            self.image.color_seam(self.seam_h, False)
        self.update_display()
        self.update_status(f'Computed {seam_type} seam, as shown in pink.')

    def show_seam(self):
        worker = Worker(self._show_seam)
        worker.signals.finished.connect(self._color_seam)
        self.threadpool.start(worker)

    def _remove_seam(self):
        seam_type = 'vertical' if self.is_vertical else 'horizontal'
        count = 0
        while True:
            if self.is_vertical:
                self.compute_vertical_seam(count)
                self.image.remove_vertical_seam(self.seam_v)
            else:
                self.compute_horizontal_seam(count)
                self.image.remove_horizontal_seam(self.seam_h)
            self.update_display()
            self.seam_v = None
            self.seam_h = None
            count += 1

            try:
                reps = int(self.repeat.value())
            except ValueError:
                break
            if reps <= 1: break
            reps -= 1
            self.repeat.setValue(reps)

        self.repeat.setValue(1)
        if count > 1:
            self.update_status(f'Removed {count} {seam_type} seams.')
        else:
            self.update_status(f'Removed {seam_type} seam.')

    def remove_seam(self):
        if self.image is None: return
        worker = Worker(self._remove_seam)
        self.threadpool.start(worker)

    def toggle_orientation(self):
        if self.toggle_v.isChecked():
            self.is_vertical = True
        elif self.toggle_h.isChecked():
            self.is_vertical = False
        else:
            raise AssertionError('something went horribly wrong!')

    def update_display(self):
        self.imgview.setPixmap(self.image._to_pixmap())
        btns_h = self.btns.geometry().height()
        new_w = max(self.image.width(), 540)
        new_h = self.image.height() + btns_h + self.status.height() + 20
        self.setFixedSize(new_w, new_h)

    def update_status(self, msg):
        self.status.setText(msg)

if __name__ == '__main__':
    app = QApplication([])
    window = SeamCarverGui()
    window.show()
    sys.exit(app.exec())
