# -*- coding:utf-8 -*-

from sender import *
from receiver import *

if __name__ == "__main__":
    # 客户端向服务端发送数据
    dstIP = '119.23.185.176'
    dstPort = 21567
    filePath = './test.mp4'
    client = sender(dstIP=dstIP, dstPort=dstPort, filePath=filePath, identity='client')
    client.createSender()

    client = receiver(hostIP='', hostPort=21567, dstIP=dstIP, dstPort=dstPort, filePath=filePath, identity='client')
    client.createReceiver()