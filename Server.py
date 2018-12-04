# -*- coding:utf-8 -*-

from sender import *
from receiver import *

if __name__ == "__main__":
    # 服务端从客户端接收数据
    hostIP = ''
    hostPort = 21567
    filePath = './get.mp4'
    server = receiver(hostIP=hostIP, hostPort=hostPort, dstIP='', dstPort='', filePath=filePath, identity='server')
    server.createReceiver()

    server = sender(dstIP='', dstPort=21567, filePath='', identity='server')
    server.createSender()

