import sys
import time
import datetime
import socket
import pickle
import select
import signal
import os
import timeit
import threading

from Packet import *

if len(sys.argv) != 6:
    print('python client.py <server-host-name> <server-port#> <file-name> <N> <MSS>')
    exit(0)

class Client:

    def __init__(self, ipAddress, portNumber, fileName, windowSize, mss):
        self.portNumber = portNumber
        self.fileName = fileName
        # Creating the socket for the Client
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ipAddress = socket.gethostbyname(ipAddress)
        self.sock.connect((self.ipAddress, self.portNumber))
        self.sock.setblocking(0)
        self.mss = mss
        self.packetList = list() # Packet List as buffer to save data as the packet to be sent
        self.window_end = windowSize
        self.unacked = 0
        self.total_unacked = 0
        self.timeout = 0.1 # Timeout value for every packet to be sent
        self.sequenceNumber = 0 # default sequence Number to divide file


    # Carry bit used in one's combliment
    def carry_around_add(self, num_1, num_2):
        c = num_1 + num_2
        return (c & 0xffff) + (c >> 16)


    # Calculate the checksum of the data only. Return True or False
    def checksum(self,msg):
        """Compute and return a checksum of the given data"""
        msg = msg.decode('utf-8')
        if len(msg) % 2:
            msg += "0"
        
        s = 0
        for i in range(0, len(msg), 2):
            w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
            s = self.carry_around_add(s, w)
        return ~s & 0xffff

    # RDT Send method to send the file to the server
    def rdt_send(self):
        sendingData = self.divideFile(self.mss, self.fileName, self.sequenceNumber)
        self.unacked = 0
        self.total_unacked = 0
        while self.unacked < len(sendingData):
            if self.total_unacked < self.window_end and (self.total_unacked + self.unacked) < len(sendingData):
                
                for i in sendingData:
                    sq = int(i.sequenceNumber, 2)
                    if sq == self.total_unacked + self.unacked:
                        sendingPkt = i
                self.sock.send(pickle.dumps(sendingPkt))
                self.total_unacked += 1
                continue
            else:
                ready = select.select([self.sock], [], [], self.timeout)
                if ready[0]:
                    ackData, address = self.sock.recvfrom(4096)
                    ackData = pickle.loads(ackData)
                    if ackData.ackField != 0b1010101010101010:
                        continue
                    
                    if int(ackData.sequenceNumber,2) == self.unacked:
                        self.unacked += 1
                        self.total_unacked -= 1
                    else:
                        self.total_unacked = 0
                        continue
                else:
                    print('Timeout, sequence number = ', self.unacked)
                    self.total_unacked = 0
                    continue

        print('Files are transmitted successfully.')
        self.sock.close()

    # Function to divide the file into many chunks of packets based on the MSS value and save into list buffer
    def divideFile(self, mss, filename, sequenceNumber):
        #k = list()
        sequenceNumber = format(sequenceNumber, '032b')
        with open(filename, "rb") as binary_file:
            # Read the whole file at once
            data = binary_file.read()
            # Seek position and read N bytes
            i = 0
            length = sys.getsizeof(data)
            while i <= length:
                binary_file.seek(i)  # Go to beginning
                couple_bytes = binary_file.read(mss)
                checksum = self.checksum(couple_bytes)
                if i + mss > length:
                    self.packetList.append(Packet(sequenceNumber, couple_bytes, checksum, 1)) # adding eof value = 1 for the lastpacket
                else:
                    self.packetList.append(Packet(sequenceNumber, couple_bytes, checksum, 0))
                i += mss
                temp = int(sequenceNumber, 2) + 1
                sequenceNumber = format(temp, '032b')
        return self.packetList



# Main function which will run the main thread
def main():
    # Arguments are passed in order of acceptance in the command line arguments
    socClient = Client(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    #try:
    print("Run Time:",timeit.timeit(socClient.rdt_send, number = 1))
    #except:
    #   print("Error occured while sending")

if __name__ == "__main__":
    main()
