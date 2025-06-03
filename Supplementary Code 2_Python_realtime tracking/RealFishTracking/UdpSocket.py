import socket
import time
import numpy as np

from RealFishTracking.utils.MyLogger import logger


class UdpSocket(object):
    def __init__(self, serverAddress, serverPort) -> None:
        self.serverAddress = serverAddress
        self.serverPort = serverPort
        self.udpSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


    def sendCoordinate(self, coorToSend):
        # msgToSend: str = np.array2string(coorToSend, separator=',', suppress_small=True)
        msgToSend = coorToSend.replace(" ", "")
        bytesToSend = str.encode(msgToSend)
        self.udpSocket.sendto(bytesToSend, (self.serverAddress, self.serverPort))
            

    def cleanUpSocket(self):
        self.udpSocket.close()

    
    def __del__(self):
        self.udpSocket.close()