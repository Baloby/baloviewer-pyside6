import os.path

from datetime import datetime
from math import floor, log, pow
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton)
from PySide6.QtGui import QImageReader, QPixmap, QMovie


class ImageDialog(QDialog):
    def __init__(self, src, dst):
        super(ImageDialog, self).__init__()
        self.set_up_ui(src, dst)
        self.open()

    def set_up_ui(self, src, dst):
        self.setWindowTitle('File Already exists')
        self.setFixedHeight(300)
        self.setFixedWidth(440)

        self.dst_dirname, self.dst_file = os.path.split(dst)
        self.dst_filename, self.dst_file_extension = os.path.splitext(self.dst_file)

        label_src_image = QLabel(self)
        label_src_image.setMinimumSize(180, 120)
        label_src_image.setAlignment(Qt.AlignCenter)
        label_dst_image = QLabel(self)
        label_dst_image.setMinimumSize(180, 120)
        label_dst_image.setAlignment(Qt.AlignCenter)

        self.display_image(label_src_image, src)
        self.display_image(label_dst_image, dst)

        str_format = "<p align='center'>Date : {} <br> size : {}</p>"
        src_date = datetime.fromtimestamp(os.path.getmtime(src)).ctime()
        src_size = self.convert_size(os.path.getsize(src))
        src_info = str_format.format(src_date, src_size)
        dst_date = datetime.fromtimestamp(os.path.getmtime(src)).ctime()
        dst_size = self.convert_size(os.path.getsize(dst))
        dst_info = str_format.format(dst_date, dst_size)

        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)

        # button box
        button_box = QDialogButtonBox()
        button_box.setOrientation(Qt.Horizontal)
        button_box.setStandardButtons(QDialogButtonBox.Cancel)

        self.button_rename = QPushButton('Rename')
        self.button_rename.clicked.connect(lambda: QDialog.done(self, 3))
        button_box.addButton(self.button_rename, QDialogButtonBox.ApplyRole)

        self.button_overwrite = button_box.addButton('Overwrite', QDialogButtonBox.AcceptRole)

        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)

        # line edit
        self.edit_file_name = QLineEdit()
        self.edit_file_name.textChanged.connect(self.text_changed)
        self.edit_file_name.setText(os.path.basename(dst))

        button_new_name = QPushButton('Suggest new name')
        layout_new_name = QHBoxLayout()
        layout_new_name.addWidget(self.edit_file_name)
        layout_new_name.addWidget(button_new_name)
        button_new_name.clicked.connect(lambda: self.sugest_new_name(dst))

        self.grid = QGridLayout()
        # self.grid.setVerticalSpacing(10)
        self.grid.addWidget(QLabel('This action will overwrite the destination.'), 0, 0, 1, 2)
        self.grid.addWidget(QLabel('<b>Source</b>'), 1, 0, Qt.AlignHCenter)
        self.grid.addWidget(QLabel('<b>Destination</b>'), 1, 1, Qt.AlignHCenter)

        self.grid.addWidget(label_dst_image, 2, 0, Qt.AlignHCenter)
        self.grid.addWidget(label_src_image, 2, 1, Qt.AlignHCenter)

        self.grid.addWidget(QLabel(src_info), 3, 0, Qt.AlignHCenter)
        self.grid.addWidget(QLabel(dst_info), 3, 1, Qt.AlignHCenter)

        self.grid.addLayout(layout_new_name, 4, 0, 1, 2)

        self.grid.addWidget(frame, 6, 0, 1, 2)

        self.grid.addWidget(button_box, 7, 0, 1, 2)

        self.setLayout(self.grid)

    def display_image(self, label, file):
        image_reader = QImageReader(file)
        if image_reader.imageCount() > 1:
            movie = QMovie(file,)
            movie.setCacheMode(QMovie.CacheAll)
            movie.jumpToFrame(0)
            size = QSize(min(label.width(), label.height()), min(label.width(), label.height()))
            movie.setScaledSize(size)
            label.setMovie(movie)
            movie.start()
        else:
            label.setPixmap((QPixmap(file).scaled(label.size(), Qt.KeepAspectRatio)))

    def convert_size(self, size):
        if size == 0:
            return '0 B'
        size_name = ('B', 'KB', 'MB')
        i = int(floor(log(size, 1024)))
        p = pow(1024, i)
        s = round(size / p, 2)
        return '%s %s' % (s, size_name[i])

    def sugest_new_name(self, dst):
        count = 0
        while os.path.isfile(os.path.join(self.dst_dirname, os.path.basename(self.edit_file_name.text()))):
            count += 1
            new_name = self.dst_filename + " ({})".format(count) + self.dst_file_extension
            self.edit_file_name.setText(new_name)

    def text_changed(self):
        if self.dst_file == self.edit_file_name.text():
            self.button_rename.setEnabled(False)
            self.button_overwrite.setEnabled(True)
        else:
            self.button_rename.setEnabled(True)
            self.button_overwrite.setEnabled(False)
