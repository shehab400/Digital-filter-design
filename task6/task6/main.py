import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import numpy as np
import pyqtgraph as pg
from Gui import Ui_MainWindow
from scipy.signal import zpk2tf, freqz
import qdarkstyle

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.plotZplane()
        self.zeros = []
        self.poles = []
        self.plottedZeros = []
        self.plottedPoles = []
        self.selected_item = None

        self.ui.actionApply.triggered.connect(self.openApply)
        self.ui.actionAdjust_Phase.triggered.connect(self.openPhaseAdjust)
        self.ui.actionDesign.triggered.connect(self.openDesign)
        self.ui.correctPhase_4.clicked.connect(self.openPhaseAdjust)
        self.ui.zPlaneCircle.scene().sigMouseClicked.connect(self.mouseClickEvent)
        self.ui.clear_4.clicked.connect(self.clear_Zeros_Poles)

    def openPhaseAdjust(self):
         self.ui.stackedWidget.setCurrentIndex(1)
    def openApply(self):
         self.ui.stackedWidget.setCurrentIndex(2)  
    def openDesign(self):
         self.ui.stackedWidget.setCurrentIndex(0)       


    def clear_Zeros_Poles(self):
        if self.ui.comboBox_4.currentIndex()==0:
            for plottedItem in self.plottedZeros:
                self.ui.zPlaneCircle.removeItem(plottedItem)
        elif self.ui.comboBox_4.currentIndex()==1:
            for plottedItem in self.plottedPoles:
                self.ui.zPlaneCircle.removeItem(plottedItem)
        elif self.ui.comboBox_4.currentIndex()==2:
            for plottedItem in self.plottedZeros:
                self.ui.zPlaneCircle.removeItem(plottedItem)
            for plottedItem in self.plottedPoles:
                self.ui.zPlaneCircle.removeItem(plottedItem)
                
    def plotZplane(self):
        theta = np.linspace(0, 2 * np.pi, 100)
        x = np.cos(theta)
        y = np.sin(theta)
        self.ui.zPlaneCircle.setAspectLocked()
        self.ui.zPlaneCircle.plot(x, y, pen=pg.mkPen('b'))
        self.ui.zPlaneCircle.showGrid(True, True)




    def mouseClickEvent(self, event):
        pos = event.pos()
        pos_scene = self.ui.zPlaneCircle.getViewBox().mapSceneToView(pos)
        x = pos_scene.x()
        y = pos_scene.y()

        if event.double():
            if self.ui.radioButton_2.isChecked():
                zero = complex(x, y)
                scatter_item = pg.ScatterPlotItem(x=[x], y=[y], pen=pg.mkPen('g'), symbol='o')
                self.plottedZeros.append(scatter_item)
                self.ui.zPlaneCircle.addItem(scatter_item)
                self.zeros.append(zero)

            elif self.ui.radioButton.isChecked():
                pole = complex(x, y)
                scatter_item = pg.ScatterPlotItem(x=[x], y=[y], pen=pg.mkPen('r'), symbol='x')
                self.plottedPoles.append(scatter_item)
                self.ui.zPlaneCircle.addItem(scatter_item)
                self.poles.append(pole)


            self.update_Mag_Phase_Response()
        


    def update_Mag_Phase_Response(self):
        # Clear previous plots
        self.ui.magPlot.clear()
        self.ui.phasePlot.clear()

        # Check if there are zeros and poles
        if self.zeros or self.poles:
            # Convert zeros, poles, and gain to numerator and denominator coefficients
            num, den = zpk2tf(self.zeros, self.poles, 1)

            # Compute the frequency response
            w, FreqResp = freqz(num, den)

            # Plot the magnitude response
            self.ui.magPlot.plot(w, 20 * np.log10(abs(FreqResp)))

            # Plot the phase response
            self.ui.phasePlot.plot(w, np.angle(FreqResp, deg=True))




                

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
