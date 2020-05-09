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
import os

NETWORK_KEY= [0xb9, 0xa5, 0x21, 0xfb, 0xbd, 0x72, 0xc3, 0x45]

session_counter = 0
file_name = None
last_read = time.time()



def on_data(data):
    global file_name, heartrate_label, window, last_read
    
    heartrate = data[7]    
    heartrate_label.configure(text=heartrate)
    window.configure(bg = "green")
    last_read = time.time()
    
       
    if file_name is None:
        pass
    else:
        now = datetime.now().strftime("%H:%M")
        with open(file_name,"a") as file:        
            file.write(now + "," + str(heartrate) + "\n" )   
       

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
    global last_read, window
    while(True):
        now = time.time()
        if(now - last_read > 1):
           window.configure(bg = "red")

def create_dir(file_path):
    global directory
    current_directory = os.getcwd()
    directory = os.path.join(current_directory, file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def on_clicked(event=None):
    global file_name, session_counter, directory, window, control_button
    if file_name is None:
        session_counter += 1
        file_name = f"recording_{session_counter}.csv"
        file_name = os.path.join(directory, file_name)   
        recording_Label = Label(window, text=f"session {session_counter}")
        recording_Label.grid(column = 0, row=(session_counter*2))
        control_button.configure(text = "stop")
        
    else:
        last_file = file_name           
        file_name = None
        reads = []           

        with open(last_file) as file:
            reader = csv.reader(file)
            for row in reader:
                reads.append(row[-1])        
        
        reads = list(map(int, reads))
        
        mean = round(statistics.mean(reads),1)
        standard_deviation = round(statistics.stdev(reads),1)
        max_reading = max(reads)
        min_reading = min(reads)
        
        stats = f"av:{mean}, SD:{standard_deviation}, max:{max_reading}, min:{min_reading}"

        with open(last_file,"a") as file:
            file.write("\n"+stats)
        
        recording_Label = Label(window, text=stats)
        recording_Label.grid(column = 0, row=((session_counter*2)+1))       
       
        control_button.configure(text = "start")
 
def create_gui():
    global window, heartrate_label, control_button
        
    today = datetime.now().strftime("%Y%m%d%H%M")
    create_dir(today)

    init_thread = threading.Thread(
        target = create_node
        )
    init_thread.start()
    
    active_connection_thread = threading.Thread(
        target = connection_checker
        )
    active_connection_thread.start()
    
    window = Tk()
    window.title("Heart Rate Recorder")
    window.geometry("500x500")
    
    heartrate_label = Label(window, text='0')
    heartrate_label.grid(column = 0, row=0)
            
    control_button = Button(window, text="start", command=on_clicked)
    control_button.grid(column=0, row=1)    
    
    window.bind('<space>', on_clicked)

    window.mainloop()

create_gui()