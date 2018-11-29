# -*- coding:utf-8 -*-

from socket import *

HOST = ''
PORT = 2000
BUFSIZ = 1024
ADDR = (HOST, PORT)
DISADDR = (HOST, 21567)

udpSerSock = socket(AF_INET, SOCK_DGRAM)
udpSerSock.bind(ADDR)

packagenum, addr = udpSerSock.recvfrom(BUFSIZ)

print(packagenum)

udpSerSock.close()