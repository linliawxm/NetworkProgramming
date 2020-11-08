#!/usr/bin/python
# -*- coding: UTF-8 -*-
# File Name：Server.py
# Created: 11/04/2020
# Author: Li Lin & Anika Tasnim

import os
import sys
import socket
import threading
import tkinter as tk
import tkinter.scrolledtext as ScrolledText
from datetime import datetime
import time
import struct
import re
import zipfile

serverPortBase = 12000

#Create main window
window = tk.Tk()
#Set widnow's title
window.title('Server')
#Set window width and height
window.geometry('1040x650')

LoggingText = ScrolledText.ScrolledText(window, height=10, width = 68)
LoggingText.place(x=200, y=30, anchor='nw')

ReceivedText = ScrolledText.ScrolledText(window, height=33, width = 68)
ReceivedText.place(x=10, y=200, anchor='nw')

ProcessedText = ScrolledText.ScrolledText(window, height=33, width = 68)
ProcessedText.place(x=520, y=200, anchor='nw')

#Labels
LogLabel = tk.Label(window, text='Log')
LogLabel.place(x=200, y=5, anchor='nw')

ReceivedLabel = tk.Label(window, text='Received')
ReceivedLabel.place(x=20, y=175, anchor='nw')

ProcessedLabel = tk.Label(window, text='Processed')
ProcessedLabel.place(x=530, y=175, anchor='nw')

#Add check button
IsCompressedVar = tk.IntVar()
checkButton = tk.Checkbutton(window, text='Send compressed file ',variable=IsCompressedVar, onvalue=1, offvalue=0)
checkButton.place(x=750, y=30, anchor='nw')


def StartServerThread():
    portIndex = 0
    try:
        while True:
            #Create socket with IPv4/TCP type
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversocket:
                #bind with server address and port
                serversocket.bind(('',serverPortBase + portIndex))
                #Start to monitor
                serversocket.listen(1)
                LoggingText.insert('insert', 'Waiting for connection\n')
                #wait for client's connection
                connection,addr = serversocket.accept()
                #print(connection, addr)
                LoggingText.insert('insert', 'connected with {0}:{1}\n'.format(addr[0],addr[1]))
                LoggingText.insert('insert', 'Waiting for request\n')
                rcv_thread = threading.Thread(target=ReceiveDataThread, name = 'Thread{}'.format(serverPortBase + portIndex), args=(connection,addr), daemon=True)
                rcv_thread.start()
                portIndex = portIndex + 1

    except socket.error as msg:
        print(msg)
    else:
        print("Start thread finished")

def UpdateLoggingToEnd():
    while True:
        LoggingText.see('end')
        time.sleep(0.5)

def StartServer():
    start_thread = threading.Thread(target=StartServerThread, name = 'StartServerThread', daemon=True)
    if not start_thread.is_alive():
        start_thread.start()
        print('Start threading started')
    else:
        LoggingText.insert('insert', 'server is already started\n')

    UpdateLogging_thread = threading.Thread(target=UpdateLoggingToEnd, name = 'UpdateLoggingthread', daemon=True)
    if not UpdateLogging_thread.is_alive():
        UpdateLogging_thread.start()


StartButton = tk.Button(window, text='Start', font=('Arial',12), width=14, height=4, command = StartServer)
StartButton.place(x=30, y=30, anchor='nw')


#reqtype = ('SEARCH','REPLACE','REVERSE')
def ReceiveDataThread(connection,address):
    isConnected = True
    request = ''
    search_word = ''
    replace_word = ''
    with connection:
        status = 'WAIT_FOR_REQUEST'
        while isConnected:
            print('waiting receive data')
            if(status == 'WAIT_FOR_REQUEST'):
                #Receive message from client
                message = connection.recv(1024)
                if not message:
                    isConnected = False
                    break
                message = message.decode()
                print(message)
                if message.find('SEARCH+') != -1:
                    LoggingText.insert('insert', 'Search request received and accepted\n')
                    request = 'SEARCH'
                    search_word = message.split('+',1)[1]
                    if search_word == '':
                        message = 'No search word defined!'
                        #keep current status
                    else:
                        message = 'Search request accepted'
                        status = 'WAIT_FOR_FILE_INFO'
                    connection.send(message.encode())
                elif message.find('REPLACE+') != -1:
                    LoggingText.insert('insert', 'Replace request received and accepted\n')
                    request = 'REPLACE'
                    msg_list = message.split('+',2)
                    search_word = msg_list[1]
                    replace_word = msg_list[2]
                    if search_word == '':
                        message = 'No search word defined!'
                        #keep current status
                    else:
                        message = 'Replace request accepted'
                        status = 'WAIT_FOR_FILE_INFO'
                    connection.send(message.encode())
                elif message =='REVERSE':
                    LoggingText.insert('insert', 'reverse request received and accepted\n')
                    request = 'REVERSE'
                    message = 'Reverse request accepted'
                    connection.send(message.encode())
                    status = 'WAIT_FOR_FILE_INFO'
                elif message == 'EXIT':
                    LoggingText.insert('insert', 'Exit request received\n')
                    connection.close()
                    isConnected = False
                else:
                    message ='unrecognized request!'
            elif (status == 'WAIT_FOR_FILE_INFO'):
                fileinfo_size = struct.calcsize('128sQI')
                fileinfo_data = connection.recv(fileinfo_size)
                if not fileinfo_data:
                    isConnected = False
                    break
                #Receive file name and size info
                filename,filesize,IsCompressed = struct.unpack('128sQI',fileinfo_data) #file name lentgh = 128 bytes; filesize = 8bytes; I:unsigned int for compression
                rcv_file_name = filename.decode('utf-8').strip('\x00')
                LoggingText.insert('insert', 'Head info received\n')

                #Receive the data of file
                received_size = 0
                all_data_str = ''
                #Clear the content firstly
                ReceivedText.delete(1.0,'end')
                with open(rcv_file_name, 'wb') as rcv_file_handle:
                    while not (received_size == filesize):
                        if(filesize - received_size > 1024):
                            data = connection.recv(1024)
                            if not data:
                                isConnected = False
                                break
                            received_size += len(data)
                        else:
                            data = connection.recv(filesize - received_size)
                            received_size = filesize
                        rcv_file_handle.write(data)

                if isConnected == False:
                    LoggingText.insert('insert', '{0} file transfer failed\n'.format(rcv_file_name))
                else:
                    LoggingText.insert('insert', 'Received all data of {0}\n'.format(rcv_file_name))
                    ProcessedText.delete(1.0,'end')
                    if IsCompressed:
                        with zipfile.ZipFile(rcv_file_name, 'r') as zf:
                            filepath = zf.extract(zf.namelist()[0]) #suppose only one file
                            rcv_file_name = os.path.basename(filepath)
                            print(rcv_file_name)

                    with open(rcv_file_name,'rb') as rf:
                        all_data_str = rf.read().decode('utf-8')
                    ReceivedText.insert('insert',all_data_str)

                    #Process the file according to request
                    if request == 'SEARCH':
                        #Search
                        count = all_data_str.count(search_word)
                        message = 'There are {0} words "{1}" found in {2}.'.format(count,search_word,rcv_file_name)
                        ProcessedText.insert('insert','There are {0} words "{1}" found in {2}'.format(count,search_word,rcv_file_name))
                        connection.send(message.encode())
                        status = 'WAIT_FOR_REQUEST'
                        LoggingText.insert('insert', 'Search result sent\n')
                    elif request == 'REPLACE':
                        #Replace
                        replaced_data = all_data_str.replace(search_word,replace_word)
                        replaced_file_name = os.path.join('./', 'Replaced_' + rcv_file_name)
                        ProcessedText.insert('insert',replaced_data)
                        #Store local file
                        with open(replaced_file_name, 'wb') as new_file_handle:
                            new_file_handle.write(replaced_data.encode())
                        if IsCompressedVar.get() == 1:
                            with zipfile.ZipFile('Replaced.zip', 'w', zipfile.ZIP_DEFLATED) as f:
                                f.write(replaced_file_name)
                            filepath = 'Replaced.zip'
                            replaced_file_name = 'Replaced.zip'
                            filesize = os.stat('Replaced.zip').st_size
                        else:
                            filesize = os.stat(replaced_file_name).st_size

                        with open(replaced_file_name, 'rb') as new_file_handle:
                            #Send file info to client
                            fileinfo_size = struct.calcsize('128sQI')    #file name lentgh = 128 bytes; filesize = 8bytes; isCompressed = 2bytes(int)
                            #define file head info, including name and size
                            fhead = struct.pack('128sQI', bytes(replaced_file_name.encode('utf-8')), filesize, IsCompressedVar.get())
                            connection.send(fhead)
                            LoggingText.insert('insert', 'Replaced file header info sent\n')
                            #send file data to client
                            send_data = new_file_handle.read()
                            connection.sendall(send_data)
                            LoggingText.insert('insert', 'Replaced file send over...\n')
                        status = 'WAIT_FOR_REQUEST'

                    elif request == 'REVERSE':
                        #Reverse
                        data_str_list = all_data_str.split()
                        reversed_data = ' '.join(reversed(data_str_list))
                        ProcessedText.insert('insert',reversed_data)
                        reversed_file_name = os.path.join('./', 'Replaced_' + rcv_file_name)
                        #Store local file
                        with open(reversed_file_name, 'wb') as new_file_handle:
                            new_file_handle.write(reversed_data.encode())
                        if IsCompressedVar.get() == 1:
                            with zipfile.ZipFile('Reversed.zip', 'w', zipfile.ZIP_DEFLATED) as f:
                                f.write(reversed_file_name)
                            filepath = 'Reversed.zip'
                            reversed_file_name = 'Reversed.zip'
                            filesize = os.stat('Reversed.zip').st_size
                        else:
                            filesize = os.stat(reversed_file_name).st_size

                        with open(reversed_file_name, 'rb') as new_file_handle:
                            #Send file info to client
                            fileinfo_size = struct.calcsize('128sQI')    #file name lentgh = 128 bytes; filesize = 8bytes
                            #define file head info, including name and size
                            fhead = struct.pack('128sQI', bytes(reversed_file_name.encode('utf-8')), filesize, IsCompressedVar.get())
                            connection.send(fhead)
                            LoggingText.insert('insert', 'Reversed file header info sent\n')
                            #send file data to client
                            send_data = new_file_handle.read()
                            connection.sendall(send_data)
                            LoggingText.insert('insert', 'Reversed file send over...\n')
                        status = 'WAIT_FOR_REQUEST'
                    else:
                        message = 'unrecognized request!'
                        status = 'WAIT_FOR_REQUEST'

            else:
                print('Server is in unknown status')
                status = 'WAIT_FOR_REQUEST'
    LoggingText.insert('insert', 'Connection closed\n')


window.mainloop()

