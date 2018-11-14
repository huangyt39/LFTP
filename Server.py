# -*- coding:utf-8 -*-

from socket import *
from time import ctime
import uu
import pdb
import numpy as np

HOST = '127.0.0.1'
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)
DISADDR = (HOST, 21566)

udpSerSock = socket(AF_INET, SOCK_DGRAM)
udpSerSock.bind(ADDR)
print('bind udp on 21567')
data = b''
result = b''

windowSize = 10
windowStart = 0
windowEnd = windowStart + windowSize

packagenum, addr = udpSerSock.recvfrom(BUFSIZ)
packagenum = int(packagenum.decode())
ackFlag = np.zeros(windowSize)
tmpData = np.array([b'']*windowSize)

while windowStart <= packagenum:
    for index in range(windowSize):
        if ackFlag.all():
            break
        data, addr = udpSerSock.recvfrom(BUFSIZ)
        if data == b'EOF':
            break
        Ack = b'ACK' + data[:8]
        udpSerSock.sendto(Ack ,DISADDR)
        if ackFlag[index] == 0:
            ackFlag[index] = 1
            if index == 0 or ackFlag[:index-1].all():
                result += data[8:]
            else:
                tmpData[index] = data[8:]
            print((data[:8]).decode(), packagenum)
    if ackFlag.all():
        # add package into data
        for i in range(windowSize):
            if tmpData[i] != b'':
                result += tmpData[i][8:]
        # clean tmp data
        windowStart += windowSize
        windowEnd += windowSize
        ackFlag = np.zeros(windowSize)
        tmpData = np.array([b'']*windowSize)
    continue

try:
    f = open('D:/gitRep/LTFP/get.mp4', 'wb')
    f.write(result)
except:
    print("error")

udpSerSock.close()