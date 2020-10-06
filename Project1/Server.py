#!/usr/bin/python
# -*- coding: UTF-8 -*-
# File Name：Server.py
# Created: 9/16/2020
# Author: Li Lin & Anika Tasnim

import os
import sys
import socket
import threading
import tkinter as tk
from datetime import datetime
import struct
import re

serverPort = 12000

#Create main window
window = tk.Tk()
#Set widnow's title
window.title('Server')
#Set window width and height
window.geometry('500x500')

LoggingText = tk.Text(window, height=10, width = 68)
LoggingText.place(x=10, y=100, anchor='nw')

#Create socket with IPv4/TCP type
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



def StartServerThread():
    try:
        #bind with server address and port
        serversocket.bind(('',serverPort))
        #Start to monitor
        serversocket.listen(1)
        LoggingText.insert('insert', 'server listening\n')
        #wait for client's connection
        connection,addr = serversocket.accept()
        #print(connection, addr)
        LoggingText.insert('insert', 'connected with {0}:{1}\n'.format(addr[0],addr[1]))
        LoggingText.insert('insert', 'Waiting for request\n')
        rcv_thread = threading.Thread(target=ReceiveDataThread, name = 'ReceiveDataThread', args=(connection,addr), daemon=True)
        if not rcv_thread.is_alive():
            rcv_thread.start()
    except socket.error as msg:
        print(msg)
    else:
        print('Connected')

def StartServer():
    start_thread = threading.Thread(target=StartServerThread, name = 'StartServerThread', daemon=True)
    if not start_thread.is_alive():
        start_thread.start()
        print('Start threading started')
        #StartButton.config(text='Stop')
    else:
        LoggingText.insert('insert', 'server is already started\n')


StartButton = tk.Button(window, text='Start', font=('Arial',12), width=14, height=4, command = StartServer)
StartButton.place(x=150, y=5, anchor='nw')


#reqtype = ('SEARCH','REPLACE','REVERSE')
def ReceiveDataThread(connection,address):
    request = ''
    search_word = ''
    replace_word = ''
    with connection:
        status = 'WAIT_FOR_REQUEST'
        while True:
            print('waiting receive data')
            if(status == 'WAIT_FOR_REQUEST'):
                #Receive message from client
                message = connection.recv(1024).decode()
                print(message)
                if message.find('SEARCH+') != -1:
                    LoggingText.insert('insert', 'Research request received and accepted\n')
                    request = 'SEARCH'
                    search_word = message.split('+',1)[1]
                    if search_word == '':
                        message = 'No search word defined!'
                        #keep current status
                    else:
                        message = 'Search request accepted'
                        status = 'WAIT_FOR_FILE_INFO'
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
                elif message =='REVERSE':
                    LoggingText.insert('insert', 'reverse request received and accepted\n')
                    request = 'REVERSE'
                    message = 'Reverse request accepted'
                    status = 'WAIT_FOR_FILE_INFO'
                else:
                    message ='unrecognized request!'
                connection.send(message.encode())
            elif (status == 'WAIT_FOR_FILE_INFO'):
                fileinfo_size = struct.calcsize('128sQ')
                fileinfo_data = connection.recv(fileinfo_size)
                if fileinfo_data:
                    #Receive file name and size info
                    filename,filesize = struct.unpack('128sQ',fileinfo_data)
                    rcv_file_name = filename.decode('utf-8').strip('\x00')
                    LoggingText.insert('insert', 'Head info received\n')
                    #Receive the data of file
                    received_size = 0
                    all_data_str = ''
                    with open(rcv_file_name, 'wb') as rcv_file_handle:
                        while not (received_size == filesize):
                            if(filesize - received_size > 1024):
                                data = connection.recv(1024)
                                received_size += len(data)
                            else:
                                data = connection.recv(filesize - received_size)
                                received_size = filesize
                            rcv_file_handle.write(data)
                            all_data_str = all_data_str + data.decode()
                        LoggingText.insert('insert', 'Received all data of {0}\n'.format(rcv_file_name))

                    #Process the file according to request
                    if request == 'SEARCH':
                        #Search
                        count = all_data_str.count(search_word)
                        message = 'Hello, Client. There are {0} words found in {1}.'.format(count,rcv_file_name)
                        connection.send(message.encode())
                        status = 'WAIT_FOR_REQUEST'
                        LoggingText.insert('insert', 'Search result sent\n')
                    elif request == 'REPLACE':
                        #Replace
                        replaced_data = all_data_str.replace(search_word,replace_word)
                        replaced_file_name = os.path.join('./', 'Replaced_' + rcv_file_name)
                        #Store local file
                        with open(replaced_file_name, 'wb') as new_file_handle:
                            new_file_handle.write(replaced_data.encode())

                        with open(replaced_file_name, 'rb') as new_file_handle:
                            #Send file info to client
                            fileinfo_size = struct.calcsize('128sQ')    #file name lentgh = 128 bytes; filesize = 8bytes
                            #define file head info, including name and size
                            fhead = struct.pack('128sQ', bytes(replaced_file_name.encode('utf-8')), len(replaced_data.encode('utf-8')))
                            connection.send(fhead)
                            LoggingText.insert('insert', 'Replaced file header info sent\n')
                            #send file data to client
                            while True:
                                send_data = new_file_handle.read(1024)
                                print(send_data.decode())
                                if not send_data:
                                    LoggingText.insert('insert', 'Replaced file send over...\n')
                                    break
                                connection.send(send_data)
                                print(data.decode())
                        status = 'WAIT_FOR_REQUEST'

                    elif request == 'REVERSE':
                        #Reverse
                        data_str_list = all_data_str.split()
                        reversed_data = ' '.join(reversed(data_str_list))
                        reversed_file_name = os.path.join('./', 'Replaced_' + rcv_file_name)
                        #Store local file
                        with open(reversed_file_name, 'wb') as new_file_handle:
                            new_file_handle.write(reversed_data.encode())

                        with open(reversed_file_name, 'rb') as new_file_handle:
                            #Send file info to client
                            fileinfo_size = struct.calcsize('128sQ')    #file name lentgh = 128 bytes; filesize = 8bytes
                            #define file head info, including name and size
                            fhead = struct.pack('128sQ', bytes(reversed_file_name.encode('utf-8')), len(reversed_data.encode('utf-8')))
                            connection.send(fhead)
                            LoggingText.insert('insert', 'Reversed file header info sent\n')
                            #send file data to client
                            while True:
                                send_data = new_file_handle.read(1024)
                                if not send_data:
                                    LoggingText.insert('insert', 'Reversed file send over...\n')
                                    break
                                connection.send(send_data)
                        status = 'WAIT_FOR_REQUEST'
                    else:
                        message = 'unrecognized request!'
                        status = 'WAIT_FOR_REQUEST'

            else:
                print('Server is in unknown status')
                status = 'WAIT_FOR_REQUEST'



window.mainloop()
serversocket.close()

