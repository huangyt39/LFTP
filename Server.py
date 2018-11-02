# -*- coding:utf-8 -*-

from socket import *
from time import ctime
import uu

HOST = '127.0.0.1'
PORT = 21567
BUFSIZ = 100024
ADDR = (HOST, PORT)

udpSerSock = socket(AF_INET, SOCK_DGRAM)
udpSerSock.bind(ADDR)
print('bind udp on 21567')
data = b""
count = 0
result = ""

packagenum, addr = udpSerSock.recvfrom(BUFSIZ)
packagenum = int(packagenum.decode())

while True:
    data, addr = udpSerSock.recvfrom(BUFSIZ)
    if data.decode() == 'EOF':
        break
    print(count/packagenum)
    count += 1
    result += data.decode()

f = open('get.txt', 'w', newline="")
f.write(result)
uu.decode('test.txt', 'test.mp4')

udpSerSock.close()