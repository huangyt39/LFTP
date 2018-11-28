from socket import *
import uu
import pdb

HOST = '127.0.0.1'
PORT = 21566
BUFSIZ = 1024
ADDR = (HOST, PORT)
DISADDR = (HOST, 21567)

udpCliSock = socket(AF_INET, SOCK_DGRAM)
udpCliSock.settimeout(1)
udpCliSock.bind(ADDR)

try:
    udpCliSock.recvfrom(BUFSIZ)
except BaseException as error:
    print(type(error))

udpCliSock.close()