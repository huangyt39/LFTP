# -*- coding:utf-8 -*-

import sys
from sender import *
from receiver import *

# data : 'LFTP lget myserver mylargefile'
# data : 'LFTP lsend myserver mylargefile'

def send(hostAddr, dstAddr, filePath):
    sender(hostAddr, dstAddr, filePath, 'server').createSender()

def receive(hostAddr, dstAddr, filePath):
    receiver(hostAddr, dstAddr, filePath, 'server').createReceiver()

if __name__ == "__main__":
    # 服务端监听请求
    hostPort = 21567
    udpSock = socket(AF_INET, SOCK_DGRAM) # 绑定socket
    udpSock.bind(('', hostPort))
    print('Bind udp on', hostPort)

    # 服务端从客户端接收数据
    while 1:
        hostPort += 10
        data, dstAddr = udpSock.recvfrom(MSS)
        temp = data.decode().split(DELIMITER)
        if temp[0] == 'lget':
            Thread(target=send, args=(('', hostPort), dstAddr, temp[1])).start()
        elif temp[0] == 'lsend':
            Thread(target=receive, args=(('', hostPort), dstAddr, temp[1])).start()
