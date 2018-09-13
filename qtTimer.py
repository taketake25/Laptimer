import sys

import RPi.GPIO as GPIO
import smbus
import time
from PyQt5 import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer ,QTime
from PyQt5.QtGui import QPainter, QColor 
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
#from PyQt5.QtCore import Qt
import threading
import csv

i2c=smbus.SMBus(1)
TICK_TIME=70

class StopWatch(Qt.QMainWindow):
    def __init__(self,parent=None):
        super(StopWatch,self).__init__()
        self.lapNum=0 
        self.lapTime=[0,0,0]
        self.startTime=0
        self.finishTime=0
        self.runTime=0
        self.getFromNucleo=1
        self.driving=False 
        self.afterSence=False 
        self.afterSenceCount=0
        self.sanpunStart=0

        filename="./out/%s%d.csv"%(sys.argv[2],int(time.time())%100000)
        #self.rf=open(sys.argv[1],"r",encoding="utf-8") 
        self.rf=open(sys.argv[1],"r") 
        #self.wf=open(filename,"w", newline='')
        self.wf=open(filename,"w")
        self.reader=csv.reader(self.rf, delimiter=",") 
        self.writer=csv.writer(self.wf, delimiter=",")
        for a in  range(int(sys.argv[3])):
            self.header=next(self.rf) 

        self.ui=loadUi("TimerGui.ui",self)
        self.reset.clicked.connect(self.do_reset) 
        self.start.clicked.connect(self.do_start)
        self.save.clicked.connect(self.do_save)

        self.timer=Qt.QTimer()
        self.timer.setInterval(TICK_TIME)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        self.timeLimit.setValue(0)
        self.do_reset(False)


    def __del__(self,parent=None):
        self.do_reset(False)
        self.rf.close()
        self.wf.close()
    

    def keyPressEvent(self,event):
        if event.key() == Qt.Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Qt.Key_R:
            self.do_reset(False)
        elif event.key() == Qt.Qt.Key_P:
            self.do_pause()
        elif event.key() == Qt.Qt.Key_N:
            self.do_reset(True)
        elif event.key() == Qt.Qt.Key_T:
            self.getFromNucleo=0


    def display(self):
        now=time.time()
        self.timeLimit.setValue((now-self.sanpunStart)/1.8)

        if not self.driving:
            now=self.finishTime
        self.runTime=now-self.startTime
        self.currentTime.display("%d:%05.2f" %(self.runTime // 60, self.runTime % 60))


    def tick(self):
        count=0
        if self.afterSence:
            if self.afterSenceCount<5: 
                self.afterSenceCount+=1
            else:
                self.afterSenceCount=0
                self.afterSence=False
        else:
            if self.driving:
                i2c.write_byte(int(0x20),ord('g'))
                self.getFromNucleo=i2c.read_byte(0x20)
                print("%c, %d"%('g',self.getFromNucleo))
            else:
                i2c.write_byte(int(0x20),ord('s'))
                self.getFromNucleo=i2c.read_byte(0x20)
                print("%c, %d"%('s',self.getFromNucleo))
             
            if self.getFromNucleo==0:
                count+=1

        if count>=1:
            if self.driving:
                self.do_pause()
            else:
                self.do_start()
            self.afterSence=True
            self.afterSence+=1
            self.getFromNucleo=1
            count=0

        self.display()


    def do_start(self):
        if self.sanpunStart==0:
            self.sanpunStart=time.time()

        if self.lapNum<=3:
            self.startTime=time.time()
            self.driving=True
            self.start.setText("Pause")
            self.start.clicked.disconnect()
            self.start.clicked.connect(self.do_pause)


    def do_pause(self):
        
        self.finishTime=time.time()

        self.runTime=self.finishTime-self.startTime
        if self.lapNum==1:
            self.lapTime[0]=self.runTime
            self.firstTimeVal.setText("%d:%05.2f" %(self.runTime // 60, self.runTime % 60))
        elif self.lapNum==2:
            self.lapTime[1]=self.runTime
            self.secondTimeVal.setText("%d:%05.2f" %(self.runTime // 60, self.runTime % 60))
        else:
            self.lapTime[2]=self.runTime

        self.driving=False
        self.start.setText("Start")
        self.start.clicked.disconnect()
        self.start.clicked.connect(self.do_start)
        self.lapNum+=1

    
    def do_reset(self,noResult):
        if not self.lapNum==0:
            self.do_save(noResult)
        self.driving=False
        self.runTime=0
        self.startTime=0
        self.finishTime=0
        
        self.header=next(self.rf) 
        words=self.header.split(',')

        print(words)
        sub=SubWindow(self)
        #sub.show()
        sub.setWindowFlags(Qt.Qt.Window|Qt.Qt.WindowStaysOnTopHint)
        sub.showMaximized()
        sub.setTexts(words[0],words[1],words[2],words[3])

        self.key.setText(words[0])
        self.group.setText(words[1])
        self.name.setText(words[2])
        self.machineName.setText(words[3])
        self.firstTimeVal.setText("0:00.00")
        self.secondTimeVal.setText("0:00.00")
        self.lapNum=1
        self.lapTime=[1000,1000,1000]
        self.sanpunStart=0
        self.timeLimit.setValue(0)


    def do_save(self,noResult): 
        t=self.firstTimeVal.text()
        if t[0]=='n':
            self.lapTime[0]=1000.0
        t=self.secondTimeVal.text()
        if t[0]=='n':
            self.lapTime[1]=1000.0
        if noResult:
            self.lapTime[2]=1000.0

        for i in range(3):
            print("%5.2f, "%(self.lapTime[i]) ,end="")
            writeWord="%s,%s,%s,%s,%d,%6.2f"%(self.key.text(),self.group.text(),self.name.text(),self.machineName.text(),i+1,self.lapTime[i])
            self.writer.writerow(writeWord.split(u','))
        print("\n")



class SubWindow(QtWidgets.QDialog):
    def __init__(self,parent=None):
        QtWidgets.QDialog.__init__(self,parent)
        self.initUI()
        self.setTexts(' ',' ',' ',' ')


    def initUI(self):
        box=QVBoxLayout()
        box.setSpacing(30)
        font1=QtGui.QFont()
        font2=QtGui.QFont()
        font1.setPointSize(120)
        font2.setPointSize(160)

#        self.keyLabel=QLabel()
        self.collegeLabel=QLabel()
        self.nameLabel=QLabel()
        self.machineNameLabel=QLabel()

#        self.keyLabel.setFont(font1)
        self.collegeLabel.setFont(font1)
        self.nameLabel.setFont(font2)
        self.machineNameLabel.setFont(font2)

#        self.keyLabel.setAlignment(Qt.Qt.AlignCenter)
        self.collegeLabel.setAlignment(Qt.Qt.AlignCenter)
        self.nameLabel.setAlignment(Qt.Qt.AlignCenter)
        self.machineNameLabel.setAlignment(Qt.Qt.AlignCenter)

#        self.keyLabel.setText('key')
        self.collegeLabel.setText('college')
        self.nameLabel.setText('name')
        self.machineNameLabel.setText('machine')

#        box.addWidget(self.keyLabel)
        box.addWidget(self.collegeLabel)
        box.addWidget(self.nameLabel)
        box.addWidget(self.machineNameLabel)
        
        self.setLayout(box)
        

    def setTexts(self,key,college,name,machineName):
#        self.keyLabel.setText(key)
        self.collegeLabel.setText(college)
        self.nameLabel.setText(name)
        self.machineNameLabel.setText(machineName)


    def keyPressEvent(self,event):
        if(event.key()):
            self.close()

if __name__ == '__main__':
    app=Qt.QApplication(sys.argv)
    watch=StopWatch()
    #watch.show()
    watch.showMaximized()
    app.exec_()
