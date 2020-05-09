from datetime import datetime
from tkinter import Tk
from tkinter import Button
from tkinter import Label

from ant.easy.node import Node
from ant.easy.channel import Channel
from ant.base.message import Message

import csv
import logging
import struct
import threading
import time
import statistics
import sys

NETWORK_KEY= [0xb9, 0xa5, 0x21, 0xfb, 0xbd, 0x72, 0xc3, 0x45]

counter = 0
fileName = None
lastRead = time.time()
today = datetime.now().strftime("%Y%m%d%H%M")


def on_data(data):
    global fileName, heartRateLabel, connectionIndicator, lastRead
    
    heartrate = data[7]    
    heartRateLabel.configure(text=heartrate)
    connectionIndicator.configure(bg = "green")
    lastRead = time.time()
       
    if fileName is None:
        pass
    else:
        file = open(fileName,"a")        
        file.write(str(heartrate) + ",")     

def createNode():
    global node
    try:  
        node = Node()
        node.set_network_key(0x00, NETWORK_KEY)
        channel = node.new_channel(Channel.Type.BIDIRECTIONAL_RECEIVE)

        channel.on_broadcast_data = on_data
        channel.on_burst_data = on_data

        channel.set_period(8070)
        channel.set_search_timeout(12)
        channel.set_rf_freq(57)
        channel.set_id(0, 120, 0)
        channel.open()          
        node.start()
    finally:
        node.stop()

def on_clicked():
    global fileName, counter, today, window, control_Button
    if fileName is None:
        fileName = f"recording_{today}_{counter}.csv"
        counter += 1
        recording_Label = Label(window, text=fileName)
        recording_Label.grid(column = 0, row=(counter*2))
        control_Button.configure(text = "stop")
    else:
        lastFile = fileName           
        fileName = None
        
        file = open(lastFile)
        data = csv.reader(file)      
        reads = list(data)[0]
        file.close()
        
        reads.pop()
        reads = list(map(int, reads))
        
        mean = round(statistics.mean(reads),1)
        standardDeviation = round(statistics.stdev(reads),1)
        maxReading = max(reads)
        minReading = min(reads)
        
        stats = f"av: {mean}, SD: {standardDeviation}, max: {maxReading}, min: {minReading}"
        file = open(lastFile,"a")
        file.write("\n"+stats)
        
        recording_Label = Label(window, text=stats)
        recording_Label.grid(column = 0, row=((counter*2)+1), columnspan=4)       
       
        control_Button.configure(text = "start")
 
def connectionChecker(): 
    global lastRead, connectionIndicator
    while(True):
        now = time.time()
        if(now - lastRead > 1):
            connectionIndicator.configure(bg = "red")

def createGui():
    global window, heartRateLabel, connectionIndicator, control_Button

    init_Thread = threading.Thread(
        target = createNode
        )
    init_Thread.start()
    
    activeConnection_Thread = threading.Thread(
        target = connectionChecker
        )
    activeConnection_Thread.start()
    
    window = Tk()
    window.title("Heart Rate Recorder")
    
    heartRateLabel = Label(window, text='0')
    heartRateLabel.grid(column = 2, row=0)

    connectionIndicator = Button(window, text="connection", bg = "red")
    connectionIndicator.grid(column=0, row=0, columnspan=2)
            
    control_Button = Button(window, text="start", command=on_clicked)
    control_Button.grid(column=0, row=1)


    window.mainloop()

createGui()