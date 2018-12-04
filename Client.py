# -*- coding:utf-8 -*-

import sys
from sender import *
from receiver import *

# data : 'LFTP lget myserver mylargefile'
# data : 'LFTP lsend myserver mylargefile'

if __name__ == "__main__":
    # 客户端向服务端发送数据
    hostPort = 21567 # 指定客户端端口
    hostAddr = ('', hostPort)
    dstAddr = (sys.argv[3], hostPort)

    if sys.argv[2] == 'lget':
        receiver(hostAddr, dstAddr, sys.argv[4], 'client').createReceiver()
    elif sys.argv[2] == 'lsend':
        sender(dstAddr, sys.argv[4], 'client').createSender()