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

session_counter = 0
file_name = None
last_read = time.time()
today = datetime.now().strftime("%Y%m%d%H%M")
heart_rate_label = None
connection_indicator = None


def on_data(data):
    global file_name, heart_rate_label, connection_indicator, last_read
    
    heartrate = data[7]    
    heart_rate_label.configure(text=heartrate)
    connection_indicator.configure(bg = "green")
    last_read = time.time()
       
    if file_name is None:
        pass
    else:
        with open(file_name, 'a') as file:
            file.write(str(heartrate) + ",")   

def create_node():
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

def connection_checker(): 
    global last_read, connection_indicator
    while True:
        now = time.time()
        if now - last_read > 1:
            connection_indicator.configure(bg = "red")

def on_clicked():
    global file_name, session_counter, today, window, control_Button
    if file_name is None:
        file_name = f"recording_{today}_{session_counter}.csv"
        session_counter += 1
        recording_Label = Label(window, text=file_name)
        recording_Label.grid(column = 0, row=(session_counter*2))
        control_Button.configure(text = "stop")
    else:
        last_file = file_name           
        file_name = None
        
        with open(last_file) as file:
            data = csv.reader(file)      
            reads = list(data)[0]
        
        reads.pop()
        reads = list(map(int, reads))
        
        mean = round(statistics.mean(reads),1)
        standard_deviation = round(statistics.stdev(reads),1)
        max_reading = max(reads)
        min_reading = min(reads)
        
        stats = f"av:{mean}, SD:{standard_deviation}, max:{max_reading}, min:{min_reading}"
        file = open(last_file,"a")
        file.write("\n"+stats)
        file.close()
        
        recording_Label = Label(window, text=stats)
        recording_Label.grid(column = 0, row=((session_counter*2)+1), columnspan=4)       
       
        control_Button.configure(text = "start")
 
def createGui():
    global window, heart_rate_label, connection_indicator, control_Button

    init_Thread = threading.Thread(
        target = create_node
        )
    init_Thread.start()
    
    activeConnection_Thread = threading.Thread(
        target = connection_checker
        )
    activeConnection_Thread.start()
    
    window = Tk()
    window.title("Heart Rate Recorder")
    window.geometry("500x500")
    
    heart_rate_label = Label(window, text='0')
    heart_rate_label.grid(column = 2, row=0)

    connection_indicator = Button(window, text="connection", bg = "red")
    connection_indicator.grid(column=0, row=0, columnspan=2)
            
    control_Button = Button(window, text="start", command=on_clicked)
    control_Button.grid(column=0, row=1)

    window.mainloop()

createGui()