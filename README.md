

# LFTP

### 简介

基于UDP实现可靠的大文件传输

### 需求

1. Please choose one of following programing languages: C, C++， Java, Python;
2. LFTP should use a client-server service model;
3. LFTP must include a client side program and a server side program;

- Client side program can not only send a large file to the server but also download a file from the server.
  - Sending file should use the following format：LFTP lsend myserver mylargefile
  - Getting file should use the following format：LFTP lget myserver mylargefile
- The parameter myserver can be a url address or an IP address.

1. LFTP should use UDP as the transport layer protocol.
2. LFTP must realize 100% reliability as TCP;
3. LFTP must implement flow control function similar as TCP;
4. LFTP must implement congestion control function similar as TCP;
5. LFTP server side must be able to support multiple clients at the same time;
6. LFTP should provide meaningful debug information when programs are executed.

### 分工

| 成员     | 黄树凯                              | 黄远韬                                    |
| -------- | :---------------------------------- | ----------------------------------------- |
| 实验分工 | 拥塞控制、多用户、日志、命令行      | 可靠传输、滑动窗口、实验报告              |
| 学号     | 16340085                            | 16340086                                  |
| Github   | [Treek](https://github.com/Treekay) | [huangyt39](https://github.com/huangyt39) |

### 环境

- windows

- python3.6.6

### 使用方法

- 发送文件

  ```shell
  LFTP lsend myserver mylargefile
  ```

- 下载文件

  ```shell
  LFTP lget myserver mylargefile
  ```

### 实验原理

#### 重传机制

receiver设置socket的timeout，如果超时未收到想要的报文，向发送方发送INITAL的Ack；

sender接收到receiver发送的Ack后进行判断，若Ack为INITAL，采用回退N步的方法重传

关键代码：

```python
# receiver.py
...
try:
	data = self.__udpSock.recv(2 * MSS)
except:
	# 超时未收到想要的报文, 向发送方发送Ack
	msg = str(self.__ack) + DELIMITER + str(self.__rwnd)
	self.__sendAck(msg.encode(), self.__dstAddr)
	print('Ack: %d' % seqNum)
...
```

```python
# sender.py
...
msg, addr = self.__udpSock.recvfrom(MSS)
temp = msg.decode().split(DELIMITER)
ack = int(temp[0])
self.__rwnd = int(temp[1])
# 该特殊ack代表rwnd重新清空
if ack == INITIAL:
	self.__sendState = True
	continue
...
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
```

#### 滑动窗口

根据窗口大小打包相应数量的数据包，即在数据的头尾分别加上序号和结束标记，同时将最后一个包打上特殊标记，发送数据包并更新滑动窗口

关键代码：

```python
# sender.py
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
```

#### 拥塞控制

一共分为三个状态，分别为慢启动SLOWSTART、拥塞避免AVOID和快速恢复FASTRECOVERY

开始时进入慢启动状态，慢启动状态中，若收到正确的Ack，则翻倍cwnd，直至超过阈值进入拥塞避免状态；若收到超过3个冗余Ack，进入快速恢复状态

在拥塞避免状态中。若收到正确的Ack，cwnd每次加1；若收到超过冗余Ack，进入快速恢复状态

在快速恢复状态中，若收到正确Ack，将cwnd置为阈值并进入拥塞避免状态；若收到冗余Ack则保持为快速恢复状态

关键代码：

```python
# sender.py
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
```



#### 多用户



关键代码：



### 测试样例

