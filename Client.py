# -*- coding:utf-8 -*-

import time
from socket import *
import uu
import pdb

HOST = '127.0.0.1'
PORT = 21566
BUFSIZ = 1024
ADDR = (HOST, PORT)
DISADDR = (HOST, 21567)

udpCliSock = socket(AF_INET, SOCK_DGRAM)
udpCliSock.bind(ADDR)

# uu.encode('test.mp4', 'test.txt')
f = open('D:/gitRep/LTFP/test.mp4', 'rb')
data = f.read()

size = len(data)
packagenum = size//1000 + 1

windowSize = 5
windowStart = 0
windowEnd = windowStart + windowSize

udpCliSock.sendto(str(packagenum).encode(), DISADDR)

for index in range(packagenum):
    subdata = b''
    Seq = str(index)
    while len(Seq) < 8:
        Seq = '0' + Seq
    Seq = Seq.encode()
    if (index + 1)*1000 >= size - 1:
        subdata = Seq + data[index*1000:]
    else:
        subdata = Seq + data[index*1000:(index + 1)*1000]
    udpCliSock.sendto(subdata, DISADDR)
    print(Seq.decode(), index, packagenum - 1)
    ack, addr = udpCliSock.recvfrom(BUFSIZ)

udpCliSock.sendto(b'EOF', DISADDR)

udpCliSock.close()