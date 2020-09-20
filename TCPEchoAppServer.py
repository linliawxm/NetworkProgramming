#!/usr/bin/python
# -*- coding: UTF-8 -*-
# File Name：TCPEchoAppServer.py
# Created: 9/16/2020
# Author: Li Lin & Anika Tasnim


from socket import *

serverPort = 12000

with socket(AF_INET, SOCK_STREAM) as serverSocket:
    #bind with server address and port
    serverSocket.bind(('',serverPort))
    #Start to monitor
    serverSocket.listen(1)
    print('The server is ready to receive...')
    #wait for client's connection
    connectionSocket,addr = serverSocket.accept()

    with connectionSocket:
        while True:
            #Receive message from client
            message = connectionSocket.recv(1024)

            #Check if empty message
            if not message:
                break
            #seperating the words by using split functions
            words = message.split()
            #counting the number of words
            count = len(words)
            print('Received:' + message.decode() + ' ;Number of Words = ' + str(count) + '\n')
            #Change all letters to Upper case
            modifiedMessage = message.decode().upper()
            #Count the number of words from received message
            messageNum = str(count)
            #Send uppder case letters to Client
            connectionSocket.send(modifiedMessage.encode())
            #Send word number to Client
            connectionSocket.send(messageNum.encode())
    print('Connection closed')
print('Socket closed')
print('Server closed')

