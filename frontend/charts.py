import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

class LiveChart:
    def __init__(self, title, max_points=100):
        self.plot_widget = pg.PlotWidget(title=title)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setYRange(0, 100)
        self.curve = self.plot_widget.plot(pen='y')
        self.data = []
        self.max_points = max_points

    def update(self, value):
        self.data.append(value)
        if len(self.data) > self.max_points:
            self.data.pop(0)
        self.curve.setData(self.data)

    def get_widget(self):
        return self.plot_widget
