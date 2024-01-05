from PyQt5 import QtWidgets, uic, QtCore,QtGui,QtMultimedia
from PyQt5.QtCore import QThread,QObject,pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QPushButton,QGraphicsScene,QWidget,QErrorMessage,QMessageBox,QDialog,QScrollBar,QSlider,QLabel
import sys
import random
import pandas as pd
import time
import numpy as np
from scipy.interpolate import interp1d
from scipy import signal
# class Worker(QObject):
#     progress = Signal(int)
#     completed = Signal(int)
#     end = False
#     @Slot(int)
#     def do_work(self, n):
#         global i
#         for i in np.arange(1,n+1,0.1):
#             if self.end == True:
#                 break
#             time.sleep(0.1)
#             self.progress.emit(i)
#         self.completed.emit(i)

PlotLine1 = []
class Signal:
    def __init__(self):
        self.time_values = []
        self.y_values = []

    def add_point(self, y):
        self.y_values.append(y)

class PlotLine:
    def __init__(self):
        self.data = None
        self.dataX = None
        self.dataY = None


class MyWindow(QMainWindow):
    # work_requested = Signal(int)
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = uic.loadUi("FixingGUI2.ui", self)

        self.ui.uniformWave.clicked.connect(self.filterDesign)
        self.ui.music.clicked.connect(self.allpassFilter)
        self.ui.animals.clicked.connect(self.output)
        self.ui.uniformWave2.clicked.connect(self.filterDesign)
        self.ui.music2.clicked.connect(self.allpassFilter)
        self.ui.animals2.clicked.connect(self.output)
        self.ui.pushButton_8.clicked.connect(self.load)
        self.ui.pushButton_7.clicked.connect(self.update_plot_Allpass)
        self.ui.pushButton_5.clicked.connect(self.add_value_to_combo)
        ## Change Qpushbutton Checkable status when stackedWidget index changed
        self.ui.radioButton_3.setChecked(True)
        # self.worker = Worker()
        self.central_widget = QWidget(self)
        self.scene = QGraphicsScene(self)
        self.touchPad.setScene(self.scene)
        # self.worker.progress.connect(self.UpdatePlots)
        # self.work_requested.connect(self.worker.do_work)
        

        self.plotWidget1 = pg.PlotWidget()
        self.plotWidget2 = pg.PlotWidget()
        self.plotWidget3 = pg.PlotWidget()
        self.plotWidget4 = pg.PlotWidget()
        self.plotWidget5 = pg.PlotWidget()
        self.plotWidget6 = pg.PlotWidget()
        self.plotWidget7 = pg.PlotWidget()
        self.plotWidget8 = pg.PlotWidget()

        layout1=QVBoxLayout()
        layout1.addWidget(self.plotWidget1 )
        self.ui.widget_11.setLayout(layout1)
        layout2=QVBoxLayout()
        layout2.addWidget(self.plotWidget2)
        self.ui.widget_9.setLayout(layout2)
        layout3=QVBoxLayout()
        layout3.addWidget(self.plotWidget3)
        self.ui.widget_10.setLayout(layout3)
        layout4=QVBoxLayout()
        layout4.addWidget(self.plotWidget4 )
        self.ui.widget_12.setLayout(layout4)
        layout5=QVBoxLayout()
        layout5.addWidget(self.plotWidget5 )
        self.ui.widget_16.setLayout(layout5)
        layout6=QVBoxLayout()
        layout6.addWidget(self.plotWidget6 )
        self.ui.widget_14.setLayout(layout6)
        layout7=QVBoxLayout()
        layout7.addWidget(self.plotWidget7 )
        self.ui.widget_18.setLayout(layout7)
        layout8=QVBoxLayout()
        layout8.addWidget(self.plotWidget8 )
        self.ui.widget_21.setLayout(layout8)

        self.plotWidget4.setAspectLocked(True)
        # Signal object
        self.signal = Signal()

        # Connect mouse events
        self.ui.touchPad.mouseMoveEvent = self.mouse_move_event
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)
        default_values = ["1-2j", "0.5+0.5j", "0.7071+0.7071j"]
        self.ui.comboBox_3.addItems(default_values)

    def stackedWidget_currentChanged (self, index):
        btn_list = self.ui.icon_only.findChild(QPushButton) \
        + self.ui.full_menu.findChild(QPushButton)

        for btn in btn_list:
            if index in [5,6]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True)

    def filterDesign(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.stackedWidget_2.setCurrentIndex(0)

    def allpassFilter(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.stackedWidget_2.setCurrentIndex(1)

    def output(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.stackedWidget_2.setCurrentIndex(2)

    def mouse_move_event(self, event):
        if self.radioButton_4.isChecked():
            y = event.pos().y()

            # Add the y-coordinate to the Signal object
            self.signal.add_point(y)


    def ErrorMsg(self, text):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning)
        x = msg.exec_()

    def random_color(self):
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)

        return (red, green, blue)

    def load(self):
        if self.ui.radioButton_3.isChecked() == True:
            filename = QtWidgets.QFileDialog.getOpenFileName()
            path = filename[0]

            if path.endswith(".txt"):
                    with open(path, "r") as data:
                        x = []
                        y = []
                        for line in data:
                            p = line.split()
                            x.append(float(p[0]))
                            y.append(float(p[1]))
                    newplot = PlotLine()
                    newplot.data = pd.DataFrame({"time": x, "amplitude": y})
                    PlotLine1.append(newplot)
                    self.plotWidget7.clear()
                    pen = pg.mkPen(color=self.random_color())
                    name = "Signal 1"
                    self.plotWidget7.plot(newplot.data["time"],newplot.data["amplitude"],pen = pen)
                    self.plotWidget7.setLimits(xMin = 0 ,xMax = newplot.data["time"].max())
                    # self.plotWidget7.setXRange(0,0.1,padding=0)
                    self.timer2 = QtCore.QTimer()
                    self.timer2.setInterval(int(50))
                    self.timer2.timeout.connect(
                        self.UpdatePlots
                    )  # Connect to a single update method
                    self.timer2.start()
                    
            elif path.endswith(".csv"):
                    newplot = PlotLine()
                    newplot.data = pd.read_csv(path, usecols=["time", "amplitude"])
                    PlotLine1.append(newplot)
                    name = "Signal 1"
                    self.plotWidget7.clear()
                    pen = pg.mkPen(color=self.random_color())
                    self.plotWidget7.plot(newplot.data["time"],newplot.data["amplitude"],pen=pen)
                    self.plotWidget7.setXRange(0,10,padding=0)
                    # self.plotWidget7.setLimits(xMin = 0 ,xMax = newplot.data["time"].max())
                    self.timer2 = QtCore.QTimer()
                    self.timer2.setInterval(int(50))
                    self.timer2.timeout.connect(
                        self.UpdatePlots
                    )  # Connect to a single update method
                    self.timer2.start()
        else:
            self.ErrorMsg("Load Signal is NOT checked")

    def UpdatePlots(self):

        xmin=self.plotWidget7.getViewBox().viewRange()[0][0]
        xmax=self.plotWidget7.getViewBox().viewRange()[0][1]
        if xmax <= PlotLine1[-1].data["time"].max():
            self.plotWidget7.setXRange(xmin+10,xmax+10,padding=0)
        else:
             self.timer.stop()

        self.plotWidget7.setLimits(xMin = 0 ,xMax = PlotLine1[-1].data["time"].max())

    def plot_signal(self, y_values):
        self.plotWidget7.clear()

        # Use interpolation for a smoother curve
        x_values = np.arange(len(y_values))
        interp_func = interp1d(x_values, y_values, kind='cubic')
        x_interp = np.linspace(0, len(y_values) - 1, 1000)
        y_interp = interp_func(x_interp)

        self.plotWidget7.plot(x_interp, y_interp, linestyle='-', color='b')
        self.plotWidget7.set_xlabel('Time')
        self.plotWidget7.set_ylabel('Y-coordinate')
        self.draw()

    def update_plot(self):
        if self.radioButton_4.isChecked():
            # Plot the signal with interpolation for smoother curve
            if len(self.signal.y_values) >= 2:
                self.plotWidget7.plot(self.signal.y_values)
                self.filteredGraph()


    def update_plot_Allpass(self):
        selected_text = self.ui.comboBox_3.currentText()
    
        if self.ui.lineEdit.text():
            a = complex(self.ui.lineEdit.text())
        else:
            #
            a = complex(selected_text)
        self.represent_allpass(a)
       

    def filteredGraph(self):
        if self.ui.radioButton_3.isChecked():
            YData = PlotLine1[-1].data["amplitude"]
            filteredgraph = signal.lfilter(YData)
        elif self.ui.radioButton_4.isChecked():
            filteredgraph = signal.lfilter(self.signal.y_values)
            #plot


    def represent_allpass(self, a):
        # Get zero and pole of all-pass
        z, p, k = signal.tf2zpk([-a, 1.0], [1.0, -a])

        self.ui.plotWidget5.clear()
        self.ui.plotWidget4.clear()

        unit_circle_item = pg.PlotDataItem()
        theta = np.linspace(0, 2 * np.pi, 100)
        x = np.cos(theta)
        y = np.sin(theta)
        unit_circle_item.setData(x=x, y=y, pen=pg.mkPen('g'))
        self.ui.plotWidget4.addItem(unit_circle_item)
        self.add_zerosPoles_fromallpass(z,p)

        for zero in z:
            self.ui.plotWidget4.plot([np.real(zero)], [np.imag(zero)], pen=None, symbol='o', symbolBrush='r') #######

        for pole in p:
            self.ui.plotWidget4.plot([np.real(pole)], [np.imag(pole)], pen=None, symbol='x', symbolBrush='b')

        self.ui.plotWidget4.setTitle('Zeros and Poles on Unit Circle')
        self.ui.plotWidget4.showGrid(x=True, y=True)
        w, h = signal.freqz([-a, 1.0], [1.0, -a])
        self.plot_Phase_allpass(w,h,1)
    def plot_Phase_allpass(self,w,h,key):
        # Plot phase response
        phase_response = np.unwrap(np.angle(h))
        if key==1:
            self.ui.plotWidget5.plot(w, phase_response, pen=pg.mkPen('b'))
            self.ui.plotWidget5.setTitle('Phase Response')
            self.ui.plotWidget5.setLabel('bottom', 'Frequency [Hz]')
            self.ui.plotWidget5.setLabel('left', 'Phase [radians]')
            self.ui.plotWidget5.showGrid(x=True, y=True)
        else:
            
            self.ui.plotWidget6.plot(w, phase_response, pen=pg.mkPen('b'))
            self.ui.plotWidget6.setTitle('Phase Response')
            self.ui.plotWidget6.setLabel('bottom', 'Frequency [Hz]')
            self.ui.plotWidget6.setLabel('left', 'Phase [radians]')
            self.ui.plotWidget6.showGrid(x=True, y=True)
    def add_value_to_combo(self):
      
        new_value = self.ui.lineEdit.text()
        if new_value:
            if new_value not in [self.ui.comboBox_3.itemText(i) for i in range(self.ui.comboBox_3.count())]:
                self.ui.comboBox_3.addItem(new_value)

    def add_zerosPoles_fromallpass(self,z,p):
        #this function should take zeros and poles of all pass filter and add them to created filter
        #also we should call plot_phase_allpass function to plot corrected phase with key !=1
        pass