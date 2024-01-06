import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import numpy as np
import pyqtgraph as pg
from Gui import Ui_MainWindow
from scipy.signal import TransferFunction
import qdarkstyle
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

LinePloting = []
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


class MainWindow(QMainWindow):
    # work_requested = Signal(int)
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.plotZplane()
        self.ui.zPlaneCircle.scene().sigMouseClicked.connect(self.mouseClickEvent)
        self.zeros = []
        self.poles = []
        self.selected_item = None
        self.ui.actionApply.triggered.connect(self.openApply)
        self.ui.actionAdjust_Phase.triggered.connect(self.openPhaseAdjust)
        self.ui.actionDesign.triggered.connect(self.openDesign)
        self.ui.correctPhase_4.clicked.connect(self.openPhaseAdjust)
        self.ui.actionOpen.triggered.connect(self.load)
        self.ui.Apply.clicked.connect(self.update_plot_Allpass) 
        self.ui.AddFilter.clicked.connect(self.addtocombo)
        ## Change Qpushbutton Checkable status when stackedWidget index changed
        # self.worker = Worker()
        self.scene = QGraphicsScene(self)
        self.ui.Touchpad.setScene(self.scene)
        # self.worker.progress.connect(self.UpdatePlots)
        # self.work_requested.connect(self.worker.do_work)
        self.ui.AllpassZplane.setAspectLocked(True)
        # Signal object
        self.signal = Signal()
        self.speed = 1  # Default speed (1 point per second)
        # Connect mouse events
        self.ui.Touchpad.mouseMoveEvent = self.MouseMoving
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)
        default_values = ["2-8j", "3.5+1.5j", "0.7071+0.7071j"]
        self.ui.comboBox.addItems(default_values)
        self.ui.horizontalSlider.setMinimum(1)
        self.ui.horizontalSlider.setMaximum(1000)
        self.ui.horizontalSlider.setValue(500)
        self.ui.horizontalSlider.valueChanged.connect(self.update_speed)
        # Start real-time filtering process automatically
       # self.start_real_time_filtering()
        #self.timer =QTimer()
        #self.timer.timeout.connect(self.update_real_time_filtering)

    def openPhaseAdjust(self):
         self.ui.stackedWidget.setCurrentIndex(1)
    def openApply(self):
         self.ui.stackedWidget.setCurrentIndex(2)  
    def openDesign(self):
         self.ui.stackedWidget.setCurrentIndex(0)       
    def plotZplane(self):
        theta = np.linspace(0, 2 * np.pi, 100)
        x = np.cos(theta)
        y = np.sin(theta)
        self.ui.zPlaneCircle.setAspectLocked()
        self.ui.zPlaneCircle.plot(x, y, pen=pg.mkPen('b'))
        self.ui.zPlaneCircle.showGrid(True, True)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            # Check if there is a selected item
            if self.selected_item:
                # Remove the selected item from the plot
                self.ui.zPlaneCircle.removeItem(self.selected_item)

                # Remove the corresponding tuple from the zeros or poles list
                if self.selected_item in self.zeros:
                    self.zeros.remove(self.selected_item)
                elif self.selected_item in self.poles:
                    self.poles.remove(self.selected_item)

                # Set selected_item to None after removal
                self.selected_item = None

    def mouseClickEvent(self, event):
        pos = event.pos()
        pos_scene = self.ui.zPlaneCircle.getViewBox().mapSceneToView(pos)

        if event.double():
                    if self.ui.radioButton_2.isChecked():
                        # Zeros
                        zero = pg.ScatterPlotItem(x=[pos_scene.x()], y=[pos_scene.y()], pen=pg.mkPen('g'), symbol='o')
                        self.ui.zPlaneCircle.addItem(zero)
                        self.zeros.append(zero)
                        self.selected_item = zero  # Set the selected item to the newly added zero

                    elif self.ui.radioButton.isChecked():
                        # Poles
                        pole = pg.ScatterPlotItem(x=[pos_scene.x()], y=[pos_scene.y()], pen=pg.mkPen('r'), symbol='x')
                        self.ui.zPlaneCircle.addItem(pole)
                        self.poles.append(pole)
                        self.selected_item = pole  # Set the selected item to the newly added pole



    def MouseMoving(self, event):
         if self.ui.Touchpadcheckbox.isChecked():
            y = event.pos().y()

            # Add the y-coordinate to the Signal object
            self.signal.add_point(y)

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()
    def generate_random_color(self):
        while True:
            # Generate random RGB values
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)

            # Calculate brightness using a common formula
            brightness = (red * 299 + green * 587 + blue * 114) / 1000

            # Check if the color is not too light (adjust the threshold as needed)
            if brightness > 100:
                return red, green, blue

    def load(self):
        if self.ui.Touchpadcheckbox.isChecked() == False:
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
                    LinePloting.append(newplot)
                    self.ui.InputSignal.clear()
                    pen = pg.mkPen(color=self.generate_random_color())
                    name = "Signal 1"
                    self.ui.InputSignal.plot(newplot.data["time"],newplot.data["amplitude"],pen = pen)
                    self.ui.InputSignal.setLimits(xMin = 0 ,xMax = newplot.data["time"].max())
                    self.ui.InputSignal.setXRange(0,0.1,padding=0)
                    self.timer2 = QtCore.QTimer()
                    self.timer2.setInterval(int(50))
                    self.timer2.timeout.connect(
                        self.UpdatePlots
                    )  # Connect to a single update method
                    self.timer2.start()
                    
            elif path.endswith(".csv"):
                    newplot = PlotLine()
                    newplot.data = pd.read_csv(path, usecols=["time", "amplitude"])
                    LinePloting.append(newplot)
                    name = "Signal 1"
                    self.ui.InputSignal.clear()
                    pen = pg.mkPen(color=self.generate_random_color())
                    self.ui.InputSignal.plot(newplot.data["time"],newplot.data["amplitude"],pen=pen)
                    self.ui.InputSignal.setXRange(0,10,padding=0)
                    # self.ui.InputSignal.setLimits(xMin = 0 ,xMax = newplot.data["time"].max())
                    self.timer2 = QtCore.QTimer()
                    self.timer2.setInterval(int(50))
                    self.timer2.timeout.connect(
                        self.UpdatePlots
                    )  # Connect to a single update method
                    self.timer2.start()
        else:
            self.ErrorMsg("Check the Check box")

    def UpdatePlots(self):

        xmin=self.ui.InputSignal.getViewBox().viewRange()[0][0]
        xmax=self.ui.InputSignal.getViewBox().viewRange()[0][1]
        if xmax <= LinePloting[-1].data["time"].max():
            self.ui.InputSignal.setXRange(xmin+10,xmax+10,padding=0)
        else:
             self.timer.stop()

        self.ui.InputSignal.setLimits(xMin = 0 ,xMax = LinePloting[-1].data["time"].max())

    def plot_signal(self, y_values):
        self.ui.InputSignal.clear()

        # Use interpolation for a smoother curve
        x_values = np.arange(len(y_values))
        interp_func = interp1d(x_values, y_values, kind='cubic')
        x_interp = np.linspace(0, len(y_values) - 1, 1000)
        y_interp = interp_func(x_interp)

        self.ui.InputSignal.plot(x_interp, y_interp, linestyle='-', color='b')
        self.ui.InputSignal.set_xlabel('Time')
        self.ui.InputSignal.set_ylabel('Y-coordinate')
        self.draw()

    def update_plot(self):
        if self.ui.Touchpadcheckbox.isChecked():
            # Plot the signal with interpolation for smoother curve
            if len(self.signal.y_values) >= 2:
                self.ui.InputSignal.plot(self.signal.y_values)
                self.filteredGraph()


    def update_plot_Allpass(self):
        selected_text = self.ui.comboBox.currentText()
    
        if self.ui.InsertFilterText.text():
            a = complex(self.ui.InsertFilterText.text())
        else:
           
            a = complex(selected_text)
        self.represent_allpass(a)
       

    def filteredGraph(self):
        self.ui.InputSignal.clear()

        if self.ui.Touchpadcheckbox.isChecked():
            y_values = np.array(self.signal.y_values)
            if len(y_values) >= 2:
                # Filter the entire signal
                filtered_values = signal.lfilter([1.0], [1.0], y_values)
                # Plot the original and filtered signals
                self.ui.InputSignal.plot(y_values, pen=pg.mkPen('b'), name='Original Signal')
                self.ui.OutputFilteredSignal.plot(filtered_values, pen=pg.mkPen('r'), name='Filtered Signal')
        else:
            YData = LinePloting[-1].data["amplitude"]
            # Filter the entire signal
            filteredgraph = signal.lfilter(YData, [1.0], YData)
            # Plot the original and filtered signals
            self.ui.InputSignal.plot(YData, pen=pg.mkPen('b'), name='Original Signal')
            self.ui.OutputFilteredSignal.plot(filteredgraph, pen=pg.mkPen('r'), name='Filtered Signal')

        # Add a legend to the plot
        if not hasattr(self, 'legend'):
            self.legend = self.ui.InputSignal.addLegend()



    def represent_allpass(self, a):
        # Get zero and pole of all-pass
        z, p, k = signal.tf2zpk([-a, 1.0], [1.0, -a])

        self.ui.AllPassPhasePlot.clear()
        self.ui.AllpassZplane.clear()

        unit_circle_item = pg.PlotDataItem()
        theta = np.linspace(0, 2 * np.pi, 100)
        x = np.cos(theta)
        y = np.sin(theta)
        unit_circle_item.setData(x=x, y=y, pen=pg.mkPen('r'))
        self.ui.AllpassZplane.addItem(unit_circle_item)
        self.add_zeros_poles_from_allpass(z,p)

        for zero in z:
            self.ui.AllpassZplane.plot([np.real(zero)], [np.imag(zero)], pen=None, symbol='o', symbolBrush='r') #######

        for pole in p:
            self.ui.AllpassZplane.plot([np.real(pole)], [np.imag(pole)], pen=None, symbol='x', symbolBrush='b')

        self.ui.AllpassZplane.setTitle('Zeros and Poles on Unit Circle')
        self.ui.AllpassZplane.showGrid(x=True, y=True)
        w, h = signal.freqz([-a, 1.0], [1.0, -a])
        self.plot_Phase_allpass(w,h,1)
        
    def plot_Phase_allpass(self,w,h,key):
        # Plot phase response
        phase_response = np.unwrap(np.angle(h))
        if key==1:
            self.ui.AllPassPhasePlot.plot(w, phase_response, pen=pg.mkPen('b'))
            self.ui.AllPassPhasePlot.setTitle('Phase Response')
            self.ui.AllPassPhasePlot.setLabel('bottom', 'Frequency [Hz]')
            self.ui.AllPassPhasePlot.setLabel('left', 'Phase [radians]')
            self.ui.AllPassPhasePlot.showGrid(x=True, y=True)
        else:
            
            self.ui.AllPassPhasePlot.plot(w, phase_response, pen=pg.mkPen('b'))
            self.ui.AllPassPhasePlot.setTitle('Phase Response')
            self.ui.AllPassPhasePlot.setLabel('bottom', 'Frequency [Hz]')
            self.ui.AllPassPhasePlot.setLabel('left', 'Phase [radians]')
            self.ui.AllPassPhasePlot.showGrid(x=True, y=True)

    def addtocombo(self):
      
        new_value = self.ui.InsertFilterText.text()
        if new_value:
            if new_value not in [self.ui.comboBox.itemText(i) for i in range(self.ui.comboBox.count())]:
                self.ui.comboBox.addItem(new_value)

    def add_zeros_poles_from_allpass(self, z, p):
        #this function should take zeros and poles of all pass filter and add them to created filter
        #also we should call plot_phase_allpass function to plot corrected phase with key !=1
        pass
    def update_speed(self, value):
        self.speed = value
        if self.timer.isActive():
            self.timer.setInterval(int(1000 / self.speed))


        
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
