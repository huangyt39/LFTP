# -*- coding:utf-8 -*-

from socket import *

HOST = '119.23.185.176'
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)

udpCliSock = socket(AF_INET, SOCK_DGRAM)
# udpCliSock.bind(ADDR)

udpCliSock.sendto(b'000000', ADDR)

udpCliSock.close()