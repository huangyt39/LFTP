# -*- coding:utf-8 -*-

import time
import numpy as np
from socket import *
from threading import *

MSS = 1024                  # 每个报文段的最大字节长度
DELIMITER = ' :|-:-|: '     # 用于分隔报文中各部分数据
SLOWSTART = 0               # 拥塞控制中的慢启动状态
AVOID = 1                   # 拥塞控制中的拥塞避免状态
FASTRECOVERY = 2            # 拥塞控制中的快速恢复状态
INITIAL = -1                # 初始信号
WORKING = -2                # 忙碌信号
DONE = -3                   # 结束信号
CONNECT = -4                # 连接信号

# 发送方类
class sender(object):
    '''
    @msg: 初始化发送的目的地址和端口, 读取要发送的文件
    @param:
        hostAddr     本机地址
        dstAddr     接收方地址
        filePath    将要发送的文件所在路径
        identity     类调用者的身份
    '''
    def __init__(self, hostAddr, dstAddr, filePath, identity):
        # 本机地址
        self.__hostAddr = hostAddr
        # 接收方地址
        self.__dstAddr = dstAddr
        # 采用udp
        self.__udpSock = socket(AF_INET, SOCK_DGRAM)
        self.__udpSock.bind(self.__hostAddr)
        # 互斥锁
        self.__lock = Lock()
        # 发送窗口大小默认为5
        self.__windowSize = 5
        # 读取文件
        self.__filePath = filePath
        # 调用者身份
        self.__identity = identity

    '''
    @msg: 开始一个发送任务, 向接收方发送特定报文获取接收方的接收窗口大小
    '''
    def createSender(self):
        self.__openFile(self.__filePath)
        if self.__fileEnd == True:
            print('File path error')
            return
        if self.__identity is 'server':
            print('server prepares to send data')
            msg = 'server prepares to send data'
        elif self.__identity is 'client':
            print('client prepares to send data')
            msg = 'lsend' + DELIMITER + self.__filePath
        self.__udpSock.sendto(msg.encode(), self.__dstAddr)
        print('send msg')
        newRwnd, self.__dstAddr = self.__udpSock.recvfrom(MSS)
        print('update rwnd')
        self.__rwnd = int(newRwnd.decode())
        self.__initArgs()
        self.__createThread()

    '''
    @msg: 
    @param:
        sendState           当前的发送状态
        sendSeq             缓存队列
        send_base           当前排在最前的已发送未确认的报文序号
        nextseqnum          下一个可用于发送的队列位置
        sendSize            发送窗口大小
        congestionState     拥塞控制状态
        cwnd                拥塞控制窗口大小
        dupAck              当前的收到的冗余Ack数量
        ssthresh            
        timerWorking        当前计时器是否处于工作状态
    '''
    def __initArgs(self):
        # 初始化所有参数
        self.__sendState = True
        self.__sendSeq = []
        self.__send_base = 0
        self.__nextseqnum = 0
        self.__sendSize = 0
        self.__congestionState = SLOWSTART
        self.__cwnd = 5.0
        self.__dupAck = 0
        self.__ssthresh = 50.0
        self.__timerWorking = False

    '''
    @msg: 创建一个线程用与发送数据, 一个线程用于接收Ack
    '''
    def __createThread(self):
        # 创建发送线程和接收线程
        self.__sendThread = Thread(target=self.__sendData, name="sendThread")
        self.__recvThread = Thread(target=self.__recvMsg, name="recvThread")
        # 启动线程
        self.__sendThread.start()
        self.__recvThread.start()
        self.__sendThread.join()
        self.__recvThread.join()

    '''
    @msg: 每次从文件中读取一定长度数据并发送, 直到整个文件发送完成
    '''
    def __sendData(self):
        print('sending start')
        # 读取到文件末尾才结束循环
        while self.__fileEnd == False:
            # 更新发送窗口大小
            # 由于发送线程和接收线程都涉及到该变量
            # 在修改时要先加锁
            self.__lock.acquire()
            self.__sendSize = np.min([self.__rwnd, self.__cwnd])
            self.__lock.release()
            # 当发送窗口为0时不能发送数据
            if self.__sendSize == 0:
                # 发送一个空报文段来让接收方更新rwnd
                self.__udpSock.sendto(b' ', self.__dstAddr) 
                print("get new rwnd")
                time.sleep(0.1)
            # 当发送窗口不为0且数据未传输完成时
            elif self.__sendState == True:
                # 将缓存队列中的数据逐个进行发送
                for i in range(int(self.__sendSize)):
                    # 流控制
                    self.__streamControl()
                    # 读取到文件末尾则退出
                    if self.__fileEnd == True:
                        break
                # 更新发送状态
                self.__lock.acquire()
                self.__sendState = False
                self.__lock.release()
        print('send complete')
        # 关闭文件
        self.__file.close()

    '''
    @msg: 执行接收Ack
    '''
    def __recvMsg(self):
        while 1:
            msg, addr = self.__udpSock.recvfrom(MSS)
            temp = msg.decode().split(DELIMITER)
            ack = int(temp[0])
            self.__rwnd = int(temp[1])
            # 该特殊ack代表rwnd重新清空
            if ack == INITIAL:
                self.__sendState = True
                continue
            # 该特殊ack代表文件接收完成
            elif ack == DONE:
                self.__udpSock.close()
                self.__timer.cancel()
                break
            # 拥塞控制
            self.__congestionControl(ack)

    '''
    @msg: 接收新的Ack
    '''
    def __recvNewAck(self):
        # 窗口右移
        self.__lock.acquire()
        del self.__sendSeq[0]
        self.__send_base += 1
        self.__lock.release()
        self.__dupAck = 0
        # 收到正在确认的报文序号, 结束计时器, 将该序号标记为已确认
        if self.__nextseqnum == self.__send_base:
            self.__timer.cancel()
            self.__timerWorking = False
        else:
            # 重启计时器
            if self.__timerWorking:
                self.__timer.cancel()
            self.__timer = Timer(1.0, self.__resend)
            self.__timer.start()
            self.__timerWorking = True

    '''
    @msg: 重传报文, 采用回退N步的方法重传
    '''
    def __resend(self):
        # 重启计时器
        if self.__timerWorking:
            self.__timer.cancel()
        self.__timer = Timer(1.0, self.__resend)
        self.__timer.start()
        self.__timerWorking = True
        # 对缓存序列中的N个报文进行重传
        self.__lock.acquire()
        for pkt in self.__sendSeq:
            seqnum, data, end = pkt.split(DELIMITER.encode())
            print("Resend pkt: %d" % int(seqnum.decode()))
            self.__udpSock.sendto(pkt, self.__dstAddr)
        self.__lock.release()

    '''
    @msg: 流控制, 限制当前的发送数量不能大于接收方接收窗口和自己的发送窗口
    '''
    def __streamControl(self):
        if self.__nextseqnum - self.__send_base < self.__rwnd and \
            self.__nextseqnum - self.__send_base < self.__windowSize:
            # 每个报文段读取1 MSS的数据
            data = self.__file.read(MSS) 
            # 数据包格式: 序号 || 数据 || 结束标记
            if len(data) < MSS:
                pkt = str(self.__nextseqnum).encode() + DELIMITER.encode() \
                    + data + DELIMITER.encode() + str(DONE).encode()
                self.__fileEnd = True
            # 最后的一个报文要打上特殊标记
            else:
                pkt = str(self.__nextseqnum).encode() + DELIMITER.encode() \
                    + data + DELIMITER.encode() + str(WORKING).encode()
                self.__fileEnd = False
            # 发送报文
            print("Send pkt: %d" % self.__nextseqnum)
            self.__udpSock.sendto(pkt, self.__dstAddr)
            if self.__nextseqnum == self.__send_base:
                # 重启计时器
                if self.__timerWorking:
                    self.__timer.cancel()
                self.__timer = Timer(1.0, self.__resend)
                self.__timer.start()
                self.__timerWorking = True
            # 更新滑动窗口
            self.__lock.acquire()
            self.__sendSeq.append(pkt)
            self.__nextseqnum += 1
            self.__lock.release()
            
    '''
    @msg: 拥塞控制
    @param: ack     本次收到的ack
    '''
    def __congestionControl(self, ack):
        # 慢启动状态
        if self.__congestionState is SLOWSTART:
            # 收到正确的ack
            if ack >= self.__send_base:
                print("recv Ack: %d" % ack)
                self.__recvNewAck()
                self.__lock.acquire()
                self.__sendState = True
                # cwnd 每次翻倍
                # (对每个报文而言是加1,但单位时间内cwnd的增加即为发的报文数量)
                if self.__cwnd + 1 < self.__ssthresh:
                    self.__cwnd = self.__cwnd + 1
                # 超过阈值将进入拥塞避免状态
                else:
                    self.__cwnd = self.__ssthresh
                    self.__congestionState = AVOID
                self.__lock.release()
            # 收到冗余ack
            else:
                print("get dup ack")
                self.__dupAck = self.__dupAck + 1
                # 超过3个冗余ack将进入快速恢复状态
                if self.__dupAck >= 3:
                    # 快速重传
                    self.__resend()
                    self.__lock.acquire()
                    # 更新阈值为拥塞窗口的一半
                    if self.__cwnd < 10:
                        self.__ssthresh = 5.0
                    else:
                        self.__ssthresh = self.__cwnd / 2
                    self.__cwnd = 5.0
                    # 清空冗余ack计数
                    self.__dupAck = 0
                    self.__lock.release()
                    # 进入快速恢复状态
                    self.__congestionState = FASTRECOVERY
        # 拥塞避免状态
        elif self.__congestionState is AVOID:
            # 收到正确的ACK
            if ack >= self.__send_base:
                print("recv Ack: %d" % ack)
                self.__recvNewAck()
                self.__lock.acquire()
                self.__sendState = True
                # cwnd 每次加 1
                self.__cwnd += 1.0 / int(self.__cwnd)
                self.__lock.release()
            # 收到冗余ack
            else:
                print("get dup ack")
                self.__dupAck =  self.__dupAck + 1
                # 超过3个冗余ack将进入快速恢复状态
                if self.__dupAck >= 3:
                    # 快速重传
                    self.__resend()
                    self.__lock.acquire()
                    # 更新阈值为拥塞窗口的一半
                    if self.__cwnd < 10:
                        self.__ssthresh = 5.0
                    else:
                        self.__ssthresh = self.__cwnd / 2
                    self.__cwnd = 5.0
                    # 清空冗余ack计数
                    self.__dupAck = 0
                    self.__lock.release()
                    # 进入快速恢复状态
                    self.__congestionState = FASTRECOVERY
        # 快速恢复状态
        elif self.__congestionState is FASTRECOVERY:
            # 收到正确ack
            if ack >= self.__send_base:
                print("recv Ack: %d" % ack)
                self.__recvNewAck()
                self.__lock.acquire()
                # 更新cwnd为阈值大小
                self.__cwnd = self.__ssthresh
                # 进入拥塞避免状态
                self.__congestionState = AVOID
                self.__lock.release()
            # 收到冗余ack
            else:
                self.__lock.acquire()
                self.__sendState = True
                self.__cwnd += 1
                self.__lock.release()
    
    '''
    @msg: 打开文件
    @param filePath: 文件路径
    '''
    def __openFile(self, filePath):
        try:
            self.__file = open('./' + filePath, 'rb')
        except:
            print("Open file error")
            self.__fileEnd = True
        else:
            self.__fileEnd = False
