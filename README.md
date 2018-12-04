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

- 阿里云Ubuntu  16.04 64位 *2
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

### TCP原理

![transfer conplete](https://github.com/huangyt39/LFTP/blob/master/pic/flow.png?raw=true)

#### TCP 可靠传输

TCP 使用超时重传来实现可靠传输：如果一个已经发送的报文段在超时时间内没有收到确认，那么就重传这个报文段。

一个报文段从发送再到接收到确认所经过的时间称为往返时间 RTT，加权平均往返时间 RTTs 计算如下：

<div align="center"><img src="https://latex.codecogs.com/gif.latex?RTTs=(1-a)*(RTTs)+a*RTT"/></div> <br>

超时时间 RTO 应该略大于 RTTs，TCP 使用的超时时间计算如下：

<div align="center"><img src="https://latex.codecogs.com/gif.latex?RTO=RTTs+4*RTT_d"/></div> <br>

其中 RTT<sub>d</sub> 为偏差。

#### TCP 滑动窗口

窗口是缓存的一部分，用来暂时存放字节流。发送方和接收方各有一个窗口，接收方通过 TCP 报文段中的窗口字段告诉发送方自己的窗口大小，发送方根据这个值和其它信息设置自己的窗口大小。

发送窗口内的字节都允许被发送，接收窗口内的字节都允许被接收。如果发送窗口左部的字节已经发送并且收到了确认，那么就将发送窗口向右滑动一定距离，直到左部第一个字节不是已发送并且已确认的状态；接收窗口的滑动类似，接收窗口左部字节已经发送确认并交付主机，就向右滑动接收窗口。

接收窗口只会对窗口内最后一个按序到达的字节进行确认，例如接收窗口已经收到的字节为 {31, 34, 35}，其中 {31} 按序到达，而 {34, 35} 就不是，因此只对字节 31 进行确认。发送方得到一个字节的确认之后，就知道这个字节之前的所有字节都已经被接收。

![transfer conplete](https://github.com/huangyt39/LFTP/blob/master/pic/windowspic.png?raw=true)

#### TCP 流量控制

流量控制是为了控制发送方发送速率，保证接收方来得及接收。

接收方发送的确认报文中的窗口字段可以用来控制发送方窗口大小，从而影响发送方的发送速率。将窗口字段设置为 0，则发送方不能发送数据。

#### TCP 拥塞控制

如果网络出现拥塞，分组将会丢失，此时发送方会继续重传，从而导致网络拥塞程度更高。因此当出现拥塞时，应当控制发送方的速率。这一点和流量控制很像，但是出发点不同。流量控制是为了让接收方能来得及接收，而拥塞控制是为了降低整个网络的拥塞程度。

![transfer conplete](https://github.com/huangyt39/LFTP/blob/master/pic/conpic.jpg?raw=true)

TCP 主要通过四个算法来进行拥塞控制：慢开始、拥塞避免、快重传、快恢复。

发送方需要维护一个叫做拥塞窗口（cwnd）的状态变量，注意拥塞窗口与发送方窗口的区别：拥塞窗口只是一个状态变量，实际决定发送方能发送多少数据的是发送方窗口。

为了便于讨论，做如下假设：

- 接收方有足够大的接收缓存，因此不会发生流量控制；
- 虽然 TCP 的窗口基于字节，但是这里设窗口的大小单位为报文段。

![transfer conplete](https://github.com/huangyt39/LFTP/blob/master/pic/conpic2.png?raw=true)

1.慢开始与拥塞避免

发送的最初执行慢开始，令 cwnd = 1，发送方只能发送 1 个报文段；当收到确认后，将 cwnd 加倍，因此之后发送方能够发送的报文段数量为：2、4、8 ...

注意到慢开始每个轮次都将 cwnd 加倍，这样会让 cwnd 增长速度非常快，从而使得发送方发送的速度增长速度过快，网络拥塞的可能性也就更高。设置一个慢开始门限 ssthresh，当 cwnd >= ssthresh 时，进入拥塞避免，每个轮次只将 cwnd 加 1。

如果出现了超时，则令 ssthresh = cwnd / 2，然后重新执行慢开始。

2.快重传与快恢复

在接收方，要求每次接收到报文段都应该对最后一个已收到的有序报文段进行确认。例如已经接收到 M<sub>1</sub> 和 M<sub>2</sub>，此时收到 M<sub>4</sub>，应当发送对 M<sub>2</sub> 的确认。

在发送方，如果收到三个重复确认，那么可以知道下一个报文段丢失，此时执行快重传，立即重传下一个报文段。例如收到三个 M<sub>2</sub>，则 M<sub>3</sub> 丢失，立即重传 M<sub>3</sub>。

在这种情况下，只是丢失个别报文段，而不是网络拥塞。因此执行快恢复，令 ssthresh = cwnd / 2 ，cwnd = ssthresh，注意到此时直接进入拥塞避免。

慢开始和快恢复的快慢指的是 cwnd 的设定值，而不是 cwnd 的增长速率。慢开始 cwnd 设定为 1，而快恢复 cwnd 设定为 ssthresh。

### 实验原理

#### 重传机制

receiver设置socket的timeout，如果超时未收到想要的报文，向发送方发送的Ack；

sender接收到receiver发送的Ack后进行判断，若Ack为冗余的，采用回退N步的方法重传

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

#### 流控制

根据接收方的接收窗口大小设置滑动窗口的大小，每次打包相应数量的数据包，并在数据的头尾分别加上序号和结束标记，文件的最后一个包加上特殊的文件结束标记以便接收方确认接收完成。实际发送时除了滑动窗口大小还要考虑拥塞控制窗口的大小来决定每次实际发送的数据包数量，发送的数据包存在缓存队列中，收到相应的Ack时从队列中移除。每次缓存队列中有新加入的数据包或移除数据包都要更新滑动窗口重新确认可用于发送的大小

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
```
```python
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
```
```python
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
将发送端和接收端封装成类, 根据客户端程序运行时命令行输入的指令, 创建相应的发送类或接受类的实例, 并给特定的服务端地址和端口发送消息, 服务端收到消息后, 创建新的线程执行新实例化的发送类或接受类


关键代码：
```python
# 客户端
if __name__ == "__main__":
    # 客户端向服务端发送数据
    hostPort = int(input('input client port: '))    # 指定客户端的端口
    dstAddr = (sys.argv[3], 21567)

    if sys.argv[2] == 'lget':
        receiver(('', hostPort), dstAddr, sys.argv[4], 'client').createReceiver()
    elif sys.argv[2] == 'lsend':
        sender(('', hostPort), dstAddr, sys.argv[4], 'client').createSender()
```
```python
# 服务端
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
```


### 测试样例

#### 机制

重传

![transfer conplete](https://github.com/huangyt39/LFTP/blob/master/pic/resend.png?raw=true)

滑动窗口

![windows](https://github.com/huangyt39/LFTP/blob/master/pic/windows.png?raw=true)

拥塞控制

![transfer conplete](https://github.com/huangyt39/LFTP/blob/master/pic/congestion.png?raw=true)

多用户

![transfer conplete](https://github.com/huangyt39/LFTP/blob/master/pic/multiuser.png?raw=true)

#### 接收方

写文件

![writing complete](https://github.com/huangyt39/LFTP/blob/master/pic/reicver%20writing.png?raw=true)

接受完成

![writing complete](https://github.com/huangyt39/LFTP/blob/master/pic/writing%20complete.png?raw=true)

#### 发送方

发送完成

![transfer conplete](https://github.com/huangyt39/LFTP/blob/master/pic/transfer%20complete.png?raw=true)

#### 传输结果

开始传输

![transfer conplete](https://github.com/huangyt39/LFTP/blob/master/pic/begin.png?raw=true)

传输完成

![transfer conplete](https://github.com/huangyt39/LFTP/blob/master/pic/result.png?raw=true)

### 注意事项

在自己的服务器运行的时候需要改一下Server的ip地址和端口，笔者使用的是自己的云服务器



