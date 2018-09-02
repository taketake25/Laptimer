import sys

#import RPi.GPIO as GPIO
#import smbus
import time
from PyQt5 import Qt
from PyQt5.QtCore import QTimer ,QTime
from PyQt5.uic import loadUi
import threading
import csv
#i2c=smbus.SMBus(1)

TICK_TIME=30

class StopWatch(Qt.QMainWindow):
    def __init__(self,parent=None):
        super(StopWatch,self).__init__()
        self.lapNum=0 # 何回目の走行か
        self.lapTime=[0,0,0]
        self.startTime=0
        self.finishTime=0
        self.runTime=0
        self.getFromNucleo=1
        self.driving=False #走行中であるか
        self.afterSence=False #センサーが反応してすぐか
        self.afterSenceCount=0

        self.rf=open(sys.argv[1],"r",encoding="utf-8") #csvファイルの読み込み
        filename="./out/%s%d.csv"%(sys.argv[2],int(time.time())%100000)
        self.wf=open(filename,"w", newline='')

        self.reader=csv.reader(self.rf, delimiter=",") #リスト形式
        self.writer=csv.writer(self.wf, delimiter=",") #リスト形式
        self.header=next(self.rf) #最初の行を得る

        self.ui=loadUi("TimerGui.ui",self) #.ui ファイルからスタイルを読み込み
        self.reset.clicked.connect(self.do_reset) #ボタンと関数の関連付け
        self.start.clicked.connect(self.do_start)
        self.save.clicked.connect(self.do_save)

        self.timer=Qt.QTimer() #アニメーション(7セグ表示部分)用
        self.timer.setInterval(TICK_TIME)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        # csvファイルの1行1列の数字にゴミが入るので、回避代わりに(誰かデバッグして)
        self.do_reset()

    def keyPressEvent(self,event):
        if event.key() == Qt.Qt.Key_Escape:
            # self.rf.close()
            # self.wf.close()
            self.close()
        elif event.key() == Qt.Qt.Key_R:
            self.do_reset()
        elif event.key() == Qt.Qt.Key_P:
            self.do_pause()
        elif event.key() == Qt.Qt.Key_S:
            self.do_save()
        elif event.key() == Qt.Qt.Key_T:
            self.getFromNucleo=0;

    def display(self):
        now=time.time()
        if not self.driving:
            now=self.finishTime

        self.runTime=now-self.startTime
        # print("%6.2f, %6.2f, %6.2f, %6.2f"%(self.startTime,self.finishTime,now,self.runTime))
        self.currentTime.display("%d:%05.2f" %(self.runTime // 60, self.runTime % 60))

    def tick(self):
        count=0
        if self.afterSence:
            if self.afterSenceCount<5: # センサーが入ってから一定時間空ける
                self.afterSenceCount+=1
            else:
                self.afterSenceCount=0
                self.afterSence=False
        else:
            """
            if self.driving:
                i2c.write_byte(int(0x20),ord('g'))
                self.getFromNucleo=i2c.read_byte(0x20)
            else:
                i2c.write_byte(int(0x20),ord('s'))
                self.getFromNucleo=i2c.read_byte(0x20)
            """ 
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

    def do_start(self): #
        if self.lapNum<=3:
            self.startTime=time.time()
            self.driving=True
            self.start.setText("Pause")
            self.start.clicked.disconnect()
            self.start.clicked.connect(self.do_pause)

    def do_pause(self):
        #self.timer.stop()
        self.finishTime=time.time()

        # self.firstTimeVal.
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
    
    def do_reset(self):
        if not self.lapNum==0:
            self.do_save()
        self.driving=False
        self.runTime=0
        self.startTime=0
        self.finishTime=0

        #最終行まで行くとエラー。デバッグめんどいし、csvファイルの最後のほうにダミーの複数行を推奨
        self.header=next(self.rf) 
        words=self.header.split(',')

        print(words)
        self.key.setText(words[0])
        self.group.setText(words[1])
        self.name.setText(words[2])
        self.machineName.setText(words[3])
        self.firstTimeVal.setText("0:00.00")
        self.secondTimeVal.setText("0:00.00")
        self.lapNum=1
        self.lapTime=[0,0,0]

    def do_save(self): #結果をcsvファイルに書き込み
        print(self.lapTime)
        for i in range(3):
            words=self.header.split(',')
            writeWord="%s,%s,%s,%s,%d,%6.2f"%(int(words[0]),str(words[1]),str(words[2]),str(words[3]),1,self.lapTime[i])
            self.writer.writerow(writeWord.split(','))

    def close(self):
        self.do_reset()
        self.rf.close()
        self.wf.close()
        super.close()

if __name__ == '__main__':
    app=Qt.QApplication(sys.argv)
    watch=StopWatch()
    watch.show()
    app.exec_()