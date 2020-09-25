#!/usr/bin/python
# -*- coding: UTF-8 -*-
# File Name：TCPEchoAppClient.py
# Created: 9/16/2020
# Author: Li Lin & Anika Tasnim
from socket import *
serverName = 'localhost'    #'192.168.0.15'
serverPort = 12000

with socket(AF_INET, SOCK_STREAM) as clientSocket:
    #Setup connection with server
    clientSocket.connect((serverName,serverPort))
    isContinue = True
    while isContinue:
        #Ask user to input message
        message =input('Input lowercase sentence:')

        #Send message to server
        clientSocket.send(message.encode())

        #Receive message from server
        modifiedMessage = clientSocket.recv(1024)
        print('From Server the Sentence in Upper Case:', modifiedMessage.decode())
        messageNum = clientSocket.recv(1024)
        print('From Server number of words in the sentence:', messageNum.decode())
        print('\n')

        #User input confirmation
        while True:
            Yes_No =input('Do you want to send more message? Y/N  ')
            if (Yes_No == 'Y') or (Yes_No == 'y'):
                print('\n')
                break
            elif (Yes_No == 'N') or (Yes_No == 'n'):
                isContinue = False
                break
            else:
                print('Please type Y or N only！\n')

print('Socket closed')
print('Client closed')