# -*- coding:utf-8 -*-

import time
from socket import *
import uu
import pdb
import numpy as np
import sys

# 设置地址 端口号 等待时间
HOST = '119.23.185.176'
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)
DISADDR = (HOST, 21567)
waitTime = 0.1

# 设置Socket
udpCliSock = socket(AF_INET, SOCK_DGRAM)
udpCliSock.settimeout(waitTime) #设置等待时间
# udpCliSock.bind(ADDR)

try:
    udpCliSock.connect((HOST,PORT))
except Exception as e:
    print('server not find or not open')
    sys.exit()

# 读入要传输的文件
f = open('./test.mp4', 'rb')
data = f.read()

# 每个package1000字节
size = len(data)
packagenum = size//1000 + 1

# 设置窗口大小 
windowSize = 50
windowStart = 0
loseNum = 0
windowEnd = windowStart + windowSize
ackFlag = np.array([0]*windowSize) #用于判断窗口中第包是否被确认

udpCliSock.sendto(str(packagenum).encode(), DISADDR)

#移动窗口
while windowStart <= packagenum - 1:
    # 判断窗口尾是否超过包尾
    if windowEnd > packagenum - 1:
        windowSize = packagenum - windowStart + 1
    for index in range(windowSize):
        # 若被确认的包数等于窗口大小，移动窗口
        if ackFlag.sum() == windowSize:
            break
        if ackFlag[index] == 0:
            subdata = b''
            # 在包头加入包号
            Seq = str(windowStart+index)
            # 补齐8位
            while len(Seq) < 8:
                Seq = '0' + Seq
            Seq = Seq.encode()
            if windowStart+index > packagenum - 1:
                subdata = Seq + data[(windowStart+index)*1000:]
            else:
                subdata = Seq + data[(windowStart+index)*1000:((windowStart+index) + 1)*1000]
            udpCliSock.sendto(subdata, DISADDR)
            print(Seq.decode(), packagenum - 1)

    # 接受Ack 若接收不到打印错误信息
    for index in range(windowSize):
        try:
            ack, addr = udpCliSock.recvfrom(BUFSIZ)
        except BaseException as error:
            print('error in package no.', windowStart + index)
            loseNum += 1
        else:
            ackFlag[int(ack[3:])-windowStart] = 1

    # 若被确认的包数等于窗口大小，移动窗口 重置
    if ackFlag.sum() == windowSize:
        windowStart += windowSize
        windowEnd += windowSize
        ackFlag = np.array([0]*windowSize)
        loseNum = 0

#传输EOF 传输结束
udpCliSock.sendto(b'EOF', DISADDR)

udpCliSock.close()