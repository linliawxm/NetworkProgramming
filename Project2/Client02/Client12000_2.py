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
import csv
import lzma

serverName = '192.168.0.15'    #'192.168.0.15'
serverPort = 12000

# recordHeader = ['Start', 'Request', 'OrgSize','ZipSize', 'SendDelta','TotalDelta']
# with open('record.txt','w') as f:
#     itemName = " ".join([str(elem) for elem in recordHeader])
#     f.write(itemName)
# recordFilename = "record.csv"
# with open(recordFilename,'w') as csv_record:
#     csv_write = csv.writer(csv_record)
#     csv_head = ['Start', 'Request', 'OrgSize','ZipSize', 'zipDuration','SendDuration','ReceiveDuration','TotalDuration']
#     csv_write.writerow(csv_head)

CurrentDirectory = os.getcwd()
appName = 'Client02'
#Create main GUI window
window = tk.Tk()
#Set widnow's title
window.title(appName)
#Set window width and height
window.geometry('1305x650')

isConnected = False

#Create a Entry
SearchWordVar = tk.StringVar()
SearchWordEntry = tk.Entry(window, show=None, font=('Arial',14), width = 12, textvariable=SearchWordVar)
SearchWordEntry.place(x=150, y=80, anchor='nw')
SearchWordVar.set('Alice')

ReplaceWordVar = tk.StringVar()
ReplaceWordEntry = tk.Entry(window, show=None, font=('Arial',14), width = 12, textvariable=ReplaceWordVar)
ReplaceWordEntry.place(x=300, y=80, anchor='nw')
ReplaceWordVar.set(appName)

SourceFilePathVar = tk.StringVar()
SourceFilePathEntry = tk.Entry(window, show=None, font=('Arial',14), width = 44, textvariable=SourceFilePathVar)
SourceFilePathEntry.place(x=10, y=160, anchor='nw')
SourceFilePathVar.set('C:/GitHubProject/NetworkProgramming/Project2/{}/alice.txt'.format(appName))

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

#UpdateLogging_thread = threading.Thread(target=UpdateLoggingToEnd, name = 'UpdateLoggingthread', daemon=True)
#UpdateLogging_thread.start()

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

def RequestThread(ReqType,ReqMsg):
    global isConnected
    record = []
    if isConnected:
        startTime = datetime.now()
        record.append('\'' + str(startTime))
        record.append(ReqType)
        try:
            #Send request to server
            clientSocket.send(ReqMsg.encode())
        except socket.error as msg:
            now = str(datetime.now())[:-7]
            LoggingText.insert('insert','{0}: Server Connected failed({1})\n'.format(now,msg))
            isConnected = False
        else:
            LoggingText.insert('insert','{} request sent\n'.format(ReqType))
            #Receive message from server
            response = clientSocket.recv(1024)
            if response:
                LoggingText.insert('insert', 'Response from server: {0} \n'.format(response.decode('utf-8')))
                expectedResponse = '{} request accepted'.format(ReqType)
                if response.decode() == expectedResponse:
                    filepath = SourceFilePathVar.get()
                    filename = os.path.basename(filepath)
                    filesize = os.stat(filepath).st_size
                    record.append(filesize)
                    if os.path.isfile(filepath):

                        if IsCompressedVar.get() == 1:
                            zipStartTime = datetime.now()
                            #Zipfile compression
                            # zipfilename = filename.split('.')[0] + '.zip'
                            # with zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED) as f:
                            #     f.write(filename)
                            #lzma compression
                            zipfilename = filename.split('.')[0] + '.xz'
                            with lzma.open(zipfilename, 'wb') as f:
                                with open(filename,'rb') as pf:
                                    textContent = pf.read()
                                f.write(textContent)
                            filepath = zipfilename
                            filename = zipfilename
                            filesize = os.stat(filepath).st_size
                            record.append(filesize)
                            zipDuration = datetime.now()-zipStartTime
                            record.append('\'' + str(zipDuration))
                        else:
                            record.append('None')
                            record.append(0)

                        #Send file info to server
                        #Header structure : file name lentgh = 128 bytes; filesize = 8bytes; IsCompressed = 4bytes(int)
                        fhead = struct.pack('128sQI', bytes(filename.encode('utf-8')), filesize, IsCompressedVar.get())
                        clientSocket.send(fhead)
                        LoggingText.insert('insert', '{} file header sent\n'.format(ReqType))

                        sendStartTime = datetime.now()
                        #Send data to server
                        with open(filepath, 'rb') as fp:
                            data = fp.read()
                            clientSocket.sendall(data)
                            LoggingText.insert('insert', '{} file send over...\n'.format(ReqType))
                        sendoverTime = datetime.now()
                        sendoverDetal = sendoverTime - sendStartTime
                        record.append('\'' + str(sendoverDetal))

                        LoggingText.insert('insert', 'Waiting for server processing and feedback\n')

                        rcvStartTime = datetime.now()
                        #4. Receive the processed result
                        fileinfo_size = struct.calcsize('128sQI')
                        fileinfo_data = clientSocket.recv(fileinfo_size)

                        if fileinfo_data:
                            filename,filesize,IsCompressed = struct.unpack('128sQI',fileinfo_data)
                            rcv_file_name = filename.decode('utf-8').strip('\x00')
                            LoggingText.insert('insert', 'Processed file header info is received for {}\n'.format(ReqType))

                            received_size = 0
                            with open(rcv_file_name, 'wb') as rcv_file_handle:
                                while not (received_size == filesize):
                                    if(filesize - received_size > 4096):
                                        data = clientSocket.recv(4096)
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
                            LoggingText.insert('insert', 'Processed file for {} is received\n'.format(ReqType))

                            reverseoverDetal = datetime.now() - rcvStartTime
                            record.append('\'' + str(reverseoverDetal))
                            if isConnected:
                                if IsCompressed:
                                    LoggingText.insert('insert', 'Processed file for {} was compressed\n'.format(ReqType))
                                    unzipStartTime = datetime.now()
                                    # with zipfile.ZipFile(rcv_file_name, 'r') as zf:
                                    #     filepath = zf.extract(zf.namelist()[0]) #suppose only one file
                                    #     #rcv_file_name = os.path.basename(filepath)
                                    #     rcv_file_name = filepath
                                    with lzma.open(rcv_file_name, 'rb') as f:
                                        zipContent = f.read()
                                        localFileName = 'ReceivedProcessedFor{}.txt'.format(ReqType)
                                        with open(localFileName,'w') as uf:
                                            uf.write(zipContent.decode("utf-8"))
                                        #Dsiplay partial content in GUI
                                        ProcessedFileText.delete(1.0,'end')
                                        ProcessedFileText.insert('insert', zipContent.decode("utf-8")[0:1000])
                                    unzipDuration = datetime.now() - unzipStartTime
                                    record.append('\'' + str(unzipDuration))
                                    LoggingText.insert('insert', 'Processed file for {} is decompressed\n'.format(ReqType))
                                else:
                                    record.append(0)

                                total_duration = datetime.now() - startTime
                                record.append('\'' + str(total_duration))

                                #with open(rcv_file_name,'rb') as rf:
                                #    all_data_str = rf.read().decode('utf-8')

                                #LoggingText.insert('insert', 'Processed file is stored locally\n')
                                #5. Display the replaced result
                                #ProcessedFileText.delete(1.0,'end')
                                #ProcessedFileText.insert('insert', all_data_str[0:2000])

                                #ProcessedFileText.insert('insert', 'Processed data received')
                            else:
                                LoggingText.insert('insert', 'No connection! Please connect firstly\n')
                    else:
                        LoggingText.insert('insert','The file path is not valid')
            else:
                isConnected = False
                LoggingText.insert('insert', 'No connection! Please connect firstly\n')
    else:
        LoggingText.insert('insert', 'No connection! Please connect firstly\n')
    print('Request thread for {} ended'.format(ReqType))
    with open('record.csv','a+') as csv_record:
        csv_write = csv.writer(csv_record)
        csv_write.writerow(record)

def SearchWordFromServer():
    ReqType = 'Search'
    search_word = SearchWordVar.get()
    ReqMsg = 'SEARCH+' + search_word
    search_thread = threading.Thread(target=RequestThread, name='RequestThread', args=(ReqType,ReqMsg), daemon=True)
    #search_thread.setDaemon(True)
    search_thread.start()
    print('RequestThread started for Search function')

SearchButton = tk.Button(window, text='Search', font=('Arial',12), width=14, height=2, command = SearchWordFromServer)
SearchButton.place(x=150, y=5, anchor='nw')

def ReplaceWordByServer():
    ReqType = 'Replace'
    search_word = SearchWordVar.get()
    replace_word = ReplaceWordVar.get()
    ReqMsg = 'REPLACE+' + search_word +'+' + replace_word

    replace_thread = threading.Thread(target=RequestThread, name='RequestThread', args=(ReqType,ReqMsg), daemon=True)
    #replace_thread.setDaemon(True)
    replace_thread.start()
    print('RequestThread started for Replace function')

ReplaceButton = tk.Button(window, text='Replace', font=('Arial',12), width=14, height=2, command = ReplaceWordByServer)
ReplaceButton.place(x=300, y=5, anchor='nw')

def ReverseWordByServer():
    ReqType = 'Reverse'
    ReqMsg = 'REVERSE'
    reverse_thread = threading.Thread(target=RequestThread, name='RequestThread', args=(ReqType,ReqMsg), daemon=True)
    #reverse_thread.setDaemon(True)
    reverse_thread.start()
    print('RequestThread started for Reverse function')

ReverseButton = tk.Button(window, text='Reverse', font=('Arial',12), width=14, height=2, command = ReverseWordByServer)
ReverseButton.place(x=450, y=5, anchor='nw')

def SelectFile():
    SourceFilePath = filedialog.askopenfilename(title='Select source file', filetypes=[("Text files", "*.txt"), ("all files", "*.*")])
    SourceFilePathEntry.delete(0,tk.END)
    SourceFilePathEntry.insert(0,SourceFilePath)
    with open(SourceFilePathVar.get(),'rb') as reader:
        SourceFileText.delete(1.0,'end')
        text = reader.read()
        #print(len(text))
        SourceFileText.insert('insert',text[0:1000])

SelectButton = tk.Button(window, text='Source path...', font=('Arial',12), width=12, height=1, command = SelectFile)
SelectButton.place(x=510, y=157, anchor='nw')

#callback function for Save button
def SaveFile():
    filename = SaveFileNameVar.get()
    filepath = os.path.join(CurrentDirectory, filename)
    #print(filepath)
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
