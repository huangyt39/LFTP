# -*- coding:utf-8 -*-

from socket import *
import uu

HOST = '127.0.0.1'
PORT = 21567
BUFSIZ = 100024
ADDR = (HOST, PORT)

udpCliSock = socket(AF_INET, SOCK_DGRAM)

uu.encode('test.mp4', 'test.txt')
f = open('test.txt', 'r')
data = f.read()

size = len(data)
packagenum = size//100 + 1

udpCliSock.sendto(str(packagenum).encode(), ADDR)

for index in range(packagenum):
    subdata = ""
    if (index + 1)*100 > size:
        subdata = data[index*100:]
    else:
        subdata = data[index*100:(index + 1)*100]
    udpCliSock.sendto(subdata.encode(), ADDR)
    # mes, ADDR = udpCliSock.recvfrom(BUFSIZ)
    # if not mes:
    #     break
    # print(mes.decode())
    print(index/packagenum)
udpCliSock.sendto(b'EOF', ADDR)

udpCliSock.close()

# while True:
#     data = input('>')
#     if not data:
#         break
#     udpCliSock.sendto(data.encode(), ADDR)
#     data, ADDR = udpCliSock.recvfrom(BUFSIZ)
#     if not data:
#         break
#     print(data.decode())