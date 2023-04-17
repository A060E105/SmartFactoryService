import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon
from ui_mainwindow import Ui_MainWindow

# http://c.biancheng.net/view/1863.html
# Qt QTableWidget 基本操作
# class TEDLayout:
#     def setDefault:


class TEDClientAgent(QObject):

    statusTxtChanged = Signal(str, str)
    statusColorChanged = Signal(str, str)

    def __init__(self):
        super().__init__()

    def doCreateCSV(self):
        print("agent create csv")
        self.statusTxtChanged.emit("server_status", 'Hello World!!!')
        self.statusTxtChanged.emit("dB", '30.5')
        self.statusTxtChanged.emit("KDE", '40.5')
        self.statusTxtChanged.emit("MSE", '50.5')

    def run(self):
        print('press run.')


class MainWindow(QMainWindow):

    def __init__(self, agent: TEDClientAgent):
        self.agent = agent

        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.lbl_server_status.setText("待機中！")
        self.ui.actioncreate_csv.triggered.connect(self.agent.doCreateCSV)
        # self.ui.actioncreate_csv.triggered.connect(self.createCSV)
        agent.statusTxtChanged.connect(self.onStatusChanged)

        self.ui.btn_predict.clicked.connect(self.do_predict)

    def do_predict(self):

        print('you pushed Btn!!')

    def test(self):
        self.agent.run()

    def createCSV(self):
        print(" csv is pressed!!")
        self.agent.doCreateCSV()

    def onStatusChanged(self, label_name, text):
        mapping = {'server_status': self.ui.lbl_server_status,
                   'predict_status': self.ui.lbl_predict_status,
                   'dB': self.ui.lbl_dB,
                   'KDE': self.ui.lbl_KDE,
                   'MSE': self.ui.lbl_MSE,
                   # 'result': self.ui.label_6,
                   }

        mapping.get(label_name).setText(text)
        print(label_name, '=', text)

    def onMyToolBarButtonClick(self, s):
        print("click", s)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    agent = TEDClientAgent()
    window = MainWindow(agent)
    window.show()

    sys.exit(app.exec())
