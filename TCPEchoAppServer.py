#!/usr/bin/python
# -*- coding: UTF-8 -*-
# File Name：TCPEchoAppServer.py
# Created: 9/16/2020
# Author: Li Lin


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
            print('Received:' + message.decode() + ';Length = ' + str(len(message)))
            #Change all letters to Upper case
            modifiedMessage = message.decode().upper()
            #Count the number of received message
            messageNum = 'Received number: ' + str(len(message))

            #Send uppder case letters to Client
            connectionSocket.send(modifiedMessage.encode())
            #Send message number to Client
            connectionSocket.send(messageNum.encode())
