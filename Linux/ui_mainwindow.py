# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTableWidget,
    QTableWidgetItem, QWidget)

from mplwidget import MplWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1325, 842)
        self.actioncreate_csv = QAction(MainWindow)
        self.actioncreate_csv.setObjectName(u"actioncreate_csv")
        self.actionrestart_server = QAction(MainWindow)
        self.actionrestart_server.setObjectName(u"actionrestart_server")
        self.actionmic_cali = QAction(MainWindow)
        self.actionmic_cali.setObjectName(u"actionmic_cali")
        self.actionclear_all_data = QAction(MainWindow)
        self.actionclear_all_data.setObjectName(u"actionclear_all_data")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tbl_result = QTableWidget(self.centralwidget)
        self.tbl_result.setObjectName(u"tbl_result")
        self.tbl_result.setGeometry(QRect(20, 410, 671, 381))
        self.btn_predict = QPushButton(self.centralwidget)
        self.btn_predict.setObjectName(u"btn_predict")
        self.btn_predict.setGeometry(QRect(30, 240, 171, 61))
        self.btn_predict.setAutoFillBackground(False)
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(670, 10, 591, 381))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.ted_widget = MplWidget(self.horizontalLayoutWidget)
        self.ted_widget.setObjectName(u"ted_widget")

        self.horizontalLayout.addWidget(self.ted_widget)

        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(820, 430, 421, 141))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        font = QFont()
        font.setPointSize(20)
        self.label_3.setFont(font)
        self.label_3.setScaledContents(False)
        self.label_3.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)
        self.label_2.setScaledContents(False)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")
        self.label.setFont(font)
        self.label.setScaledContents(False)
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lbl_dB = QLabel(self.gridLayoutWidget)
        self.lbl_dB.setObjectName(u"lbl_dB")
        self.lbl_dB.setFont(font)
        self.lbl_dB.setScaledContents(False)
        self.lbl_dB.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbl_dB, 1, 0, 1, 1)

        self.lbl_KDE = QLabel(self.gridLayoutWidget)
        self.lbl_KDE.setObjectName(u"lbl_KDE")
        self.lbl_KDE.setFont(font)
        self.lbl_KDE.setScaledContents(False)
        self.lbl_KDE.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbl_KDE, 1, 1, 1, 1)

        self.lbl_MSE = QLabel(self.gridLayoutWidget)
        self.lbl_MSE.setObjectName(u"lbl_MSE")
        self.lbl_MSE.setFont(font)
        self.lbl_MSE.setScaledContents(False)
        self.lbl_MSE.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lbl_MSE, 1, 2, 1, 1)

        self.gridLayoutWidget_3 = QWidget(self.centralwidget)
        self.gridLayoutWidget_3.setObjectName(u"gridLayoutWidget_3")
        self.gridLayoutWidget_3.setGeometry(QRect(30, 50, 531, 181))
        self.gridLayout_3 = QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.lbl_predict_status = QLabel(self.gridLayoutWidget_3)
        self.lbl_predict_status.setObjectName(u"lbl_predict_status")
        self.lbl_predict_status.setFont(font)
        self.lbl_predict_status.setScaledContents(False)
        self.lbl_predict_status.setAlignment(Qt.AlignCenter)

        self.gridLayout_3.addWidget(self.lbl_predict_status, 1, 1, 1, 1)

        self.label_8 = QLabel(self.gridLayoutWidget_3)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font)
        self.label_8.setScaledContents(False)
        self.label_8.setAlignment(Qt.AlignCenter)

        self.gridLayout_3.addWidget(self.label_8, 1, 0, 1, 1)

        self.lbl_server_status = QLabel(self.gridLayoutWidget_3)
        self.lbl_server_status.setObjectName(u"lbl_server_status")
        self.lbl_server_status.setFont(font)
        self.lbl_server_status.setScaledContents(False)
        self.lbl_server_status.setAlignment(Qt.AlignCenter)

        self.gridLayout_3.addWidget(self.lbl_server_status, 0, 1, 1, 1)

        self.label_7 = QLabel(self.gridLayoutWidget_3)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font)
        self.label_7.setScaledContents(False)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.gridLayout_3.addWidget(self.label_7, 0, 0, 1, 1)

        self.horizontalLayoutWidget_2 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(820, 580, 421, 41))
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.horizontalLayoutWidget_2)
        self.label_5.setObjectName(u"label_5")
        font1 = QFont()
        font1.setPointSize(15)
        self.label_5.setFont(font1)
        self.label_5.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label_5)

        self.label_4 = QLabel(self.horizontalLayoutWidget_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)
        self.label_4.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label_4)

        self.horizontalLayoutWidget_3 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_3.setObjectName(u"horizontalLayoutWidget_3")
        self.horizontalLayoutWidget_3.setGeometry(QRect(820, 620, 421, 51))
        self.horizontalLayout_3 = QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.lbl_freq_analysis = QLabel(self.horizontalLayoutWidget_3)
        self.lbl_freq_analysis.setObjectName(u"lbl_freq_analysis")
        self.lbl_freq_analysis.setFont(font1)
        self.lbl_freq_analysis.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.lbl_freq_analysis)

        self.lbl_AI_noise_analysis = QLabel(self.horizontalLayoutWidget_3)
        self.lbl_AI_noise_analysis.setObjectName(u"lbl_AI_noise_analysis")
        self.lbl_AI_noise_analysis.setFont(font1)
        self.lbl_AI_noise_analysis.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.lbl_AI_noise_analysis)

        self.horizontalLayoutWidget_4 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_4.setObjectName(u"horizontalLayoutWidget_4")
        self.horizontalLayoutWidget_4.setGeometry(QRect(820, 690, 421, 91))
        self.horizontalLayout_4 = QHBoxLayout(self.horizontalLayoutWidget_4)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.lbl_final_result = QLabel(self.horizontalLayoutWidget_4)
        self.lbl_final_result.setObjectName(u"lbl_final_result")
        self.lbl_final_result.setFont(font)
        self.lbl_final_result.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.lbl_final_result)

        self.btn_play = QPushButton(self.centralwidget)
        self.btn_play.setObjectName(u"btn_play")
        self.btn_play.setGeometry(QRect(500, 280, 151, 101))
        font2 = QFont()
        font2.setPointSize(35)
        self.btn_play.setFont(font2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1325, 24))
        self.menubar.setMinimumSize(QSize(20, 20))
        self.menubar.setNativeMenuBar(False)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuOption = QMenu(self.menubar)
        self.menuOption.setObjectName(u"menuOption")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOption.menuAction())
        self.menuFile.addAction(self.actioncreate_csv)
        self.menuFile.addAction(self.actionclear_all_data)
        self.menuOption.addAction(self.actionrestart_server)
        self.menuOption.addAction(self.actionmic_cali)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actioncreate_csv.setText(QCoreApplication.translate("MainWindow", u"create csv", None))
        self.actionrestart_server.setText(QCoreApplication.translate("MainWindow", u"restart server", None))
        self.actionmic_cali.setText(QCoreApplication.translate("MainWindow", u"mic calibration", None))
        self.actionclear_all_data.setText(QCoreApplication.translate("MainWindow", u"clear all data", None))
        self.btn_predict.setText(QCoreApplication.translate("MainWindow", u"Run Test", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"AI Score2", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"AI Score1", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u5206\u8c9d\u6578\u503c", None))
        self.lbl_dB.setText(QCoreApplication.translate("MainWindow", u"35.3", None))
        self.lbl_KDE.setText(QCoreApplication.translate("MainWindow", u"35.3", None))
        self.lbl_MSE.setText(QCoreApplication.translate("MainWindow", u"35.3", None))
        self.lbl_predict_status.setText(QCoreApplication.translate("MainWindow", u"\u5f85\u6a5f\u4e2d", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"\u6e2c\u8a66\u72c0\u614b", None))
        self.lbl_server_status.setText(QCoreApplication.translate("MainWindow", u"\u672a\u555f\u52d5", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Server \u72c0\u614b", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u983b\u8b5c\u5206\u6790", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"AI\u7570\u97f3\u5206\u6790", None))
        self.lbl_freq_analysis.setText(QCoreApplication.translate("MainWindow", u"OK", None))
        self.lbl_AI_noise_analysis.setText(QCoreApplication.translate("MainWindow", u"OK", None))
        self.lbl_final_result.setText(QCoreApplication.translate("MainWindow", u"PASS", None))
        self.btn_play.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuOption.setTitle(QCoreApplication.translate("MainWindow", u"Option", None))
    # retranslateUi

