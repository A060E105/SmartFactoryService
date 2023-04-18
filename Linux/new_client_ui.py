import sys
import threading
import numpy as np
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon
from ui_mainwindow import Ui_MainWindow

from UI_Controller import UIController

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

    def __init__(self, agent: UIController):
        self.agent = agent
        self.__result_df = pd.DataFrame()

        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        agent.change_text.connect(self.on_text_changed)
        agent.change_style.connect(self.on_style_changed)
        agent.clear_result.connect(self.clear_result_info)
        agent.table_updated.connect(self.updated_table)
        self.ui.btn_predict.clicked.connect(self.do_predict)
        self.ui.actionrestart_server.triggered.connect(agent.restart_server)

        # initialized
        self.ui.lbl_predict_status.setText('等待按下測試按鈕')
        threading.Thread(target=self.agent.check_server_start).start()
        # table initialized
        self.clear_result_info()
        self.ui.tbl_result.setColumnCount(5)
        self.ui.tbl_result.setHorizontalHeaderLabels(['filename', 'result', 'KDE', 'MSE', 'datetime'])

        # QMessageBox.critical(None, 'Error', 'error')

    def updated_table(self, df: pd.DataFrame):
        self.__result_df = df
        self.ui.tbl_result.clear()
        row_count, col_count = df.shape
        self.ui.tbl_result.setRowCount(row_count)
        self.ui.tbl_result.setColumnCount(col_count)
        self.ui.tbl_result.setHorizontalHeaderLabels(df.columns)

        for row, row_data in df.iterrows():
            for column, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.ui.tbl_result.setItem(row, column, item)

        self.update_result_info(df.iloc[-1, :])

    def update_result_info(self, data: pd.Series):
        self.on_text_changed('dB', str(np.round(data['decibel'], 1)))
        self.on_text_changed('KDE', str(np.round(data['ai_score1'], 1)))
        self.on_text_changed('MSE', str(np.round(data['ai_score2'], 1)))
        for item_name in ['freq_result', 'ai_result', 'final_result']:
            color = 'green' if data[item_name] in ['OK', 'PASS'] else 'red'
            style = f"background: {color}"
            self.on_text_changed(item_name, data[item_name])
            self.on_style_changed(item_name, style)

    def clear_result_info(self):
        for item_name in ['dB', 'KDE', 'MSE']:
            self.on_text_changed(item_name, '')
        for item_name in ['freq_result', 'ai_result', 'final_result']:
            style = "background: transparent"
            self.on_text_changed(item_name, '')
            self.on_style_changed(item_name, style)

    def do_predict(self):
        threading.Thread(target=self.agent.start_analysis).start()

    def on_text_changed(self, label_name: str, text: str) -> None:
        mapping = {'server_status': self.ui.lbl_server_status,
                   'predict_status': self.ui.lbl_predict_status,
                   'dB': self.ui.lbl_dB,
                   'KDE': self.ui.lbl_KDE,
                   'MSE': self.ui.lbl_MSE,
                   'freq_result': self.ui.lbl_freq_analysis,
                   'ai_result': self.ui.lbl_AI_noise_analysis,
                   'final_result': self.ui.lbl_final_result,
                   }

        if mapping.__contains__(label_name):
            mapping.get(label_name).setText(text)
            print(label_name, '=', text)

    def on_style_changed(self, label_name: str, style: str) -> None:
        mapping = {'server_status': self.ui.lbl_server_status,
                   'freq_result': self.ui.lbl_freq_analysis,
                   'ai_result': self.ui.lbl_AI_noise_analysis,
                   'final_result': self.ui.lbl_final_result,
                   }
        if mapping.__contains__(label_name):
            mapping.get(label_name).setStyleSheet(style)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # agent = TEDClientAgent()
    # window = MainWindow(agent)
    ui_ctrl = UIController()
    window = MainWindow(ui_ctrl)
    window.show()

    sys.exit(app.exec())
