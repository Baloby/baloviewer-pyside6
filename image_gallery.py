import os
import shiboken2

from PySide6.QtCore import QSize, Qt, QTimer, QEventLoop, Slot
from PySide6.QtGui import QCursor, QImageReader, QMovie, QPixmap
from PySide6.QtWidgets import QAbstractItemView, QLabel, QListWidget, QListWidgetItem


class ImageGallery(QListWidget):
    def __init__(self, parent):
        super(ImageGallery, self).__init__()
        self.size = QSize(180, 120)
        self.parent = parent

    def add_images(self, images):
        """add images list to the list box

        Args:
            images (list): list of image path
        """
        self.clear()
        self.images = images
        if len(images):
            QTimer.singleShot(0, self.load_images)

    def for_loop_files(self, images, interval=100, parent=None, objectName=""):
        timer = QTimer(parent=parent, singleShot=True, interval=interval)
        if objectName:
            timer.setObjectName(objectName)
        loop = QEventLoop(timer)
        timer.timeout.connect(loop.quit)
        timer.destroyed.connect(loop.quit)

        for image_path in images:
            if shiboken2.isValid(timer):
                timer.start()
                loop.exec_()
                yield image_path

    @Slot()
    def load_images(self):
        for path in self.for_loop_files(images=self.images, interval=1, parent=self, objectName="icon_timer"):
            if os.path.isfile(path):
                image = QLabel()
                image.setAlignment(Qt.AlignCenter)

                image_reader = QImageReader(path)
                if image_reader.imageCount() > 1:
                    # Animated image
                    movie = QMovie(path)
                    movie.setCacheMode(QMovie.CacheAll)
                    movie.jumpToFrame(0)
                    movie.setScaledSize(self.size)
                    image.setMovie(movie)
                    movie.start()
                else:
                    image.setPixmap((QPixmap(path).scaled(
                        self.size, Qt.KeepAspectRatio, Qt.FastTransformation)))

                item = QListWidgetItem(self)
                item.setSizeHint(self.size)
                self.setItemWidget(item, image)

                if path == self.images[self.parent.index]:
                    self.select_row(self.parent.index)

    def select_row(self, index):
        if index > -1 and index < self.count():
            self.setCurrentRow(index)
            self.scrollToItem(self.item(index), QAbstractItemView.PositionAtCenter)

    def select_row_pos(self):
        pos = self.mapFromGlobal(QCursor.pos())
        item = self.itemAt(pos)
        if item:
            self.setCurrentItem(item)
            return self.currentRow()

    def remove_row(self, index):
        if index > -1 and index < self.count():
            item = self.takeItem(index)  # noqa : F841
            del item
            self.scrollToItem(self.item(index), QAbstractItemView.PositionAtCenter)
