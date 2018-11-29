# -*- coding:utf-8 -*-

from socket import *

HOST = '127.0.0.1'
PORT = 2000
BUFSIZ = 1024
ADDR = (HOST, PORT)

udpCliSock = socket(AF_INET, SOCK_DGRAM)

udpCliSock.sendto(b'000000', ADDR)

udpCliSock.close()