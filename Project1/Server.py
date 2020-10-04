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

text = tk.Text(master=window)
text.pack(expand=True, fill="both")

entry = tk.Entry(master=window)
entry.pack(expand=True, fill="x")

frame = tk.Frame(master=window)
frame.pack()

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# class ServerSocket(object):
#     client = ''

#     def __init__(self, port):
#         self.port = port
#         self.serversocket = socket(AF_INET, SOCK_STREAM)

#     def start(self):
#         #bind with server address and port
#         self.serversocket.bind(("", self.port))
#         #Start to monitor
#         self.serversocket.listen(1)
#         now = str(datetime.now())[:-7]
#         text.insert("insert", "({}) : Connected.\n".format(now))
#         #wait for client's connection
#         self.connection, self.addr = self.serversocket.accept()
#         self.client = self.connection
#         data = self.connection.recv(1024)
#         text.insert("insert", "({}) : {} connected.\n".format(str(datetime.now())[:-7], str(data)[1:]))

#     def receive(self):
#         with self.connection:
#             while True:
#                 #Receive message from client
#                 message = self.connection.recv(1024)


#     def send(self):
#         with self.connection:
#             self.connection.send('xxx')

# srv = ServerSocket(serverPort)

def StartServerThread():
    try:
        #bind with server address and port
        serversocket.bind(('',serverPort))
        #Start to monitor
        serversocket.listen(1)
        print('The server is ready to receive...')
        #wait for client's connection
        connection,addr = serversocket.accept()

        rcv_thread = threading.Thread(target=ReceiveDataThread,args=(connection,addr))
        rcv_thread.setDaemon(True)
        rcv_thread.start()
        print('Receive threading started')
    except socket.error as msg:
        print(msg)
    else:
        print('Socket created.')


def StartServer():
    start_thread = threading.Thread(target=StartServerThread)
    start_thread.setDaemon(True)
    start_thread.start()
    print('Start threading started')

StartButton = tk.Button(master=frame, text='Start', font=('Arial',12), width=14, height=1, command = StartServer)
StartButton.pack(side="left")


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
                    request = 'SEARCH'
                    search_word = message.split('+',1)[1]
                    if search_word == '':
                        message = 'No search word defined!'
                        #keep current status
                    else:
                        message = 'Search request accepted'
                        status = 'WAIT_FOR_FILE_INFO'
                elif message.find('REPLACE+') != -1:
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
                        print('received all data of {0}'.format(rcv_file_name))

                    #Process the file according to request
                    if request == 'SEARCH':
                        #Search
                        count = all_data_str.count(search_word)
                        message = 'Hello, Client. There are {0} words found in {1}.'.format(count,rcv_file_name)
                        connection.send(message.encode())
                        status = 'WAIT_FOR_REQUEST'
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
                            print('sent file header')
                            #send file data to client
                            while True:
                                send_data = new_file_handle.read(1024)
                                print(send_data.decode())
                                if not send_data:
                                    print('Replaced file send over...')
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
                            print('sent file header')
                            #send file data to client
                            while True:
                                send_data = new_file_handle.read(1024)
                                if not send_data:
                                    print('Reversed file send over...')
                                    break
                                connection.send(send_data)
                        status = 'WAIT_FOR_REQUEST'
                    else:
                        message = 'unrecognized request!'
                        status = 'WAIT_FOR_REQUEST'

            else:
                print('Server is in unknown status')
                status = 'WAIT_FOR_REQUEST'


if __name__ == "__main__":
    window.mainloop()
    serversocket.close()


# with socket(AF_INET, SOCK_STREAM) as serverSocket:
#     #bind with server address and port
#     serverSocket.bind(('',serverPort))
#     #Start to monitor
#     serverSocket.listen(1)
#     print('The server is ready to receive...')
#     #wait for client's connection
#     connectionSocket,addr = serverSocket.accept()

#     with connectionSocket:
#         while True:
#             #Receive message from client
#             message = connectionSocket.recv(1024)

#             #Check if empty message
#             if not message:
#                 break
#             #seperating the words by using split functions
#             words = message.split()
#             #counting the number of words
#             count = len(words)
#             print('Received:' + message.decode() + ' ;Number of Words = ' + str(count) + '\n')
#             #Change all letters to Upper case
#             modifiedMessage = message.decode().upper()
#             #Count the number of words from received message
#             messageNum = str(count)
#             #Send uppder case letters to Client
#             connectionSocket.send(modifiedMessage.encode())
#             #Send word number to Client
#             connectionSocket.send(messageNum.encode())
#     print('Connection closed')
# print('Socket closed')
# print('Server closed')

