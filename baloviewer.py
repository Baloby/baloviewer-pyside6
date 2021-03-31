import sys
from optparse import OptionParser
from single_application import SingleApplication
from window import Window
from PySide6.QtCore import QCoreApplication

if __name__ == '__main__':
    QCoreApplication.setApplicationName('Balob')
    QCoreApplication.setApplicationName('Balobviewer')

    appGuid = 'baloviwer-server-125156dsfdsf'
    app = SingleApplication(appGuid, sys.argv)
    if app.get_is_running():
        parser = OptionParser()
        parser.add_option("-f", "--file", dest="filename", help="open a file")
        (options, args) = parser.parse_args()
        parser_file = options.filename
        if parser_file is not None:
            app.send_message(parser_file)
        sys.exit(0)

    window = Window()
    window.showMaximized()
    app.set_activation_window(window)
    sys.exit(app.exec_())

    # app = QApplication(sys.argv)
    # main = Window()
    # main.showMaximized()
    # app.exec_()
