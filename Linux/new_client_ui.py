# import os
# import sys
#
# # Add Homebrew packages to the Python path
# homebrew_prefix = os.popen("brew --prefix").read().strip()
# sys.path.append(homebrew_prefix + "/lib/python3.9/site-packages")
#
#
# from PySide6.QtWidgets import QApplication, QWidget
#
# # Only needed for access to command line arguments
# import sys
#
# # You need one (and only one) QApplication instance per application.
# # Pass in sys.argv to allow command line arguments for your app.
# # If you know you won't use command line arguments QApplication([]) works too.
# app = QApplication(sys.argv)
#
# # Create a Qt widget, which will be our window.
# window = QWidget()
# window.show()  # IMPORTANT!!!!! Windows are hidden by default.
#
# # Start the event loop.
# app.exec_()

# Your application won't reach here until you exit and the event
# loop has stopped.



import sys

from PySide6.QtCore import QSize, Qt
from ui_mainwindow import Ui_MainWindow
from PySide6.QtWidgets import QApplication, QMainWindow
# from PySide6.QtCore import QFile
from ui_mainwindow import Ui_MainWindow


# from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        # super().__init__()

        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #
        # self.setWindowTitle("My App")
        #
        # button = QPushButton("Press Me!")
        #
        # # Set the central widget of the Window.
        # self.setCentralWidget(button)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

# app = QApplication(sys.argv)
#
# window = MainWindow()
# window.show()
#
# app.exec_()
