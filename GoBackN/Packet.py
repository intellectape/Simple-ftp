"""
This code is to create class for the Packet to be transferred
"""


class Packet:
    def __init__(self, sequenceNumber, packet, checksum, eof = False):
        self.sequenceNumber = sequenceNumber
        self.dataId = 0b0101010101010101
        self.packet = packet
        self.checksum = checksum
        self.eof = eof
    def printPacket(self):
        print('Sequence Number: ', self.sequenceNumber)
        print('ID: ', self.dataId)
        print('Checksum: ', self.checksum)
        print('End of File: ', self.eof)

class Acknowledgment:
    def __init__(self, sequenceNumber):
        self.sequenceNumber = sequenceNumber
        self.zeros = 0
        self.ackField = 0b1010101010101010
    
    def printAcknowledgement(self):
        print('Sequence Number: ', self.sequenceNumber)
        print('Zeros: ', self.zeros)
        print('ACK Field: ', self.ackField)