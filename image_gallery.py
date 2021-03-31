import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QImageReader, QMovie, QPixmap
from PySide6.QtWidgets import QAbstractItemView, QLabel, QListWidget, QListWidgetItem


class ImageGallery(QListWidget):
    def __init__(self):
        super(ImageGallery, self).__init__()
        self.image_width = 180
        self.image_height = 120

    def add_images(self, images):
        """add images list to the list box

        Args:
            images (list): list of image path
        """
        self.clear()

        if len(images):
            size = QSize(self.image_width, self.image_height)

            for image_path in images:
                image = QLabel()
                image.setAlignment(Qt.AlignCenter)
                if os.path.isfile(image_path):
                    image_reader = QImageReader(image_path)
                    if image_reader.imageCount() > 1:
                        # Animated image
                        movie = QMovie(image_path)
                        movie.setCacheMode(QMovie.CacheAll)
                        movie.jumpToFrame(0)
                        size = QSize(self.image_height, self.image_height)
                        movie.setScaledSize(size)
                        image.setMovie(movie)
                        movie.start()
                    else:
                        image.setPixmap((QPixmap(image_path).scaled(size, Qt.KeepAspectRatio)))

                item = QListWidgetItem(self)
                item.setSizeHint(size)
                self.setItemWidget(item, image)

    def select_row(self, index):
        if index > -1 and index < self.count():
            self.setCurrentRow(index)
            self.scrollToItem(self.item(index), QAbstractItemView.PositionAtCenter)

    def select_row_pos(self):
        pos = self.mapFromGlobal(QCursor.pos())
        item = self.itemAt(pos)
        self.setCurrentItem(item)
        return self.currentRow()

    def remove_row(self, index):
        if index > -1 and index < self.count():
            item = self.takeItem(index) # noqa : F841
            del item
            self.scrollToItem(self.item(index), QAbstractItemView.PositionAtCenter)
