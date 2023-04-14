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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.actioncreate_csv = QAction(MainWindow)
        self.actioncreate_csv.setObjectName(u"actioncreate_csv")
        self.actionrestart_server = QAction(MainWindow)
        self.actionrestart_server.setObjectName(u"actionrestart_server")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(30, 320, 256, 192))
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(30, 240, 171, 61))
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(360, 70, 341, 111))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(340, 210, 421, 191))
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

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)
        self.label_4.setScaledContents(False)
        self.label_4.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font)
        self.label_5.setScaledContents(False)
        self.label_5.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_5, 1, 1, 1, 1)

        self.label_6 = QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font)
        self.label_6.setScaledContents(False)
        self.label_6.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)

        self.gridLayoutWidget_2 = QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(340, 420, 421, 91))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.centralwidget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(20, 90, 134, 51))
        self.label_7.setFont(font)
        self.label_7.setScaledContents(False)
        self.label_7.setAlignment(Qt.AlignCenter)
        self.label_8 = QLabel(self.centralwidget)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(20, 160, 134, 51))
        self.label_8.setFont(font)
        self.label_8.setScaledContents(False)
        self.label_8.setAlignment(Qt.AlignCenter)
        self.lbl_server_status = QLabel(self.centralwidget)
        self.lbl_server_status.setObjectName(u"lbl_server_status")
        self.lbl_server_status.setGeometry(QRect(160, 90, 134, 51))
        self.lbl_server_status.setFont(font)
        self.lbl_server_status.setScaledContents(False)
        self.lbl_server_status.setAlignment(Qt.AlignCenter)
        self.label_10 = QLabel(self.centralwidget)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(160, 160, 134, 51))
        self.label_10.setFont(font)
        self.label_10.setScaledContents(False)
        self.label_10.setAlignment(Qt.AlignCenter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))
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
        self.menuOption.addAction(self.actionrestart_server)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actioncreate_csv.setText(QCoreApplication.translate("MainWindow", u"create csv", None))
        self.actionrestart_server.setText(QCoreApplication.translate("MainWindow", u"restart server", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Run Test", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"AI Score2", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"AI Score1", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u5206\u8c9d\u6578\u503c", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"35.3", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"35.3", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"35.3", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Server \u72c0\u614b", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"\u6e2c\u8a66\u72c0\u614b", None))
        self.lbl_server_status.setText(QCoreApplication.translate("MainWindow", u"\u672a\u555f\u52d5", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"\u5f85\u6a5f\u4e2d", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuOption.setTitle(QCoreApplication.translate("MainWindow", u"Option", None))
    # retranslateUi

