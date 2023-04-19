# test
# from PySide6 import QtWidgets

from PySide6.QtWidgets import QWidget, QVBoxLayout
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from matplotlib.backends.backend_qt5agg import FigureCanvasQT

# import matplotlib
#

class MplWidget(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        super(MplWidget, self).__init__(fig)
#

# # Matplotlib canvas class to create figure
# class MplCanvas(Canvas):
#     def __init__(self):
#         self.fig = Figure()
#         self.ax = self.fig.add_subplot(111)
#         Canvas.__init__(self, self.fig)
#         # Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
#         Canvas.updateGeometry(self)
#
# # Matplotlib widget
# class MplWidget(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
#         self.canvas = MplCanvas()                  # Create canvas object
#         self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
#         self.vbl.addWidget(self.canvas)
#         self.setLayout(self.vbl)


# class MplWidget(QWidget):
#     pass
#     def __init__(self, parent=None):
#         QWidget.__init__(self, parent)
#         self.canvas = FigureCanvasQTAgg(Figure())
#         vertical_layout = QVBoxLayout()
#         vertical_layout.addWidget(self.canvas)
#         self.canvas.axes = self.canvas.figure.add_subplot(111)
#         self.setLayout(vertical_layout)
#         # fig = Figure()
#         # self.axes = fig.add_subplot(111)
