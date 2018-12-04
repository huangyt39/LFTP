# -*- coding:utf-8 -*-

import sys
from sender import *
from receiver import *

# data : 'LFTP lget myserver mylargefile'
# data : 'LFTP lsend myserver mylargefile'

def send(dstAddr, filePath):
    sender = sender(dstAddr, filePath, 'server')
    sender.createSender()

def receive(hostAddr, dstAddr, filePath):
    receiver = receiver(hostAddr, dstAddr, filePath, 'server')
    receiver.createReceiver()

if __name__ == "__main__":
    # 服务端监听请求
    hostPort = 21567  # 指定服务端的监听端口
    hostAddr = ('', hostPort)
    listenSocket = socket(AF_INET, SOCK_DGRAM) # 绑定socket
    listenSocket.bind(hostAddr)
    print('Bind udp on', hostPort)

    # 服务端从客户端接收数据
    while 1:
        hostPort += 10
        data, dstAddr = listenSocket.recvfrom(MSS)
        temp = data.split(DELIMITER.encode())
        if temp[0] == 'lget':
            Thread(target=send, args=(dstAddr, temp[1])).start()
        elif temp[0] == 'lsend':
            Thread(target=receive, args=(hostAddr, dstAddr, temp[1])).start()