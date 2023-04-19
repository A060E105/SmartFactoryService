# class MplCanvas(FigureCanvasQTAgg):
#
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#         super(MplCanvas, self).__init__(fig)

from PySide6.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# class MplWidget(QWidget):
#
#     def __init(self, parent=None):
#         QWidget.__init__(self, parent)
#         self.canvas = FigureCanvas(Figure())
#         vertical_layout = QVBoxLayout()
#         vertical_layout.addWidget(self.canvas)
#         self.canvas.axes = self.canvas.figure.add_subplot(111)
#         self.setLayout(vertical_layout)

class MplWidget(FigureCanvasQTAgg):

    # def __init__(self, parent=None, width=5, height=4, dpi=100):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        super(MplWidget, self).__init__(fig)

# class MplWidget(F)



