#!/usr/bin/python
# -*- coding: UTF-8 -*-
# File Name：Client.py
# Created: 9/16/2020
# Author: Li Lin & Anika Tasnim
import socket
import tkinter as tk
from tkinter import filedialog
from  tkinter  import ttk
import os
import sys
import struct
import threading
import win32api

serverName = 'localhost'    #'192.168.0.15'
serverPort = 12000

# class Client(object):
#     def __init__(self,serverName,serverPort):
#         self.serverName = serverName
#         self.serverPort = serverPort
#         self.clientSocket = socket(AF_INET, SOCK_STREAM)

#     def connect(self):
#         #Setup connection with server
#         self.clientSocket.connect((self.serverName,self.serverPort))

#     def send(self):
#         pass

#     def receive(self):
#         pass

# c1 = Client(serverName,serverPort)

CurrentDirectory = os.getcwd()

#Create main window
window = tk.Tk()
#Set widnow's title
window.title('Client')
#Set window width and height
window.geometry('1350x900')

#Create a Entry
SearchWordVar = tk.StringVar()
SearchWordEntry = tk.Entry(window, show=None, font=('Arial',14), width = 15, textvariable=SearchWordVar)
SearchWordEntry.place(x=200, y=80, anchor='nw')
SearchWordVar.set('Mobile')

ReplaceWordVar = tk.StringVar()
ReplaceWordEntry = tk.Entry(window, show=None, font=('Arial',14), width = 15, textvariable=ReplaceWordVar)
ReplaceWordEntry.place(x=400, y=80, anchor='nw')
ReplaceWordVar.set('iPhone')

SourceFilePathVar = tk.StringVar()
SourceFilePathEntry = tk.Entry(window, show=None, font=('Arial',14), width = 44, textvariable=SourceFilePathVar)
SourceFilePathEntry.place(x=10, y=160, anchor='nw')
SourceFilePathVar.set('C:/GitHubProject/NetworkProgramming/Project1/Mobile IP wiki.txt')

SaveFileNameVar = tk.StringVar()
SaveFileNameEntry = tk.Entry(window, show=None, font=('Arial',14), width = 44, textvariable=SaveFileNameVar)
SaveFileNameEntry.place(x=700, y=160, anchor='nw')
SaveFileNameVar.set('output.txt')

#Create Text
SourceFileText = tk.Text(window, height=50, width = 90)
SourceFileText.place(x=10, y=200, anchor='nw')
if os.path.isfile(SourceFilePathVar.get()):
    with open(SourceFilePathVar.get(),'rb') as reader:
        SourceFileText.delete(1.0,'end')
        text = reader.read()
        SourceFileText.insert('insert',text)

ProcessedFileText = tk.Text(window, height=50, width = 90)
ProcessedFileText.place(x=700, y=200, anchor='nw')

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Create buttons
def ConnectServer():
    try:
        #Setup connection with server
        clientSocket.connect((serverName,serverPort))
        print('start connection')
        #print(clientSocket.recv(1024))
    except socket.error as msg:
        print(msg)
    else:
        print('connection established.')

ConnectButton = tk.Button(window, text='Connect', font=('Arial',12), width=10, height=5, command = ConnectServer)
ConnectButton.place(x=5, y=5, anchor='nw')

def SearchThread():
    #1.Send request to server
    search_word = SearchWordVar.get()

    request = 'SEARCH+' + search_word
    clientSocket.send(request.encode())

    #Receive message from server
    response = clientSocket.recv(1024)
    print(response.decode())
    if response.decode() == 'Search request accepted':
        filepath = SourceFilePathVar.get()
        if os.path.isfile(filepath):
            #2. Send file info to server
            fileinfo_size = struct.calcsize('128sQ')    #file name lentgh = 128 bytes; filesize = 8bytes
            #define file head info, including name and size
            fhead = struct.pack('128sQ', bytes(os.path.basename(filepath).encode('utf-8')),
                                    os.stat(filepath).st_size)
            clientSocket.send(fhead)
            #3. Send data to server
            with open(filepath, 'rb') as fp:
                while 1:
                    data = fp.read(1024)
                    if not data:
                        print('{0} file send over...'.format(filepath))
                        break
                    clientSocket.send(data)
            #4. Receive the search result
            response = clientSocket.recv(1024)
            #5. Display the search result
            print(response.decode())
            ProcessedFileText.delete(1.0,'end')
            ProcessedFileText.insert('insert',response.decode())
        else:
            print('The file path is not valid')


def ReplaceThread():
    #1.Send request to server
    search_word = SearchWordVar.get()
    replace_word = ReplaceWordVar.get()

    request = 'REPLACE+' + search_word +'+' + replace_word
    clientSocket.send(request.encode())

    #Receive message from server
    response = clientSocket.recv(1024)
    if response.decode() == 'Replace request accepted':
        filepath = SourceFilePathVar.get()
        if os.path.isfile(filepath):
            #2. Send file info to server
            fileinfo_size = struct.calcsize('128sQ')    #file name lentgh = 128 bytes; filesize = 8bytes
            #define file head info, including name and size
            fhead = struct.pack('128sQ', bytes(os.path.basename(filepath).encode('utf-8')),
                                    os.stat(filepath).st_size)
            clientSocket.send(fhead)
            #3. Send data to server
            with open(filepath, 'rb') as fp:
                while 1:
                    data = fp.read(1024)
                    if not data:
                        print('{0} file send over...'.format(filepath))
                        break
                    clientSocket.send(data)
            #4. Receive the replace result
            fileinfo_size = struct.calcsize('128sQ')
            fileinfo_data = clientSocket.recv(fileinfo_size)

            if fileinfo_data:
                filename,filesize = struct.unpack('128sQ',fileinfo_data)
                rcv_file_name = filename.decode('utf-8').strip('\x00')
                print('{0} is received and size is {1}'.format(rcv_file_name,filesize))

                received_size = 0
                received_data = ''
                while not (received_size == filesize):
                    if(filesize - received_size > 1024):
                        data = clientSocket.recv(1024)
                        received_size += len(data)
                    else:
                        data = clientSocket.recv(filesize - received_size)
                        received_size = filesize
                    received_data = received_data + data.decode()
                    print(data.decode())
                print('received all')
                #5. Display the replaced result
                ProcessedFileText.delete(1.0,'end')
                ProcessedFileText.insert('insert', received_data)
        else:
            print('The file path is not valid')

def ReverseThread():
    #1.Send request to server
    request = 'REVERSE'
    clientSocket.send(request.encode())

    #Receive message from server
    response = clientSocket.recv(1024)
    if response.decode() == 'Reverse request accepted':
        filepath = SourceFilePathVar.get()
        if os.path.isfile(filepath):
            #2. Send file info to server
            fileinfo_size = struct.calcsize('128sQ')    #file name lentgh = 128 bytes; filesize = 8bytes
            #define file head info, including name and size
            fhead = struct.pack('128sQ', bytes(os.path.basename(filepath).encode('utf-8')),
                                    os.stat(filepath).st_size)
            clientSocket.send(fhead)
            #3. Send data to server
            with open(filepath, 'rb') as fp:
                while 1:
                    data = fp.read(1024)
                    if not data:
                        print('{0} file send over...'.format(filepath))
                        break
                    clientSocket.send(data)
            #4. Receive the reversed result
            fileinfo_size = struct.calcsize('128sQ')
            fileinfo_data = clientSocket.recv(fileinfo_size)
            if fileinfo_data:
                filename,filesize = struct.unpack('128sQ',fileinfo_data)

                received_size = 0
                received_data = ''
                while not (received_size == filesize):
                    if(filesize - received_size > 1024):
                        data = clientSocket.recv(1024)
                        received_size += len(data)
                    else:
                        data = clientSocket.recv(filesize - received_size)
                        received_size = filesize
                    received_data = received_data + data.decode()
                print('received all')
            #5. Display the replaced result
            ProcessedFileText.delete(1.0,'end')
            ProcessedFileText.insert('insert', received_data)
        else:
            print('The file path is not valid')

def SearchWordFromServer():
    search_thread = threading.Thread(target=SearchThread, name='SearchThread')
    search_thread.setDaemon(True)
    search_thread.start()
    print('Search threading started')

    pass

SearchButton = tk.Button(window, text='Search Word', font=('Arial',12), width=14, height=2, command = SearchWordFromServer)
SearchButton.place(x=220, y=5, anchor='nw')

def ReplaceWordByServer():
    replace_thread = threading.Thread(target=ReplaceThread, name='replace_thread')
    replace_thread.setDaemon(True)
    replace_thread.start()
    print('Replace threading started')

ReplaceButton = tk.Button(window, text='Replace Word', font=('Arial',12), width=14, height=2, command = ReplaceWordByServer)
ReplaceButton.place(x=420, y=5, anchor='nw')

def ReverseWordByServer():
    reverse_thread = threading.Thread(target=ReverseThread, name='reverse_thread')
    reverse_thread.setDaemon(True)
    reverse_thread.start()
    print('Reverse threading started')

ReverseButton = tk.Button(window, text='Reverse Word', font=('Arial',12), width=14, height=2, command = ReverseWordByServer)
ReverseButton.place(x=700, y=5, anchor='nw')

def DisplayFile():
    pass

DisplayButton = tk.Button(window, text='Display file', font=('Arial',12), width=14, height=2, command = DisplayFile)
DisplayButton.place(x=900, y=5, anchor='nw')

def SelectFile():
    SourceFilePath = filedialog.askopenfilename(title='Select source file', filetypes=[("Text files", "*.txt"), ("all files", "*.*")])
    SourceFilePathEntry.delete(0,tk.END)
    SourceFilePathEntry.insert(0,SourceFilePath)
    with open(SourceFilePathVar.get(),'rb') as reader:
        SourceFileText.delete(1.0,'end')
        text = reader.read()
        SourceFileText.insert('insert',text)

SelectButton = tk.Button(window, text='Source path...', font=('Arial',12), width=14, height=1, command = SelectFile)
SelectButton.place(x=510, y=160, anchor='nw')

def SaveFile():
    filename = SaveFileNameVar.get()
    filepath = os.path.join(CurrentDirectory, filename)
    print(filepath)
    with open(filepath, 'w') as fp:
        file_data = ProcessedFileText.get(1.0,'end')
        fp.write(file_data)
    fp.close()
    print('file saved')

SaveButton = tk.Button(window, text='Save', font=('Arial',12), width=14, height=1, command = SaveFile)
SaveButton.place(x=1200, y=160, anchor='nw')


window.mainloop()
clientSocket.close()
