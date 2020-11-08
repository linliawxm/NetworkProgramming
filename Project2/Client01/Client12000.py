#!/usr/bin/python
# -*- coding: UTF-8 -*-
# File Name：Client.py
# Created: 9/16/2020
# Author: Li Lin & Anika Tasnim
import socket
import tkinter as tk
from tkinter import filedialog
from  tkinter  import ttk
import tkinter.scrolledtext as ScrolledText
import os
import sys
import struct
import threading
import win32api
from datetime import datetime
import time
import zipfile

serverName = 'localhost'    #'192.168.0.15'
serverPort = 12000

# recordHeader = ['Start', 'Request', 'OrgSize','ZipSize', 'SendDelta','TotalDelta']
# with open('record.txt','w') as f:
#     itemName = " ".join([str(elem) for elem in recordHeader])
#     f.write(itemName)

CurrentDirectory = os.getcwd()

#Create main GUI window
window = tk.Tk()
#Set widnow's title
window.title('Client')
#Set window width and height
window.geometry('1305x650')

isConnected = False

#Create a Entry
SearchWordVar = tk.StringVar()
SearchWordEntry = tk.Entry(window, show=None, font=('Arial',14), width = 12, textvariable=SearchWordVar)
SearchWordEntry.place(x=150, y=80, anchor='nw')
SearchWordVar.set('Mobile')

ReplaceWordVar = tk.StringVar()
ReplaceWordEntry = tk.Entry(window, show=None, font=('Arial',14), width = 12, textvariable=ReplaceWordVar)
ReplaceWordEntry.place(x=300, y=80, anchor='nw')
ReplaceWordVar.set('iPhone')

SourceFilePathVar = tk.StringVar()
SourceFilePathEntry = tk.Entry(window, show=None, font=('Arial',14), width = 44, textvariable=SourceFilePathVar)
SourceFilePathEntry.place(x=10, y=160, anchor='nw')
SourceFilePathVar.set('C:/GitHubProject/NetworkProgramming/Project1/Mobile IP wiki.txt')

SaveFileNameVar = tk.StringVar()
SaveFileNameEntry = tk.Entry(window, show=None, font=('Arial',14), width = 15, textvariable=SaveFileNameVar)
SaveFileNameEntry.place(x=1000, y=194, anchor='nw')
SaveFileNameVar.set('output.txt')

#Label
LogLabel = tk.Label(window, text='Log')
LogLabel.place(x=650, y=10, anchor='nw')

SourceLabel = tk.Label(window, text='Source file')
SourceLabel.place(x=20, y=210, anchor='nw')

ReceivedLabel = tk.Label(window, text='Received from server')
ReceivedLabel.place(x=670, y=210, anchor='nw')

SearchLabel = tk.Label(window, text='Search word')
SearchLabel.place(x=150, y=59, anchor='nw')

ReplaceLabel = tk.Label(window, text='Replace word')
ReplaceLabel.place(x=300, y=59, anchor='nw')

SaveLabel = tk.Label(window, text='Save file name')
SaveLabel.place(x=1000, y=173, anchor='nw')

#Add check button
IsCompressedVar = tk.IntVar()
checkButton = tk.Checkbutton(window, text='File compression enable',variable=IsCompressedVar, onvalue=1, offvalue=0)
checkButton.place(x=150, y=120, anchor='nw')

#Create Text
SourceFileText = ScrolledText.ScrolledText(window, height=30, width = 88)
SourceFileText.place(x=10, y=230, anchor='nw')
if os.path.isfile(SourceFilePathVar.get()):
    with open(SourceFilePathVar.get(),'rb') as reader:
        SourceFileText.delete(1.0,'end')
        text = reader.read()
        SourceFileText.insert('insert',text)

ProcessedFileText = ScrolledText.ScrolledText(window, height=30, width = 90)
ProcessedFileText.place(x=650, y=230, anchor='nw')

LoggingText = ScrolledText.ScrolledText(window, height=10, width = 90)
LoggingText.place(x=650, y=40, anchor='nw')

#update text to show end content
def UpdateLoggingToEnd():
    while True:
        LoggingText.see('end')
        time.sleep(0.5)

UpdateLogging_thread = threading.Thread(target=UpdateLoggingToEnd, name = 'UpdateLoggingthread', daemon=True)
if not UpdateLogging_thread.is_alive():
    UpdateLogging_thread.start()

#Socket created
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Create buttons
def ConnectServer():
    global isConnected
    if not isConnected:
        try:
            #Setup connection with server
            clientSocket.connect((serverName,serverPort))
        except socket.error as msg:
            now = str(datetime.now())[:-7]
            LoggingText.insert('insert','{0}: Server Connected failed({1})\n'.format(now,msg))
        else:
            isConnected = True
            now = str(datetime.now())[:-7]
            LoggingText.insert('insert','{0}: Server Connected\n'.format(now))
    else:
        LoggingText.insert('insert','Server already Connected )\n')

ConnectButton = tk.Button(window, text='Connect', font=('Arial',12), width=10, height=2, command = ConnectServer)
ConnectButton.place(x=10, y=10, anchor='nw')


def ExitThread():
    global isConnected
    if isConnected:
        request = 'EXIT'
        clientSocket.send(request.encode())
        LoggingText.insert('insert','Exit request sent to server\n')
        clientSocket.close()
    else:
        LoggingText.insert('insert','No connection\n')
    window.destroy()

def ExitProcess():
    exit_thread = threading.Thread(target=ExitThread, name='ExitThread')
    exit_thread.setDaemon(True)
    exit_thread.start()
    print('Exit threading started')

ExitButton = tk.Button(window, text='Exit', font=('Arial',12), width=10, height=2, command = ExitProcess)
ExitButton.place(x=10, y=70, anchor='nw')

def SearchThread():
    global isConnected
    record = []
    if isConnected:
        startTime = datetime.now()
        record.append(startTime)
        #1.Send request to server
        search_word = SearchWordVar.get()

        request = 'SEARCH+' + search_word
        record.append('Search')
        try:
            clientSocket.send(request.encode())
        except socket.error as msg:
            now = str(datetime.now())[:-7]
            LoggingText.insert('insert','{0}: Server Connected failed({1})\n'.format(now,msg))
            isConnected = False
        else:
            LoggingText.insert('insert','Search request sent with search word "{0}"\n'.format(search_word))
            #Receive reply from server
            response = clientSocket.recv(1024)
            if response:
                LoggingText.insert('insert', 'Response from server: {0} \n'.format(response.decode('utf-8')))
                if response.decode() == 'Search request accepted':
                    filepath = SourceFilePathVar.get()
                    filename = os.path.basename(filepath)
                    filesize = os.stat(filepath).st_size
                    record.append(filesize)
                    print('Source file size:{}'.format(filesize))
                    if os.path.isfile(filepath):
                        #2. Send file info to server
                        fileinfo_size = struct.calcsize('128sQI')    #file name lentgh = 128 bytes; filesize = 8bytes; I:unsigned int for compression
                        #define file head info, including name and size
                        if IsCompressedVar.get() == 1:
                            with zipfile.ZipFile('Search.zip', 'w', zipfile.ZIP_DEFLATED) as f:
                                f.write(filename)
                            filepath = 'Search.zip'
                            filename = 'Search.zip'
                            filesize = os.stat('Search.zip').st_size
                            record.append(filesize)
                            print('Compressed file size:{}'.format(filesize))
                        else:
                            record.append('None')
                        fhead = struct.pack('128sQI', bytes(filename.encode('utf-8')), filesize, IsCompressedVar.get())
                        clientSocket.send(fhead)
                        LoggingText.insert('insert', 'Search file header sent\n')

                        sendStartTime = datetime.now()
                        with open(filepath, 'rb') as fp:
                            data = fp.read()
                            #3. Send data to server
                            clientSocket.sendall(data)
                            LoggingText.insert('insert', 'Search file send over...\n')

                        sendoverTime = datetime.now()
                        sendoverDetal = sendoverTime - sendStartTime
                        record.append(sendoverDetal)

                        #4. Receive the search result
                        response = clientSocket.recv(1024)
                        if response:
                            #5. Display the search result
                            LoggingText.insert('insert', 'Search result received\n')
                            ProcessedFileText.delete(1.0,'end')
                            ProcessedFileText.insert('insert',response.decode())
                        else:
                            isConnected = False
                            LoggingText.insert('insert', 'Server connection closed! Please check if server is still running\n')
                        searchoverTime = datetime.now()
                        searchoverDetal = searchoverTime - sendStartTime
                        record.append(searchoverDetal)
                    else:
                        LoggingText.insert('insert','The file path is not valid')
            else:
                isConnected = False
                LoggingText.insert('insert', 'Server connection closed! Please check if server is still running\n')
    else:
        LoggingText.insert('insert', 'No connection! Please connect firstly\n')
    print('Search threading ended')

    with open('Record.txt','a') as f:
        recordValue = " ".join([str(elem) for elem in record])
        f.write(recordValue)
        f.write('\n')

def ReplaceThread():
    global isConnected
    record = []
    if isConnected:
        startTime = datetime.now()
        record.append(startTime)
        #1.Send request to server
        search_word = SearchWordVar.get()
        replace_word = ReplaceWordVar.get()
        record.append('Replace')
        request = 'REPLACE+' + search_word +'+' + replace_word
        try:
            clientSocket.send(request.encode())
        except socket.error as msg:
            now = str(datetime.now())[:-7]
            LoggingText.insert('insert','{0}: Server Connected failed({1})\n'.format(now,msg))
            isConnected = False
        else:
            LoggingText.insert('insert','Replace request sent with  search word "{0}" and replace word "{1}"\n'.format(search_word,replace_word))

            #Receive message from server
            response = clientSocket.recv(1024)
            if response:
                LoggingText.insert('insert', 'Response from server: {0} \n'.format(response.decode('utf-8')))
                if response.decode() == 'Replace request accepted':
                    filepath = SourceFilePathVar.get()
                    filename = os.path.basename(filepath)
                    filesize = os.stat(filepath).st_size
                    record.append(filesize)
                    if os.path.isfile(filepath):
                        #2. Send file info to server
                        fileinfo_size = struct.calcsize('128sQI')    #file name lentgh = 128 bytes; filesize = 8bytes;IsCompressed = 4bytes(int)
                        #define file head info, including name and size
                        if IsCompressedVar.get() == 1:
                            with zipfile.ZipFile('Replace.zip', 'w', zipfile.ZIP_DEFLATED) as f:
                                f.write(filename)
                            filepath = 'Replace.zip'
                            filename = 'Replace.zip'
                            filesize = os.stat('Replace.zip').st_size
                            record.append(filesize)
                        else:
                            record.append('None')
                        fhead = struct.pack('128sQI', bytes(filename.encode('utf-8')), filesize, IsCompressedVar.get())
                        clientSocket.send(fhead)
                        LoggingText.insert('insert', 'Replace file header sent\n')

                        sendStartTime = datetime.now()
                        #3. Send data to server
                        with open(filepath, 'rb') as fp:
                            data = fp.read()
                            clientSocket.sendall(data)
                            LoggingText.insert('insert', 'Replace file send over...\n')
                        sendoverTime = datetime.now()
                        sendoverDetal = sendoverTime - sendStartTime
                        record.append(sendoverDetal)
                        #4. Receive the replace result
                        fileinfo_size = struct.calcsize('128sQI')
                        fileinfo_data = clientSocket.recv(fileinfo_size)

                        if fileinfo_data:
                            filename,filesize,IsCompressed = struct.unpack('128sQI',fileinfo_data)
                            rcv_file_name = filename.decode('utf-8').strip('\x00')
                            LoggingText.insert('insert', '{0} header info is received and size is {1} bytes\n'.format(rcv_file_name,filesize))

                            received_size = 0
                            with open(rcv_file_name, 'wb') as rcv_file_handle:
                                while not (received_size == filesize):
                                    if(filesize - received_size > 1024):
                                        data = clientSocket.recv(1024)
                                        if data:
                                            received_size += len(data)
                                        else:
                                            isConnected = False
                                            break
                                    else:
                                        data = clientSocket.recv(filesize - received_size)
                                        if data:
                                            received_size = filesize
                                        else:
                                            isConnected = False
                                            break
                                    rcv_file_handle.write(data)

                            replaceoverTime = datetime.now()
                            replaceoverDetal = replaceoverTime - sendStartTime
                            record.append(replaceoverDetal)

                            if isConnected:
                                if IsCompressed:
                                    with zipfile.ZipFile(rcv_file_name, 'r') as zf:
                                        filepath = zf.extract(zf.namelist()[0]) #suppose only one file
                                        rcv_file_name = os.path.basename(filepath)
                                        print(rcv_file_name)

                                with open(rcv_file_name,'rb') as rf:
                                    all_data_str = rf.read().decode('utf-8')

                                LoggingText.insert('insert', 'Replaced file {0} is received\n'.format(rcv_file_name))
                                #5. Display the replaced result
                                ProcessedFileText.delete(1.0,'end')
                                ProcessedFileText.insert('insert', all_data_str)
                            else:
                                LoggingText.insert('insert', 'Server connection closed! Please check if server is still running\n')
                    else:
                        LoggingText.insert('insert', 'The file path is not valid\n')
                else:
                    isConnected = False
                    LoggingText.insert('insert', 'Server connection closed! Please check if server is still running\n')
    else:
        LoggingText.insert('insert', 'No connection! Please connect firstly\n')
    print('Replace threading ended')
    with open('Record.txt','a') as f:
        recordValue = " ".join([str(elem) for elem in record])
        f.write(recordValue)
        f.write('\n')
def ReverseThread():
    global isConnected
    record = []
    if isConnected:
        startTime = datetime.now()
        record.append(startTime)
        #1.Send request to server
        request = 'REVERSE'
        record.append('Reverse')
        try:
            clientSocket.send(request.encode())
        except socket.error as msg:
            now = str(datetime.now())[:-7]
            LoggingText.insert('insert','{0}: Server Connected failed({1})\n'.format(now,msg))
            isConnected = False
        else:
            LoggingText.insert('insert','Reverse request sent\n')
            #Receive message from server
            response = clientSocket.recv(1024)
            if response:
                LoggingText.insert('insert', 'Response from server: {0} \n'.format(response.decode('utf-8')))
                if response.decode() == 'Reverse request accepted':
                    filepath = SourceFilePathVar.get()
                    filename = os.path.basename(filepath)
                    filesize = os.stat(filepath).st_size
                    record.append(filesize)
                    if os.path.isfile(filepath):
                        #2. Send file info to server
                        fileinfo_size = struct.calcsize('128sQI')    #file name lentgh = 128 bytes; filesize = 8bytes;IsCompressed = 4bytes(int)
                        #define file head info, including name and size
                        if IsCompressedVar.get() == 1:
                            with zipfile.ZipFile('Reverse.zip', 'w', zipfile.ZIP_DEFLATED) as f:
                                f.write(filename)
                            filepath = 'Reverse.zip'
                            filename = 'Reverse.zip'
                            filesize = os.stat('Reverse.zip').st_size
                            record.append(filesize)
                        else:
                            record.append('None')
                        fhead = struct.pack('128sQI', bytes(filename.encode('utf-8')), filesize, IsCompressedVar.get())
                        clientSocket.send(fhead)
                        LoggingText.insert('insert', 'Reverse file header sent\n')

                        sendStartTime = datetime.now()
                        #3. Send data to server
                        with open(filepath, 'rb') as fp:
                            data = fp.read()
                            clientSocket.sendall(data)
                            LoggingText.insert('insert', 'Reverse file send over...\n')
                        sendoverTime = datetime.now()
                        sendoverDetal = sendoverTime - sendStartTime
                        record.append(sendoverDetal)
                        #4. Receive the reversed result
                        fileinfo_size = struct.calcsize('128sQI')
                        fileinfo_data = clientSocket.recv(fileinfo_size)

                        if fileinfo_data:
                            filename,filesize,IsCompressed = struct.unpack('128sQI',fileinfo_data)
                            rcv_file_name = filename.decode('utf-8').strip('\x00')
                            LoggingText.insert('insert', '{0} header info is received and size is {1} bytes\n'.format(rcv_file_name,filesize))

                            received_size = 0
                            with open(rcv_file_name, 'wb') as rcv_file_handle:
                                while not (received_size == filesize):
                                    if(filesize - received_size > 1024):
                                        data = clientSocket.recv(1024)
                                        if data:
                                            received_size += len(data)
                                        else:
                                            isConnected = False
                                            break
                                    else:
                                        data = clientSocket.recv(filesize - received_size)
                                        if data:
                                            received_size = filesize
                                        else:
                                            isConnected = False
                                            break
                                    rcv_file_handle.write(data)
                            reverseoverTime = datetime.now()
                            reverseoverDetal = reverseoverTime - sendStartTime
                            record.append(reverseoverDetal)
                            if isConnected:
                                if IsCompressed:
                                    with zipfile.ZipFile(rcv_file_name, 'r') as zf:
                                        filepath = zf.extract(zf.namelist()[0]) #suppose only one file
                                        rcv_file_name = os.path.basename(filepath)
                                        print(rcv_file_name)

                                with open(rcv_file_name,'rb') as rf:
                                    all_data_str = rf.read().decode('utf-8')

                                LoggingText.insert('insert', 'Reversed file is received\n')
                                #5. Display the replaced result
                                ProcessedFileText.delete(1.0,'end')
                                ProcessedFileText.insert('insert', all_data_str)
                            else:
                                LoggingText.insert('insert', 'No connection! Please connect firstly\n')
                    else:
                        LoggingText.insert('insert','The file path is not valid')
            else:
                isConnected = False
                LoggingText.insert('insert', 'No connection! Please connect firstly\n')
    else:
        LoggingText.insert('insert', 'No connection! Please connect firstly\n')
    print('Reverse threading ended')
    with open('Record.txt','a') as f:
        recordValue = " ".join([str(elem) for elem in record])
        f.write(recordValue)
        f.write('\n')
        
def SearchWordFromServer():
    search_thread = threading.Thread(target=SearchThread, name='SearchThread')
    search_thread.setDaemon(True)
    search_thread.start()
    print('Search threading started')

SearchButton = tk.Button(window, text='Search', font=('Arial',12), width=14, height=2, command = SearchWordFromServer)
SearchButton.place(x=150, y=5, anchor='nw')

def ReplaceWordByServer():
    replace_thread = threading.Thread(target=ReplaceThread, name='replace_thread')
    replace_thread.setDaemon(True)
    replace_thread.start()
    print('Replace threading started')

ReplaceButton = tk.Button(window, text='Replace', font=('Arial',12), width=14, height=2, command = ReplaceWordByServer)
ReplaceButton.place(x=300, y=5, anchor='nw')

def ReverseWordByServer():
    reverse_thread = threading.Thread(target=ReverseThread, name='reverse_thread')
    reverse_thread.setDaemon(True)
    reverse_thread.start()
    print('Reverse threading started')

ReverseButton = tk.Button(window, text='Reverse', font=('Arial',12), width=14, height=2, command = ReverseWordByServer)
ReverseButton.place(x=450, y=5, anchor='nw')

def SelectFile():
    SourceFilePath = filedialog.askopenfilename(title='Select source file', filetypes=[("Text files", "*.txt"), ("all files", "*.*")])
    SourceFilePathEntry.delete(0,tk.END)
    SourceFilePathEntry.insert(0,SourceFilePath)
    with open(SourceFilePathVar.get(),'rb') as reader:
        SourceFileText.delete(1.0,'end')
        text = reader.read()
        print(len(text))
        SourceFileText.insert('insert',text)

SelectButton = tk.Button(window, text='Source path...', font=('Arial',12), width=12, height=1, command = SelectFile)
SelectButton.place(x=510, y=157, anchor='nw')

#callback function for Save button
def SaveFile():
    filename = SaveFileNameVar.get()
    filepath = os.path.join(CurrentDirectory, filename)
    print(filepath)
    with open(filepath, 'w') as fp:
        file_data = ProcessedFileText.get(1.0,'end')
        fp.write(file_data)
    fp.close()
    LoggingText.insert('end', 'File {0} saved under {1}\n'.format(filename,CurrentDirectory))
#Create Save button
SaveButton = tk.Button(window, text='Save', font=('Arial',12), width=10, height=1, command = SaveFile)
SaveButton.place(x=1175, y=190, anchor='nw')


window.mainloop()
clientSocket.close()
