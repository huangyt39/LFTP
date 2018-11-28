# -*- coding:utf-8 -*-

from socket import *

HOST = '192.168.199.109'
PORT = 21566
BUFSIZ = 1024
ADDR = (HOST, PORT)

udpCliSock = socket(AF_INET, SOCK_DGRAM)
udpCliSock.connect(ADDR)

udpCliSock.sendto(b'000000', ADDR)

udpCliSock.close()