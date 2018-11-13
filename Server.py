# -*- coding:utf-8 -*-

from socket import *
from time import ctime
import uu
import pdb

HOST = '127.0.0.1'
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)
DISADDR = (HOST, 21566)

udpSerSock = socket(AF_INET, SOCK_DGRAM)
udpSerSock.bind(ADDR)
print('bind udp on 21567')
data = b''
count = 0
result = b''

packagenum, addr = udpSerSock.recvfrom(BUFSIZ)
packagenum = int(packagenum.decode())

while True:
    data, addr = udpSerSock.recvfrom(BUFSIZ)
    if data == b'EOF':
        break
    Ack = b'ACK' + data[:9]
    udpSerSock.sendto(Ack ,DISADDR)
    print((data[:8]).decode(), count, packagenum)
    count += 1
    result += data[8:]

try:
    f = open('D:/gitRep/LTFP/get.mp4', 'wb')
    f.write(result)
except:
    print("error")

udpSerSock.close()