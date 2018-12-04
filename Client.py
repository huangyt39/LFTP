# -*- coding:utf-8 -*-

import sys
from sender import *
from receiver import *

# data : 'LFTP lget myserver mylargefile'
# data : 'LFTP lsend myserver mylargefile'

if __name__ == "__main__":
    # 客户端向服务端发送数据
    hostPort = int(input('input client port: '))    # 指定客户端的端口
    dstAddr = (sys.argv[3], 21567)

    if sys.argv[2] == 'lget':
        receiver(('', hostPort), dstAddr, sys.argv[4], 'client').createReceiver()
    elif sys.argv[2] == 'lsend':
        sender(('', hostPort), dstAddr, sys.argv[4], 'client').createSender()
