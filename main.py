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
import statistics
import sys

NETWORK_KEY= [0xb9, 0xa5, 0x21, 0xfb, 0xbd, 0x72, 0xc3, 0x45]

counter = 0
fileName = None

def on_data(data):
    global fileName, heartRateLabel
    
    heartrate = data[7]
    
    heartRateLabel.configure(text=heartrate)
       
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

def on_start():
    global fileName, counter, window
      if fileName is None:
        pass
    else:
        fileName = "recording_" + str(counter)+".csv"
        counter += 1
        recording_Label = Label(window, text=fileName)
        recording_Label.grid(column = 0, row=(counter*2))
    
    
    
def on_stop():
    global fileName, window
    if fileName is None:
        pass
    else:
        lastFile = fileName           
        fileName = None
        
        file = open(lastFile)
        data = csv.reader(file)      
        reads = list(data)[0]
        file.close()
        
        reads.pop()
        reads = list(map(int, reads))
        
        mean = statistics.mean(reads)
        standardDeviation = statistics.stdev(reads)
        maxReading = max(reads)
        minReading = min(reads)
        
        stats = f"av: {mean}, SD: {standardDeviation}, max: {maxReading}, min: {minReading}"
        file = open(lastFile,"a")
        file.write("\n"+stats)
        
        recording_Label = Label(window, text=stats)
        recording_Label.grid(column = 0, row=((counter*2)+1))
    

def createGui():
    init_Thread = threading.Thread(
        target = createNode
        )
    init_Thread.start()
    
    global window, heartRateLabel
    
    window = Tk()
    window.title("Heart Rate Recorder")
    
    heartRateLabel = Label(window, text='0')
    heartRateLabel.grid(column = 2, row=0)
            
    gentle_StartButton = Button(window, text="start", command=on_start)
    gentle_StartButton.grid(column=0, row=1)
    
    gentle_StopButton = Button(window, text="stop", command=on_stop)
    gentle_StopButton.grid(column=1, row=1)
    
    window.mainloop()

createGui()