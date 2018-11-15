# -*- coding:utf-8 -*-

import time
from socket import *
import uu
import pdb
import numpy as np

HOST = '127.0.0.1'
PORT = 21566
BUFSIZ = 1024
ADDR = (HOST, PORT)
DISADDR = (HOST, 21567)
waitTime = 0.1

udpCliSock = socket(AF_INET, SOCK_DGRAM)
udpCliSock.settimeout(waitTime)
udpCliSock.bind(ADDR)

# uu.encode('test.mp4', 'test.txt')
f = open('D:/gitRep/LTFP/test.mp4', 'rb')
data = f.read()

size = len(data)
packagenum = size//1000 + 1

windowSize = 50
windowStart = 0
loseNum = 0
windowEnd = windowStart + windowSize
ackFlag = np.array([0]*windowSize)

udpCliSock.sendto(str(packagenum).encode(), DISADDR)

while windowStart <= packagenum - 1:
    if windowEnd > packagenum - 1:
        windowSize = packagenum - windowStart + 1
    for index in range(windowSize):
        if ackFlag.sum() == windowSize:
            break
        if ackFlag[index] == 0:
            subdata = b''
            Seq = str(windowStart+index)
            while len(Seq) < 8:
                Seq = '0' + Seq
            Seq = Seq.encode()
            if windowStart+index > packagenum - 1:
                subdata = Seq + data[(windowStart+index)*1000:]
            else:
                subdata = Seq + data[(windowStart+index)*1000:((windowStart+index) + 1)*1000]
            udpCliSock.sendto(subdata, DISADDR)
            print(Seq.decode(), packagenum - 1)

    for index in range(windowSize):
        try:
            ack, addr = udpCliSock.recvfrom(BUFSIZ)
        except BaseException as error:
            print('error in package no.', windowStart + index)
            loseNum += 1
        else:
            ackFlag[int(ack[3:])-windowStart] = 1
    if ackFlag.sum() == windowSize:
        windowStart += windowSize
        windowEnd += windowSize
        ackFlag = np.array([0]*windowSize)
        loseNum = 0

udpCliSock.sendto(b'EOF', DISADDR)

udpCliSock.close()