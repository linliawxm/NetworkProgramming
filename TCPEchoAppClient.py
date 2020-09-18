
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# File Name：TCPEchoAppClient.py
# Created: 9/16/2020
# Author: Li Lin

from socket import *
serverName = 'localhost'
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
        print('From Server:', modifiedMessage.decode())
        messageNum = clientSocket.recv(1024)
        print('From Server:', messageNum.decode())

        #User input confirmation
        while True:
            Yes_No =input('Do you want to send more message? Y/N  ')
            if (Yes_No == 'Y') or (Yes_No == 'y'):
                break
            elif (Yes_No == 'N') or (Yes_No == 'n'):
                isContinue = False
                break
            else:
                print('Please type Y or N only！')
