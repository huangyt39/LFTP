# -*- coding:utf-8 -*-

import time
import numpy as np
from socket import *
from threading import *

MSS = 1024                  # 每个报文段的最大字节长度
DELIMITER = ' :|-:-|: '     # 用于分隔报文中各部分数据
SLOWSTART = 0               # 拥塞控制中的慢启动状态
AVOID = 1                   # 拥塞控制中的拥塞避免状态
FASTRECOVERY = 2            # 拥塞控制中的快速回复状态
INITIAL = -1                # 初始信号
WORKING = -2                # 忙碌信号
DONE = -3                   # 结束信号
CONNECT = -4                # 连接信号

# 接收方类
class receiver(object):
    '''
    @msg: 初始化发送的目的地址和端口, 读取要发送的文件
    @param:
        hostAddr     本机地址
        dstAddr      发送方地址
        filePath     文件存储的路径
        identity     类调用者的身份
    '''
    def __init__(self, hostAddr, dstAddr, filePath, identity):
        # 本机地址
        self.__hostAddr = hostAddr
        # 发送方地址
        self.__dstAddr = dstAddr
        # 采用udp
        self.__udpSock = socket(AF_INET, SOCK_DGRAM)
        self.__udpSock.bind(self.__hostAddr)
        # 互斥锁
        self.__lock = Lock()
        # 默认接收缓存大小设置为5
        self.__recvBuffer = 5
        # 打开文件存储路径
        self.__filePath = filePath
        # 调用者身份
        self.__identity = identity

    '''
    @msg: 开始一个接收任务, 收到发送方的报文之后回复接收缓存的大小, 以便接收方维护一个滑动流量控制窗口
    '''
    def createReceiver(self):
        self.__openFile(self.__filePath)
        if self.__fileExist == False:
            print('File path error')
            return
        if self.__identity is 'client':
            msg = 'lget' + DELIMITER + self.__filePath
            self.__udpSock.sendto(msg.encode(), self.__dstAddr)
            print('waiting for reply')
            data, self.__dstAddr = self.__udpSock.recvfrom(MSS)
            print('get server address')
            if data.decode() == 'server prepares to send data':
                self.__udpSock.sendto(b'%d' % self.__recvBuffer, self.__dstAddr)
                print('client prepares to receive data')
        elif self.__identity is 'server':
            self.__udpSock.sendto(b'%d' % self.__recvBuffer, self.__dstAddr)
            print('server prepares to receive data')
        self.__updateReceiving(True)
        self.__intiArgs() #  初始化所有参数
        self.__createThread() # 创建接收线程和写文件线程

    '''
    @msg: 初始化所有参数
    '''
    def __intiArgs(self):
        # 初始化所有参数
        self.__recvSeq = []
        self.__updateLastRcvd(0)
        self.__updateLastRead(0)
        self.__updateAck(-1)

    '''
    @msg: 创建发送线程和接收线程并启动
    '''
    def __createThread(self):
        # 创建发送线程和接收线程
        self.__recvThread = Thread(target=self.__recvData, name="recvThread")
        self.__writeThread = Thread(target=self.__writeData, name="writeThread")
        # 启动线程
        self.__recvThread.start()
        self.__writeThread.start()
        self.__recvThread.join()
        self.__writeThread.join()

    '''
    @msg: 执行接收数据
    '''
    def __recvData(self):
        self.__udpSock.settimeout(0.5)
        while 1:
            # 每次都要先更新接收窗口
            self.__updateRwnd(self.__recvBuffer - (self.__lastRcvd - self.__lastRead))
            # 若接收窗口为0则不接收数据
            if self.__rwnd == 0:
                continue
            # 监听数据包
            try:
                data = self.__udpSock.recv(2 * MSS)
            except:
                # 超时未收到想要的报文, 向发送方发送Ack
                msg = str(self.__ack) + DELIMITER + str(self.__rwnd)
                self.__sendAck(msg.encode(), self.__dstAddr)
                print('Ack: %d' % self.__ack)
            else:
                # 收到报文, 获取报文中的数据和序号，文件尾标识等
                temp = data.split(DELIMITER.encode())
                # 清空rwnd的特殊报文
                if temp[0].decode() == ' ':
                    msg = str(INITIAL) + DELIMITER + str(self.__rwnd)
                    print("send new rwnd")
                    self.__udpSock.sendto(msg.encode(), self.__dstAddr)
                    continue
                # 收到所请求的报文
                seqNum = int(temp[0].decode())
                if self.__ack + 1 == seqNum:
                    print("Receive pkt: %d" % seqNum)
                    self.__lock.acquire()
                    # 加入接收缓存队列
                    self.__recvSeq.append(temp[1])
                    self.__lock.release()
                    # 更新最新接收位置
                    self.__updateLastRcvd(self.__lastRcvd + 1)
                    self.__updateAck(self.__ack + 1)
                    # 收到文件尾标识
                    reply = ''
                    if int(temp[2]) == DONE:
                        reply = DONE
                        self.__updateReceiving(False)
                        self.__updateRwnd(self.__recvBuffer - (self.__lastRcvd - self.__lastRead))
                        # 回复特殊ack以告知传输完成 
                        reply = str(DONE) + DELIMITER + str(self.__rwnd)
                        self.__sendAck(reply.encode(), self.__dstAddr)
                        print('Ack: %d' % seqNum)
                        self.__udpSock.close()
                        print('receive complete')
                        break
                    # 发送ack
                    self.__updateRwnd(self.__recvBuffer - (self.__lastRcvd - self.__lastRead))
                    reply = str(seqNum) + DELIMITER + str(self.__rwnd)
                    self.__sendAck(reply.encode(), self.__dstAddr)
                    print('Ack: %d' % seqNum)

    '''
    @msg: 发送ack
    @param: 
        reply       回复的内容
        addr        发送地址
    '''
    def __sendAck(self, reply, addr):
        self.__lock.acquire()
        self.__udpSock.sendto(reply, addr)
        self.__lock.release()
        
    '''
    @msg: 将读到的数据写入文件
    '''
    def __writeData(self):
        while 1:
            # 将缓存队列中的数据按序依次写入文件
            while len(self.__recvSeq) > 0:
                self.__file.write(self.__recvSeq[0])
                # 更新已读位置
                self.__updateLastRead(self.__lastRead + 1)
                # 已写入文件的数据要从缓存队列中移除
                del self.__recvSeq[0]
            # 接收完成且完成写入文件
            if self.__recvState == False:
                print("Write complete")
                break
        self.__file.close()

        
    '''
    @msg: 更新接收窗口大小
    @param: newRwnd 当前的接收窗口大小
    '''
    def __updateRwnd(self, newRwnd):
        self.__lock.acquire()
        self.__rwnd = newRwnd
        self.__lock.release()

    '''
    @msg: 更新已收到的报文序号
    @param: newLastRcvd 上一个接收的报文序号
    '''
    def __updateLastRcvd(self, newLastRcvd):
        self.__lock.acquire()
        self.__lastRcvd = newLastRcvd
        self.__lock.release()

    '''
    @msg: 更新读到的文件位置
    @param: newLastRead 最新读到的文件位置
    '''
    def __updateLastRead(self, newLastRead):
        self.__lock.acquire()
        self.__lastRead = newLastRead
        self.__lock.release()

    '''
    @msg: 更新当前的Ack序号
    @param: newAck 下一个Ack序号
    '''
    def __updateAck(self, newAck):
        self.__lock.acquire()
        self.__ack = newAck
        self.__lock.release()

    '''
    @msg: 更新接收状态
    @param: newRecvState 新的接收状态 
    '''
    def __updateReceiving(self, newRecvState):
        self.__lock.acquire()
        self.__recvState = newRecvState
        self.__lock.release()

    '''
    @msg: 打开文件
    @param: filePath 文件路径
    '''
    def __openFile(self, filePath):
        try:
            self.__file = open('./' + str(filePath), 'wb')
        except:
            print("Open file error")
            self.__fileExist = False
        else:
            self.__fileExist = True
