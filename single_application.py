from PySide6.QtCore import Signal, QTextStream, Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QLocalSocket, QLocalServer


class SingleApplication(QApplication):

    message_received = Signal(str)

    def __init__(self, id, *argv):

        super(SingleApplication, self).__init__(*argv)
        self.id = id
        self.activation_window = None
        self.activate_on_message = False

        # Is there another instance running?
        self.out_socket = QLocalSocket()
        self.out_socket.connectToServer(self.id)
        self.is_running = self.out_socket.waitForConnected()

        if self.is_running:
            self.out_stream = QTextStream(self.out_socket)
        else:
            # No, there isn't.
            self.out_socket = None
            self.out_stream = None
            self.in_socket = None
            self.in_stream = None
            self.server = QLocalServer()
            self.server.listen(self.id)
            self.server.newConnection.connect(self.on_new_connection)

    def get_is_running(self):
        return self.is_running

    def id(self):
        return self.id

    def activation_window(self):
        return self.activation_window

    def set_activation_window(self, activation_window, activate_on_message=True):
        self.activation_window = activation_window
        self.activate_on_message = activate_on_message
        self.message_received.connect(self.activation_window.on_message_received)

    def activate_Window(self):

        if not self.activation_window:
            return

        self.activation_window.setWindowState((self.activation_window.windowState()
                                              & ~Qt.WindowMinimized) | Qt.WindowActive)

        self.activation_window.activateWindow()

    def send_message(self, msg):
        if not self.out_stream:
            return False
        self.out_stream << msg << '\n'
        self.out_stream.flush()
        return self.out_socket.waitForBytesWritten()

    def on_new_connection(self):
        if self.in_socket:
            self.in_socket.readyRead.disconnect(self.on_ready_read)
        self.in_socket = self.server.nextPendingConnection()
        if not self.in_socket:
            return
        self.in_stream = QTextStream(self.in_socket)
        self.in_socket.readyRead.connect(self.on_ready_read)
        if self.activate_on_message:
            self.activate_Window()

    def on_ready_read(self):
        while True:
            msg = self.in_stream.readLine()
            if not msg:
                break
            
            self.message_received.emit(msg)
