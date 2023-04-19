import sys
import threading
import numpy as np
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QAction, QIcon
from ui_mainwindow import Ui_MainWindow

from UI_Controller import UIController
import matplotlib.pyplot as plt
import os

# http://c.biancheng.net/view/1863.html
# Qt QTableWidget 基本操作
# class TEDLayout:
#     def setDefault:


class MainWindow(QMainWindow):

    def __init__(self, agent: UIController):
        self.agent = agent
        self.__result_df = pd.DataFrame()
        self.__timer_count = 0

        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('智慧工廠用戶端')
        # set connect
        agent.change_text.connect(self.on_text_changed)
        agent.change_style.connect(self.on_style_changed)
        agent.show_error_msg.connect(self.show_error_msg)
        agent.clear_result.connect(self.clear_result_info)
        agent.table_updated.connect(self.updated_table)
        self.ui.btn_predict.clicked.connect(self.do_predict)
        self.ui.actionrestart_server.triggered.connect(agent.restart_server)

        # initialized
        # ted temp mark
        # self.agent.updated_table()
        self.clear_result_info()
        self.ui.lbl_predict_status.setText('等待按下測試按鈕')
        threading.Thread(target=self.agent.check_server_start).start()

        # table initialized
        self.ui.tbl_result.setColumnCount(5)
        self.ui.tbl_result.setHorizontalHeaderLabels(['filename', 'result', 'KDE', 'MSE', 'datetime'])

        # set timer
        self.update_table_timer = QTimer()
        self.update_table_timer.timeout.connect(self.on_timer_method)
        # self.update_table_timer.timeout.connect(self.agent.updated_table)
        self.update_table_timer.start(1000)
        # self.server_recording_time = QTimer()
        # self.server_recording_time.timeout.connect(self.agent.check_server_recording)
        # self.server_recording_time.start(3000)

        # TEST(): plot
        self.update_fig()

    def on_timer_method(self):
        if self.__timer_count % 3 == 0:
            threading.Thread(target=self.agent.check_server_recording).start()
        self.agent.updated_table()
        self.__timer_count = (self.__timer_count + 1) % 1000

    def update_fig(self):
        df = pd.read_csv("freq_ana.csv")
        self.ui.ted_widget.axes.clear()
        ax = self.ui.ted_widget.axes
        df.columns = ['freq', 'db']
        ax.semilogx(df.freq, df.db, 'b')
        # ted_added
        if os.path.exists("one_file.csv"):
            df2 = pd.read_csv("ted_max.csv")
            df2.columns = ['freq', 'db']
            ax.semilogx(df2.freq, df2.db, 'r')
        ax.grid(which='major')
        ax.grid(which='minor', linestyle=':')
        ax.set_xlabel(r'Frequency [Hz]')
        ax.set_ylabel('Level [dB]')
        plt.xlim(11, 25000)
        ax.set_xticks([16, 31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000])
        ax.set_xticklabels(['16', '31.5', '63', '125', '250', '500', '1k', '2k', '4k', '8k', '16k'])
        # plt.show()

    @staticmethod
    def show_error_msg(title, text):
        QMessageBox.critical(None, title, text)

    def updated_table(self, df: pd.DataFrame):
        if self.__result_df.shape[0] == df.shape[0]:
            return

        self.__result_df = df
        self.ui.tbl_result.clear()
        self.on_text_changed('predict_status', '等待按下測試按鈕t ')
        row_count, col_count = df.shape
        self.ui.tbl_result.setRowCount(row_count)
        self.ui.tbl_result.setColumnCount(col_count)
        self.ui.tbl_result.setHorizontalHeaderLabels(df.columns)

        for row, row_data in df.iterrows():
            for column, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.ui.tbl_result.setItem(row, column, item)

        self.update_result_info(df.iloc[-1, :])
        self.update_fig()  # ted_added

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
    ui_ctrl = UIController()
    window = MainWindow(ui_ctrl)
    window.show()

    sys.exit(app.exec())
