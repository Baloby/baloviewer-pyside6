import os
import glob
import shutil

from optparse import OptionParser
from PySide6.QtCore import QEvent, QPoint, QSettings, Qt
from PySide6.QtGui import QAction, QIcon, QImageReader, QMovie, QPixmap, QTransform
from PySide6.QtWidgets import (QDialog, QDockWidget, QFileDialog, QLabel, QMainWindow,
                               QMenu, QMessageBox, QScrollArea, QWidget)
from image_dialog import ImageDialog
from image_gallery import ImageGallery


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.images = []
        self.index = -1
        self.ratio = 1  # ratio for QLabel image
        self.mouse_position = None
        self.settings = None

        # Extensions
        self.extensions = []
        for format in QImageReader.supportedImageFormats():
            self.extensions.append(format.data().decode('utf-8'))

        # Filters
        self.filters = []
        for extension in self.extensions:
            self.filters.append('*.{0}'.format(str(extension)))

        # UI
        self.set_up_ui()

        # settings
        self.load_settings()

    def on_message_received(self, msg):
        """ on message received from single application

        Args:
            msg (string): file path
        """
        self.create_images(msg)
        self.display_image()

    def set_up_ui(self):
        # Status Bar
        self.status_bar = self.statusBar()
        self.label_name = QLabel()
        self.label_numero = QLabel()
        self.status_bar.addPermanentWidget(self.label_name, 1)
        self.status_bar.addPermanentWidget(self.label_numero, 0)

        # Main Window
        self.setWindowTitle('BaloViewer')
        self.setWindowIcon(QIcon('baloviewer.ico'))

        # Label image
        self.image = QLabel()
        self.image.setScaledContents(True)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image)
        self.scroll_area.showMaximized()
        self.scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.viewport().installEventFilter(self)

        # image list
        self.image_gallery = ImageGallery()
        self.image_gallery.itemClicked.connect(self.image_gallery_clicked)
        self.image_gallery.viewport().installEventFilter(self)
        self.dock_widget = QDockWidget('Image Gallery', self)
        self.dock_widget.setWidget(self.image_gallery)
        self.dock_widget.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)

        # central widget
        self.setCentralWidget(self.scroll_area)

        # Action bar
        self.create_actions()
        self.create_menubar()
        self.create_toolbar()

        # option parser
        parser = OptionParser()
        parser.add_option("-f", "--file", dest="filename", help="open a file")
        (options, args) = parser.parse_args()
        parser_file = options.filename
        if parser_file is not None and os.path.isfile(parser_file):
            self.create_images(parser_file)
            self.display_image()

    def create_actions(self):
        # Action Open
        self.action_open = QAction(QIcon.fromTheme('document-open'), 'Open', self)
        self.action_open.setShortcut('Ctrl+O')
        self.action_open.setStatusTip('Open file')
        self.action_open.triggered.connect(self.open)

        # Action Save
        self.action_save = QAction(QIcon.fromTheme('document-save'), 'Save', self)
        self.action_save.setShortcut('Ctrl+S')
        self.action_save.setStatusTip('Save file')
        self.action_save.triggered.connect(self.save)

        # Action Copy
        self.action_copy = QAction(QIcon.fromTheme('edit-copy'), 'Copy', self)
        self.action_copy.setStatusTip('Copy')
        self.action_copy.triggered.connect(self.copy)

        # Action move
        self.action_move = QAction(QIcon.fromTheme('edit-cut'), 'Move', self)
        self.action_move.setStatusTip('Move')
        self.action_move.triggered.connect(self.move)

        # Action Delete
        self.action_delete = QAction(QIcon.fromTheme('edit-delete'), 'Delete', self)
        self.action_delete.setStatusTip('Delete')
        self.action_delete.triggered.connect(self.delete)

        # Action Quit
        self.action_quit = QAction(QIcon.fromTheme('application-exit'), 'Quit', self)
        self.action_quit.setShortcut('Ctrl+Q')
        self.action_quit.setStatusTip('Quit')
        self.action_quit.triggered.connect(self.close)

        # Action Rotate left
        self.action_rotate_left = QAction(QIcon.fromTheme('object-rotate-left'), 'Rotate left', self)
        self.action_rotate_left.setStatusTip('Rotate left')
        self.action_rotate_left.triggered.connect(self.rotate_left)

        # Action Rotate right
        self.action_rotate_right = QAction(QIcon.fromTheme('object-rotate-right'), 'Rotate right', self)
        self.action_rotate_right.setStatusTip('Rotate right')
        self.action_rotate_right.triggered.connect(self.rotate_right)

        # Action Mirror
        self.action_flip_horizontal = QAction(QIcon.fromTheme('object-flip-horizontal'), 'Flip horizontally', self)
        self.action_flip_horizontal.setStatusTip('Flip horizontally')
        self.action_flip_horizontal.triggered.connect(self.flip_horizontal)

        # Action Flip vertical
        self.action_flip_vertical = QAction(QIcon.fromTheme('object-flip-vertical'), 'Flip vertically', self)
        self.action_flip_vertical.setStatusTip('Flip vertically')
        self.action_flip_vertical.triggered.connect(self.flip_vertical)

        # Action Previous image
        self.action_previous_image = QAction(QIcon.fromTheme('go-previous'), 'Previous image', self)
        self.action_previous_image.setStatusTip('Previous image')
        self.action_previous_image.triggered.connect(self.previous_image)

        # Action Full screen
        self.action_fullscreen = QAction(QIcon.fromTheme('view-fullscreen'), 'Full screen', self)
        self.action_fullscreen.setStatusTip('Full screen')
        self.action_fullscreen.triggered.connect(self.fullscreen)

        # Action Normal size
        self.action_normal_size = QAction(QIcon.fromTheme('zoom-original'), 'Normal size', self)
        self.action_normal_size.setStatusTip('Normal Size')
        self.action_normal_size.triggered.connect(self.normal_size)

        # Action Fit Screen
        self.action_fit_screen = QAction(QIcon.fromTheme('zoom-fit-best'), 'Fit to screen', self)
        self.action_fit_screen.setStatusTip('Fit to screen')
        self.action_fit_screen.setCheckable(True)
        self.action_fit_screen.triggered.connect(self.fit_screen)

        # Action Zoom in
        self.action_zoom_in = QAction(QIcon.fromTheme('zoom-in'), 'Zoom in', self)
        self.action_zoom_in.setStatusTip('Zoom in')
        self.action_zoom_in.triggered.connect(self.zoom_in)

        # Action Zoom out
        self.action_zoom_out = QAction(QIcon.fromTheme('zoom-out'), 'Zoom out', self)
        self.action_zoom_out.setStatusTip('Zoom out')
        self.action_zoom_out.triggered.connect(self.zoom_out)

        # Action Fit height
        self.action_fit_vertical = QAction('Fit vertically', self)
        self.action_fit_vertical.setStatusTip('Fit vertically')
        self.action_fit_vertical.setCheckable(True)
        self.action_fit_vertical.triggered.connect(self.fit_height)

        # Action Fit width
        self.action_fit_horizontal = QAction('Fit horizontally', self)
        self.action_fit_horizontal.setStatusTip('Fit horizontally')
        self.action_fit_horizontal.setCheckable(True)
        self.action_fit_horizontal.triggered.connect(self.fit_width)

        # Action Fit width
        self.action_fit_horizontal = QAction('Fit horizontally', self)
        self.action_fit_horizontal.setStatusTip('Fit horizontally')
        self.action_fit_horizontal.setCheckable(True)
        self.action_fit_horizontal.triggered.connect(self.fit_width)

        # Action Image list
        self.action_image_gallery = QAction('Image gallery', self)
        self.action_image_gallery.setStatusTip('Image gallery')
        self.action_image_gallery.setCheckable(True)
        self.action_image_gallery.triggered.connect(self.image_gallery_triggered)

        # Action Next_image
        self.action_next_image = QAction(QIcon.fromTheme('go-next'), 'Next image', self)
        self.action_next_image.setStatusTip('Next image')
        self.action_next_image.triggered.connect(self.next_image)

        # Action First image
        self.action_first_image = QAction(QIcon.fromTheme('go-first'), 'First image', self)
        self.action_first_image.setStatusTip('First image')
        self.action_first_image.triggered.connect(self.first_image)

        # Action Last image
        self.action_last_image = QAction(QIcon.fromTheme('go-last'), 'Last image', self)
        self.action_last_image.setStatusTip('Last image')
        self.action_last_image.triggered.connect(self.last_image)

        # Action About
        self.action_about = QAction(QIcon.fromTheme('help-about'), 'About', self)
        self.action_about.setStatusTip('About')
        self.action_about.triggered.connect(self.about)

    def create_menubar(self):
        self.menubar = self.menuBar()

        # File
        self.menu_file = self.menubar.addMenu('File')
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_copy)
        self.menu_file.addAction(self.action_move)
        self.menu_file.addAction(self.action_delete)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_quit)

        # Edit
        self.menu_edit = self.menubar.addMenu('Edit')
        self.menu_edit.addAction(self.action_rotate_left)
        self.menu_edit.addAction(self.action_rotate_right)
        self.menu_edit.addSeparator()
        self.menu_edit.addAction(self.action_flip_horizontal)
        self.menu_edit.addAction(self.action_flip_vertical)

        # View
        self.menu_view = self.menubar.addMenu('View')
        self.menu_view.addAction(self.action_fullscreen)
        self.menu_view.addAction(self.action_normal_size)
        self.menu_view.addAction(self.action_fit_screen)
        self.menu_view.addSeparator()
        self.menu_view.addAction(self.action_zoom_in)
        self.menu_view.addAction(self.action_zoom_out)
        self.menu_view.addSeparator()
        self.menu_view.addAction(self.action_fit_vertical)
        self.menu_view.addAction(self.action_fit_horizontal)
        self.menu_view.addSeparator()
        self.menu_view.addAction(self.action_image_gallery)

        # Go
        self.menu_go = self.menubar.addMenu('Go')
        self.menu_go.addAction(self.action_previous_image)
        self.menu_go.addAction(self.action_next_image)
        self.menu_go.addSeparator()
        self.menu_go.addAction(self.action_first_image)
        self.menu_go.addAction(self.action_last_image)

        # About
        self.menu_about = self.menubar.addMenu('About')
        self.menu_about.addAction(self.action_about)

    def create_toolbar(self):
        self.toolbar = self.addToolBar('Tool bar')

        self.toolbar.addAction(self.action_open)
        self.toolbar.addAction(self.action_save)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_fullscreen)
        self.toolbar.addAction(self.action_normal_size)
        self.toolbar.addAction(self.action_fit_screen)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_zoom_in)
        self.toolbar.addAction(self.action_zoom_out)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_rotate_left)
        self.toolbar.addAction(self.action_rotate_right)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_first_image)
        self.toolbar.addAction(self.action_previous_image)
        self.toolbar.addAction(self.action_next_image)
        self.toolbar.addAction(self.action_last_image)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_copy)
        self.toolbar.addAction(self.action_move)

    def load_settings(self):
        self.settings = QSettings()
        check_state = self.settings.value('view/image_gallery', True, type=bool)
        self.action_image_gallery.setChecked(check_state)
        self.image_gallery_triggered()

    def contextMenuEvent(self, QContextMenuEvent):
        menu = QMenu()
        menu.addAction(self.action_fullscreen)
        menu.addSeparator()
        menu.addAction(self.action_image_gallery)
        menu.addSeparator()
        menu.addAction(self.action_previous_image)
        menu.addAction(self.action_next_image)
        menu.addSeparator()
        menu.addAction(self.action_normal_size)
        menu.addAction(self.action_fit_screen)
        menu.addAction(self.action_fit_vertical)
        menu.addAction(self.action_fit_horizontal)
        menu.addSeparator()
        menu.addAction(self.action_zoom_in)
        menu.addAction(self.action_zoom_out)
        menu.addSeparator()
        menu.addAction(self.action_copy)
        menu.addAction(self.action_move)
        menu.addSeparator()
        menu.addAction(self.action_delete)
        menu.exec_(QContextMenuEvent.globalPos())

    def eventFilter(self, obj, event):
        """ filter events for wheel events

        Args:
            obj (QWidget): scroll_area
            event (QEvent): event
        """

        # try:
        if event.type() == QEvent.Wheel:
            if event.angleDelta().y() < 0:
                self.next_image()
            else:
                self.previous_image()

            return True
        elif event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            index = self.image_gallery.select_row_pos()
            if index > -1:
                self.index = index
                self.display_image()
                return True
        # pass the event on to the parent class
        return super(QMainWindow, self).eventFilter(obj, event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Delete:
            self.delete()
        elif key == Qt.Key_Left:
            self.previous_image()
        elif key == Qt.Key_Right:
            self.next_image()
        elif key == Qt.Key_PageUp:
            self.first_image()
        elif key == Qt.Key_PageDown:
            self.last_image()
        elif key == Qt.Key_Escape and self.isFullScreen():
            self.fullscreen()
        else:
            QWidget.keyPressEvent(self, event)

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.fullscreen()

    def mousePressEvent(self, QMouseEvent):
        self.mouse_position = QMouseEvent.pos()

    def mouseMoveEvent(self, QMouseEvent):
        diff = QPoint(QMouseEvent.pos() - self.mouse_position)
        self.mouse_position = QMouseEvent.pos()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().value() - diff.y())
        self.scroll_area.horizontalScrollBar().setValue(self.scroll_area.horizontalScrollBar().value() - diff.x())

    def resizeEvent(self, event):
        if not self.index == -1:
            self.display_image()

    def create_images(self, filename):
        """Create image list

        Args:
            filename (string): file from which to retrieve the list of images in the folder
        """

        self.images.clear()
        # get images only with an allowed extension
        for ext in self.extensions:
            self.images += glob.glob(os.path.join(glob.escape(os.path.dirname(filename)), '*.' +
                                                  ''.join('[%s%s]' % (e.lower(), e.upper()) for e in ext)))

        self.images.sort()
        if filename in self.images:
            self.index = self.images.index(filename)
        else:
            self.index = -1

        # iamge list
        self.image_gallery.add_images(self.images)

    def remove_index(self):
        """ remove file from list images and display next or previous image
        """

        del self.images[self.index]
        self.image_gallery.remove_row(self.index)

        if len(self.images) == 0:
            self.images.clear()
            self.index = -1
            self.image.clear()
            self.image.resize(self.image.minimumSizeHint())
        elif self.index < len(self.images) - 1:
            self.display_image()
        else:
            self.index = len(self.images) - 1
            self.display_image()

    def display_image(self):
        if not self.index == -1:
            self.image.clear()
            self.image.resize(self.image.minimumSizeHint())

            file = self.images[self.index]
            if os.path.isfile(file):
                self.label_name.setText(file)
                self.label_numero.setText(str(self.index + 1) + ' / ' + str(len(self.images)))

                # image list
                self.image_gallery.select_row(self.index)

                image_reader = QImageReader(file)
                if image_reader.imageCount() > 1:
                    # Animated image
                    movie = QMovie(file)
                    movie.setCacheMode(QMovie.CacheAll)
                    movie.jumpToFrame(0)
                    movie_size = movie.currentPixmap().size()
                    self.image.setMovie(movie)
                    self.image.resize(movie_size)
                    movie.start()
                else:
                    self.image.setPixmap(QPixmap(file))
                    self.image.resize(self.image.pixmap().size())

                # fit image
                if self.action_fit_screen.isChecked():
                    self.fit_screen()
                elif self.action_fit_horizontal.isChecked():
                    self.fit_width()
                elif self.action_fit_vertical.isChecked():
                    self.fit_height()

                else:
                    self.ratio = 1.0

                self.action_zoom_in.setEnabled(True)
                self.action_zoom_out.setEnabled(True)

                # scrollbar position
                self.scroll_area.verticalScrollBar().setSliderPosition(0)
                self.scroll_area.horizontalScrollBar().setSliderPosition(0)

    def resize_image(self):
        if self.action_fit_screen.isChecked():
            self.fit_screen()
        elif self.action_fit_horizontal.isChecked():
            self.fit_width()
        elif self.action_fit_vertical.isChecked():
            self.fit_height()
        elif self.image.pixmap():
            self.image.resize(self.ratio * self.image.pixmap().size())
        elif movie := self.image.movie():
            movie.jumpToFrame(0)
            movie_size = movie.currentPixmap().size()
            self.image.resize(self.ratio * movie_size)

    def open(self):
        """Open a file
        """
        filename, filtr = QFileDialog.getOpenFileName(
            self, 'Open file', os.path.expanduser('~'), "Images ({0});;All files (*)".format((' '.join(self.filters)))
        )
        if filename:
            try:
                self.create_images(filename)
                self.display_image()
            except Exception as e:
                self.message_box_error('Error', 'The file cannot be opened', e)

    def save(self):
        if not self.index == -1:
            if not self.image.pixmap().save(self.images[self.index]):
                self.message_box_error('Error', 'This file cannot be saved')

    def copy(self):
        self.move_copy_dialog(True)

    def move(self):
        self.move_copy_dialog(False)

    def move_copy_dialog(self, copy):
        """dialog for copy or move a file

        Args:
            copy (boolean): True to copy, False to move
        """

        if copy:
            libelle = "Move to"
        else:
            libelle = "Copy to"

        if not self.index == -1:
            directory = QFileDialog.getExistingDirectory(self, libelle, self.images[self.index],
                                                         QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog)
            if directory:
                file = os.path.join(directory, os.path.basename(self.images[self.index]))
                if not os.path.isfile(file):
                    self.move_copy_file(self.images[self.index], file, copy)
                else:
                    dialog = ImageDialog(self.images[self.index], file)
                    result = dialog.exec_()
                    if result == QDialog.Accepted:
                        self.move_copy_file(self.images[self.index], file, copy)
                    elif result == 3:
                        # renamme
                        self.move_copy_file(self.images[self.index],
                                            os.path.join(directory, os.path.basename(dialog.edit_file_name.text())),
                                            copy)

    def move_copy_file(self, src, dst, copy):
        """move or copy a file

        Args:
            src (string): source image
            dst (string): destination image
            copy (boolean): True to copy, False to move
        """
        try:
            if copy:
                shutil.copy(src, dst)
            else:
                shutil.move(src, dst)
                self.remove_index()
        except Exception as e:
            if copy:
                self.message_box_error('This file cannot be moved', e)
            else:
                self.message_box_error('This file cannot be copied', e)

    def delete(self):
        if not self.index == -1:
            if os.path.isfile(self.images[self.index]):
                reply = QMessageBox.critical(self, 'Delete file', 'Are you sure you want to delete this file ?',
                                             QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    try:
                        if movie := self.image.movie():
                            movie.stop()
                        os.remove(self.images[self.index])
                    except Exception as e:
                        self.message_box_error('Error', 'This file cannot be deleted', e)
                    else:
                        self.remove_index()
            else:
                self.remove_index()

    def rotate_left(self):
        if self.image.pixmap():
            self.image.setPixmap(self.image.pixmap().transformed(QTransform().rotate(270),
                                                                 Qt.SmoothTransformation))
            self.resize_image()

    def rotate_right(self):
        if self.image.pixmap():
            self.image.setPixmap(self.image.pixmap().transformed(QTransform().rotate(90),
                                                                 Qt.SmoothTransformation))
            self.resize_image()

    def flip_horizontal(self):
        if self.image.pixmap():
            self.image.setPixmap(self.image.pixmap().fromImage(self.image.pixmap().toImage().mirrored(True, False)))
            self.resize_image()

    def flip_vertical(self):
        if self.image.pixmap():
            self.image.setPixmap(self.image.pixmap().fromImage(self.image.pixmap().toImage().mirrored()))
            self.resize_image

    def fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.showMaximized()
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.menubar.show()
            self.toolbar.show()
            self.status_bar.show()
            self.dock_widget.show()
            self.display_image()
        elif self.index > -1:
            self.showFullScreen()
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.menubar.hide()
            self.toolbar.hide()
            self.status_bar.hide()
            self.dock_widget.hide()
            screen = self.screen()
            self.scroll_area.resize(screen.availableGeometry().width(),
                                    screen.availableGeometry().height())
            self.display_image()

    def normal_size(self):
        if not self.index == -1:
            self.image.adjustSize()
            self.ratio = 1.0
            self.action_fit_vertical.setChecked(False)
            self.action_fit_horizontal.setChecked(False)
            self.action_fit_screen.setChecked(False)
            self.action_zoom_in.setEnabled(True)
            self.action_zoom_out.setEnabled(True)

    def fit_screen(self):
        if not self.index == -1:
            self.image.adjustSize()
            self.ratio = 1.0
            if self.image.pixmap():
                width = self.image.width()
                height = self.image.height()
            elif movie := self.image.movie():
                movie.jumpToFrame(0)
                width = self.image.width()
                height = self.image.height()

            if self.action_fit_screen.isChecked():
                self.action_fit_horizontal.setChecked(False)
                self.action_fit_vertical.setChecked(False)
                viewport_height = self.scroll_area.viewport().height()
                viewport_width = self.scroll_area.viewport().width()

                if height > viewport_height or width > viewport_width:
                    indice = min(float(viewport_width / width), float(viewport_height / height))
                    self.ratio = 1.0
                    self.scale_image(indice)
            else:
                self.normal_size()
        else:
            self.action_fit_screen.setChecked(False)

    def adjust_scrollbar(self, scroll_bar, ratio):
        """Adjust scroll bar

        Args:
            scroll_bar (ScrollBarPolicy): horizontal or vertical scroll bar
            ratio (float): ratio
        """
        scroll_bar.setValue(int(ratio * scroll_bar.value() + ((ratio - 1) * scroll_bar.pageStep() / 2)))

    def scale_image(self, ratio):
        if not self.index == -1:
            self.ratio *= ratio
            if self.image.pixmap():
                self.image.resize(self.ratio * self.image.pixmap().size())
            elif movie := self.image.movie():
                movie.jumpToFrame(0)
                movie_size = movie.currentPixmap().size()
                self.image.resize(self.ratio * movie_size)

            self.adjust_scrollbar(self.scroll_area.horizontalScrollBar(), ratio)
            self.adjust_scrollbar(self.scroll_area.verticalScrollBar(), ratio)

            self.action_zoom_in.setEnabled(self.ratio < 3.0)
            self.action_zoom_out.setEnabled(self.ratio > 0.333)

            self.image.repaint()

    def zoom_in(self):
        self.scale_image(1.20)

    def zoom_out(self):
        self.scale_image(0.8)

    def fit_height(self):
        if not self.index == -1:
            self.image.adjustSize()
            self.ratio = 1.0
            if self.image.pixmap():
                width = self.image.width()
                height = self.image.height()
            elif movie := self.image.movie():
                movie.jumpToFrame(0)
                width = self.image.width()
                height = self.image.height()

            if self.action_fit_vertical.isChecked():
                self.action_fit_horizontal.setChecked(False)
                self.action_fit_screen.setChecked(False)
                viewport_height = self.scroll_area.viewport().height()
                viewport_width = self.scroll_area.viewport().width()
                ratio = float(viewport_height) / height
                # remove scrollbar height
                if width * ratio > viewport_width and self.isFullScreen() is False:
                    ratio = float(viewport_height - self.scroll_area.horizontalScrollBar().height()) / height
                self.scale_image(ratio)
            else:
                self.normal_size()
        else:
            self.action_fit_vertical.setChecked(False)

    def fit_width(self):
        if not self.index == -1:
            self.image.adjustSize()
            self.ratio = 1.0
            if self.image.pixmap():
                width = self.image.pixmap().width()
                height = self.image.pixmap().height()
            elif movie := self.image.movie():
                movie.jumpToFrame(0)
                width = movie.currentPixmap().width()
                height = movie.currentPixmap().height()

            if self.action_fit_horizontal.isChecked():
                self.action_fit_vertical.setChecked(False)
                self.action_fit_screen.setChecked(False)
                viewport_height = self.scroll_area.viewport().height()
                viewport_width = self.scroll_area.viewport().width()
                ratio = float(viewport_width) / width
                # remove scrollbar width
                if height * ratio > viewport_height and self.isFullScreen() is False:
                    ratio = float(viewport_width - self.scroll_area.verticalScrollBar().width()) / width
                self.scale_image(ratio)
            else:
                self.normal_size()
        else:
            self.action_fit_horizontal.setChecked(False)

    def image_gallery_triggered(self):
        value = self.action_image_gallery.isChecked()
        if self.action_image_gallery.isChecked():
            self.dock_widget.show()
        else:
            self.dock_widget.hide()

        self.settings.setValue('view/image_gallery', value)

    def previous_image(self):
        if self.index > 0:
            self.index -= 1
            self.ratio = 1.0
            self.display_image()

    def next_image(self):
        if self.index < len(self.images) - 1:
            self.index += 1
            self.ratio = 1.0
            self.display_image()

    def first_image(self):
        if not self.index == -1:
            self.index = 0
            self.display_image()

    def last_image(self):
        if not self.index == -1:
            self.index = len(self.images) - 1
            self.display_image()

    def about(self):
        QMessageBox.about(self, "About Baloviewer",
                          """<p align='center'><b>Baloviewer</b></p>
                          <p align='center'>An Image Viewer</p>
                          <p align='center'>Copyright © 2019 Baloby</p>
                          <p align='center'>Licence: GNU General Public License Version 3</p>""")

    def message_box_error(self, title, text, error=None):
        message = QMessageBox(self, title, text)
        message.setIcon(QMessageBox.Warning)
        message.setWindowTitle(title)
        message.setText(text)
        if error is not None:
            message.setDetailedText(str(error))
        message.exec_()

    def image_gallery_clicked(self, item):
        self.index = self.image_gallery.row(item)
        self.display_image()
