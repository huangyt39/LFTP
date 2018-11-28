# -*- coding:utf-8 -*-

from socket import *

HOST = '47.107.126.23'
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)
DISADDR = (HOST, 21567)

udpSerSock = socket(AF_INET, SOCK_DGRAM)
udpSerSock.bind((HOST,PORT))

packagenum, addr = udpSerSock.recvfrom(BUFSIZ)

print(packagenum)

udpSerSock.close()