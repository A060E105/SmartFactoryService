import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon
from ui_mainwindow import Ui_MainWindow


# class TEDLayout:
#     def setDefault:


class TEDClientAgent(QObject):

    statusChanged = Signal(str)

    def __init__(self):
        super().__init__()



    def doCreateCSV(self):
        print("agent create csv")
        self.statusChanged.emit("Creating CSV....")


class MainWindow(QMainWindow):

    def __init__(self, agent: TEDClientAgent):
        self.agent = agent

        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.lbl_server_status.setText("待機中！")
        self.ui.actioncreate_csv.triggered.connect(self.createCSV)
        agent.statusChanged.connect(self.onStatusChanged)

    def createCSV(self):
        print(" csv is pressed!!")
        self.agent.doCreateCSV()

    def onStatusChanged(self, status):
        self.ui.lbl_server_status.setText(status)


    def onMyToolBarButtonClick(self, s):
        print("click", s)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    agent = TEDClientAgent()
    window = MainWindow(agent)
    window.show()

    sys.exit(app.exec())
