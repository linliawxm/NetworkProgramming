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
import csv

serverPort = 12000

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

serverStarted = False

def StartServerThread():
    global serverStarted
    serverStarted = True
    LoggingText.insert('insert', 'Server Started\n')
    try:
        while True:
            #Create socket with IPv4/TCP type
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversocket:
                #bind with server address and port
                serversocket.bind(('',serverPort))
                #Start to monitor
                serversocket.listen(1)

                #wait for client's connection
                connection,addr = serversocket.accept()
                #print(connection, addr)
                LoggingText.insert('insert', 'connected with {0}:{1}\n'.format(addr[0],addr[1]))
                LoggingText.insert('insert', 'Waiting for request from {}:{}\n'.format(addr[0],addr[1]))
                rcv_thread = threading.Thread(target=ReceiveDataThread, name = 'Thread{}'.format(addr[1]), args=(connection,addr), daemon=True)
                rcv_thread.start()

    except socket.error as msg:
        print(msg)
        LoggingText.insert('insert', 'Server error:{}. Server closed\n'.format(msg))
    else:
        print("Server closed")
        LoggingText.insert('insert', 'Server closed\n')
    serverStarted = False

def UpdateLoggingToEnd():
    while True:
        LoggingText.see('end')
        time.sleep(0.5)

#UpdateLogging_thread = threading.Thread(target=UpdateLoggingToEnd, name = 'UpdateLoggingthread', daemon=True)
#UpdateLogging_thread.start()

def StartServer():
    global serverStarted
    if serverStarted == False:
        start_thread = threading.Thread(target=StartServerThread, name = 'StartServerThread', daemon=True)
        start_thread.start()
    else:
        LoggingText.insert('insert', 'server is already started\n')


StartButton = tk.Button(window, text='Start', font=('Arial',12), width=14, height=4, command = StartServer)
StartButton.place(x=30, y=30, anchor='nw')


#reqtype = ('SEARCH','REPLACE','REVERSE')
def ReceiveDataThread(connection,address):
    isConnected = True
    request = ''
    search_word = ''
    replace_word = ''
    clientIp = address[0]
    clientPort = address[1]
    foldername = str(clientIp)+'_'+str(clientPort)
    isExisting = os.path.exists(foldername)
    if not isExisting:
        os.makedirs(foldername)

    recordFilename = os.path.join('./{}/'.format(foldername), foldername + "record.csv")
    with open(recordFilename,'w') as csv_record:
        csv_write = csv.writer(csv_record)
        csv_head = ['Client','StartTime','RequestType','ReceivedDuration','UnzipDuration','ReadDuration','ProcessDuration','StoreDuration','ZipDuration','ReplyDuration','TotalDuration']
        csv_write.writerow(csv_head)

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

                record = [foldername]

                startTime = datetime.now()
                record.append('\'' + str(startTime))
                reqType = ''
                if message.find('SEARCH+') != -1:
                    reqType = 'Search'
                    LoggingText.insert('insert', '{}:{} Search request received and accepted\n'.format(clientIp,clientPort))
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
                    reqType = 'Replace'
                    LoggingText.insert('insert', '{}:{} Replace request received and accepted\n'.format(clientIp,clientPort))
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
                    reqType = 'Reverse'
                    LoggingText.insert('insert', '{}:{} Reverse request received and accepted\n'.format(clientIp,clientPort))
                    request = 'REVERSE'
                    message = 'Reverse request accepted'
                    connection.send(message.encode())
                    status = 'WAIT_FOR_FILE_INFO'
                elif message == 'EXIT':
                    reqType = 'Exit'
                    LoggingText.insert('insert', '{}:{} Exit request received\n'.format(clientIp,clientPort))
                    connection.close()
                    isConnected = False
                else:
                    reqType = 'Unknown'
                    message ='unrecognized request!'
                record.append(reqType)
            elif (status == 'WAIT_FOR_FILE_INFO'):
                fileinfo_size = struct.calcsize('128sQI')
                fileinfo_data = connection.recv(fileinfo_size)
                if not fileinfo_data:
                    isConnected = False
                    break
                #Receive file name and size info
                filename,filesize,IsCompressed = struct.unpack('128sQI',fileinfo_data) #file name lentgh = 128 bytes; filesize = 8bytes; I:unsigned int for compression
                rcv_file_name = filename.decode('utf-8').strip('\x00')
                LoggingText.insert('insert', '{}:{} Header info received\n'.format(clientIp,clientPort))

                #Receive the data of file
                received_size = 0
                rcvStartTime = datetime.now()
                pre_process_file = os.path.join('./{}/'.format(foldername), rcv_file_name)
                with open(pre_process_file, 'wb') as rcv_file_handle:
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

                rcvEndTime = datetime.now()
                rcvDelta = rcvEndTime - rcvStartTime
                #record.append('\'' + str(rcvDelta))
                record.append('\'' + str(rcvEndTime))

                if isConnected == False:
                    LoggingText.insert('insert', '{}:{} {} file transfer failed\n'.format(clientIp, clientPort, rcv_file_name))
                else:
                    LoggingText.insert('insert', '{}:{} Received all data of {}\n'.format(clientIp, clientPort, rcv_file_name))
                    #Check if the received file is compressed
                    if IsCompressed:
                        upzipStartTime = datetime.now()
                        with zipfile.ZipFile(pre_process_file, 'r') as zf:
                            filepath = zf.extract( zf.namelist()[0], './{}/'.format(foldername)) #suppose only one file
                            pre_process_file = filepath
                        upzipDelta = datetime.now()-upzipStartTime
                        #record.append('\'' + str(upzipDelta))
                        record.append('\'' + str(datetime.now()))
                    else:
                        record.append('None')

                    readStartTime = datetime.now()
                    #Read out the data from file
                    all_data_str = 'No Data'
                    with open(pre_process_file,'rb') as rf:
                        all_data_str = rf.read().decode('utf-8')
                    readDelta = datetime.now()-readStartTime
                    #record.append('\'' + str(readDelta))
                    record.append('\'' + str(datetime.now()))

                    #Write data to GUI ReceivedText field
                    ReceivedText.delete(1.0,'end')
                    ReceivedText.insert('insert',all_data_str)

                    processStartTime = datetime.now()
                    #Process data according to request
                    if request == 'SEARCH':
                        #Search
                        count = all_data_str.count(search_word)
                        processed_data = 'There are {} words "{}" found in {}.'.format(count,search_word,rcv_file_name)
                        processed_file_name = os.path.join('./{}/'.format(foldername), 'SearchResult_' + rcv_file_name)
                    elif request == 'REPLACE':
                        #Replace
                        processed_data = all_data_str.replace(search_word,replace_word)
                        processed_file_name = os.path.join('./{}/'.format(foldername), 'ReplaceResult_' + rcv_file_name)
                    elif request == 'REVERSE':
                        #Reverse
                        data_str_list = all_data_str.split()
                        processed_data = ' '.join(reversed(data_str_list))
                        processed_file_name = os.path.join('./{}/'.format(foldername), 'ReverseResult_' + rcv_file_name)
                    else:
                        processed_data = 'unknown request!'
                        processed_file_name = os.path.join('./{}/'.format(foldername), 'unknowRequest.txt')
                    processDuration = datetime.now()-processStartTime
                    #record.append('\'' + str(processDuration))
                    record.append('\'' + str(datetime.now()))

                    ProcessedText.delete(1.0,'end')
                    ProcessedText.insert('insert',processed_data)

                    storeStartTime = datetime.now()
                    #Store local file
                    with open(processed_file_name, 'wb') as new_file_handle:
                        new_file_handle.write(processed_data.encode())
                    storeDuration = datetime.now() - storeStartTime
                    #record.append('\'' + str(storeDuration))
                    record.append('\'' + str(datetime.now()))

                    #Check if send compressed file
                    if IsCompressedVar.get() == 1:
                        zipStartTime = datetime.now()
                        compressFileName = os.path.join('./{}/'.format(foldername),'Processed.zip')
                        with zipfile.ZipFile(compressFileName, 'w', zipfile.ZIP_DEFLATED) as f:
                            f.write(processed_file_name)
                        filepath = compressFileName
                        processed_file_name = compressFileName
                        filesize = os.stat(compressFileName).st_size
                        zipDuration = datetime.now() - zipStartTime
                        #record.append('\'' + str(zipDuration))
                        record.append('\'' + str(datetime.now()))
                    else:
                        filesize = os.stat(processed_file_name).st_size
                        record.append('None')

                    replyStartTime = datetime.now()
                    with open(processed_file_name, 'rb') as new_file_handle:
                        #Send file info to client
                        fileinfo_size = struct.calcsize('128sQI')    #file name lentgh = 128 bytes; filesize = 8bytes
                        #define file head info, including name and size
                        filename = os.path.basename(processed_file_name)
                        fhead = struct.pack('128sQI', bytes(filename.encode('utf-8')), filesize, IsCompressedVar.get())
                        connection.send(fhead)
                        LoggingText.insert('insert', '{}:{} {} file header info sent\n'.format(clientIp, clientPort, request))
                        #send file data to client
                        send_data = new_file_handle.read()
                        connection.sendall(send_data)
                        LoggingText.insert('insert', '{}:{} {} file send over...\n'.format(clientIp, clientPort, request))
                    replyDuration = datetime.now() - replyStartTime
                    #record.append('\'' + str(replyDuration))
                    record.append('\'' + str(datetime.now()))

                    TotalDuration = datetime.now()-startTime
                    record.append('\'' + str(TotalDuration))

                    with open(recordFilename,'a+') as csv_record:
                        csv_write = csv.writer(csv_record)
                        csv_write.writerow(record)

                    status = 'WAIT_FOR_REQUEST'
            else:
                print('Server is in unknown status')
                status = 'WAIT_FOR_REQUEST'
    LoggingText.insert('insert', '{}：{} Connection closed\n'.format(clientIp,clientPort))



window.mainloop()

