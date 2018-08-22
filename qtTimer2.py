import sys

import RPi.GPIO as GPIO
import smbus
import time
from PyQt5 import Qt
from PyQt5.QtCore import QTimer ,QTime
from PyQt5.uic import loadUi

i2c = smbus.SMBus(1)
TICK_TIME = 20

class StopWatch(Qt.QMainWindow):
    def __init__(self,parent = None):
        super(StopWatch,self).__init__()
        self.ui = loadUi("gui.ui",self)
        self.reset.clicked.connect(self.do_reset)
        self.start.clicked.connect(self.do_start)

        self.driving=False
        self.count=0
        self.afterSence=False
        self.afterSenceCount=0
        self.timer=Qt.QTimer()
        self.timer.setInterval(TICK_TIME)
        self.timer.timeout.connect(self.tick)
        self.do_reset()

    def keyPressEvent(self,event):
        if event.key() == Qt.Qt.Key_Escape:
            self.do_close()
        elif event.key() == Qt.Qt.Key_R:
            self.do_reset()
            self.driving=False
        elif event.key() == Qt.Qt.Key_Enter:
            self.do_start()
        elif event.key() == Qt.Qt.Key_S:
            self.do_start()
        #else:
            #super().keyPressEvent(event)

    def display(self):
        self.lcd.display("%d:%05.2f" %(self.time // 60, self.time % 60))

    def tick(self):
        if self.afterSence:
            if self.afterSenceCount<10:
                self.afterSenceCount+=1
            else:
                #print "after finish"
                self.afterSenceCount=0
                self.afterSence=False
        else:
            if self.driving:
                i2c.write_byte(int(0x20),ord('g'))
                get = i2c.read_byte(0x20)
            else:
                i2c.write_byte(int(0x20),ord('s'))
                get = i2c.read_byte(0x20)
            
            if get==0:
                self.count+=1

        if self.count>=1:
            if self.driving:
                self.driving=False
                self.do_pause()
            else:
                self.driving=True
                self.do_start()

            self.afterSence=True
            self.afterSence+=1
            self.count=0
            get=0

        if self.driving:
            self.time += TICK_TIME/1000.0
        self.display()

    def do_start(self):
        self.timer.start()
        self.start.setText("Pause")
        self.start.clicked.disconnect()
        self.start.clicked.connect(self.do_pause)

    def do_pause(self):
        #self.timer.stop()
        self.start.setText("Start")
        self.start.clicked.disconnect()
        self.start.clicked.connect(self.do_start)
        
    def do_reset(self):
        #print type(self)
        self.do_pause()
        self.timer.stop()
        self.time = 0
        self.display()

app = Qt.QApplication(sys.argv)

watch = StopWatch()
watch.show()

app.exec_()
