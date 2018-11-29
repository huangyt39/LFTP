# -*- coding:utf-8 -*-

from socket import *
from time import ctime
import uu
import pdb
import numpy as np

# 设置地址 端口号 等待时间
HOST = ''
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)
# 设置Socket
udpSerSock = socket(AF_INET, SOCK_DGRAM)
udpSerSock.bind(ADDR)

# sendSocked
DST = '47.107.126.23'
DSTADDR = (DST, PORT)
sendSock = socket(AF_INET, SOCK_DGRAM)

print('bind udp on 2000')
data = b''
result = b''

packagenum, addr = udpSerSock.recvfrom(BUFSIZ)
packagenum = int(packagenum.decode())
print('recive packet num success')


# 设置窗口大小 
windowSize = 50
windowStart = 0
windowEnd = windowStart + windowSize
ackFlag = np.zeros(windowSize)
tmpData = np.array([b'']*windowSize)

while windowStart <= packagenum - 1:
    if windowEnd > packagenum - 1:
        windowSize = packagenum - windowStart + 1
    print(windowStart , packagenum, windowSize)
    print(ackFlag)
    for index in range(windowSize):
        if ackFlag.sum() == windowSize:
            break
        data, addr = udpSerSock.recvfrom(BUFSIZ)
        #若收到EOF，传输结束
        if data == b'EOF':
            break
        Ack = b'ACK' + data[:8]
        sendSock.sendto(Ack ,DSTADDR)
        if ackFlag[index] == 0:
            ackFlag[index] = 1
            if index == 0 or ackFlag[:index-1].all():
                result += data[8:]
            else:
                tmpData[index] = data[8:]
            print((data[:8]).decode(), packagenum)
    if ackFlag.sum() == windowSize:
        # add package into data
        for i in range(windowSize):
            if tmpData[i] != b'':
                result += tmpData[i][8:]
        # clean tmp data
        windowStart += windowSize
        windowEnd += windowSize
        ackFlag = np.zeros(windowSize)
        tmpData = np.array([b'']*windowSize)

try:
    f = open('./get.mp4', 'wb')
    f.write(result)
except:
    print("error")

udpSerSock.close()
