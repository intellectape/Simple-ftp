
import socket  # Import socket module
import sys
from collections import namedtuple
import pickle
# from _thread import *
import threading
import inspect
import time
import signal

# from Packet import Packet

"""
N = 64  # window size
MSS = 100 # maximum segment size
ACK = 0 # ACK received from server.
num_pkts_sent = 0
num_pkts_acked = 0
seq_num = 0
#print(file_content)
#print (N)
window_low = 0
window_high = int(N)-1
total_pkts = 0
RTT = 2
#pkts = []
done_transmitting = 0
starttime = 0
stoptime= 0
"""

class Packet:
    def __init__(self, sequenceNumber ,id ,data ,eof ,checksum):
        self.sequenceNumber = sequenceNumber
        self. checksum =checksum
        self. id =id
        self. data =data
        self. eof =eof

class Acknowledgement:
    def __init__(self, sequenceNumber, zeros, ackField):
        self.sequenceNumber = sequenceNumber
        self.zeros = zeros
        self.ackField = ackField


class Client:


    num_pkts_sent = 0
    num_pkts_acked = 0
    window_low = 0
    # N = 64  # window size
    MSS = 100 # maximum segment size

    total_pkts = 0
    done_transmitting = 0
    starttime = 0
    stoptime= 0
    RTT = 2
    ACK = 0
    k=[]
    N=0
    filename=""

    def _init__(self, fileName, windowSize, mss, sequenceNumber):
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.fileName = fileName
        self.N = windowSize
        self.window_high = self.N - 1
        self.mss = mss
        self.ackSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ackSock.bind(("127.0.0.1", 62223))
        self.lock = threading.RLock()
        self.sequenceNumber = sequenceNumber
        # self.sock.bind((ipAddress, portNumber))



    def carry_checksum_addition(self,num_1, num_2):

        c = num_1 + num_2
        return (c & 0xffff) + (c >> 16)

    def calculate_checksum(self,message):

        # print (message)
        # if (len(message) % 2) != 0:
        #     message += bytes("0")

        checksum = 0
        for i in range(0, len(message), 2):
            my_message = str(message)
            w = ord(my_message[i]) + (ord(my_message[i + 1]) << 8)
            checksum = self.carry_checksum_addition(checksum, w)
        return (not checksum) & 0xfff

    def socket_function(self,pkts):

        # print (pkts)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a socket object

        # comment this block when ready for command line argument
        # N = input("Please enter window size N:>")
        # MSS = input("Please enter MSS in Bytes:>")
        host = socket.gethostname()  # Get local machine name
        # print("Host:", host)
        port = 7735  # Reserve a port for your service.
        s.sendto(pickle.dumps(pkts), (host, port))
        s.close()

    def timer(self,s, f):

        # global pkts
        # global window_low
        # global window_high
        # global total_pkts
        # global ACK
        # t = threading.Timer(RTT, timer)
        # t.start()
        # print ("Timer AAAAA")
        resent_index = self.window_low  # resent from window_low to window_high
        sendingData = self.divideFile(self.mss, self.filename, self.sequenceNumber)
        if self.ACK == self.window_low:
            print ("Timeout sequence number =" + str(self.ACK))
            self.lock.acquire()
            # print ("Timer CC")
            # print ("resent begin")
            while resent_index <= self.window_high and resent_index < self.total_pkts:
                # print ("resent "+ str(resent_index))
                # signal.alarm(0)
                # signal.alarm(int(RTT))
                signal.alarm(0)
                signal.setitimer(signal.ITIMER_REAL, self.RTT)
                self.socket_function(sendingData[resent_index])
                resent_index += 1
            self.lock.release()

    def rdt_send(self, sequenceNumber, filecontent):

        # global total_pkts
        # global num_pkts_sent
        self.total_pkts = len(filecontent)
        current_max_window = min(int(self.N), int(self.total_pkts))
        pkts = self.divideFile(self.mss, self.filename, sequenceNumber)
        signal.setitimer(signal.ITIMER_REAL, self.RTT)
        while self.num_pkts_sent < current_max_window:
        # socket_function(pkts[num_pkts_sent], sock, hostname, port)
        # t = threading.Timer(RTT,socket_function("hello"))
            if self.ACK == 0:
                # print ("num_pkts_sent"+ str(num_pkts_sent))
                self.socket_function(pkts[self.num_pkts_sent])
                # print("pakage "+str(num_pkts_sent)+"sent from first")
                # print(pkts[num_pkts_sent])
                self.num_pkts_sent += 1
            else:
                break

    def divideFile(self, mss, filename, sequenceNumber):

        # k = list()
        seqno = format(sequenceNumber, "032b")
        id = "0101010101010101"
        with open(filename, "rb") as binary_file:
            # Read the whole file at once
            data = binary_file.read()
            # Seek position and read N bytes
            i = 0
            length = sys.getsizeof(data)
            while i <= length:
                binary_file.seek(i)  # Go to beginning
                couple_bytes = binary_file.read(mss)
                checksum = self.calculate_checksum(couple_bytes)
                if i + mss > length:

                    self.k.append(Packet(seqno, id, couple_bytes, str(1), checksum))
                else:

                    self.k.append(Packet(seqno, id, couple_bytes, str(0), checksum))

                i += mss
                temp = int(seqno, 2) + 1
                seqno = format(temp, "032b")
        return self.k

    def ack_listen_thread(self,sock, host, port):

        """
        global window_high
        global window_low
        global num_pkts_sent
        global num_pkts_acked
        global total_pkts
        global ACK
        global done_transmitting
        global stoptime
        """
        self.done_transmitting = 0
        pkts = self.divideFile(self.mss, self.filename, self.sequenceNumber)
        # global threading_first_window
        while True:
            # threading_first_window.stop()
            data = pickle.loads(self.ackSock.recv(256))
            # print("ACK "+str(data[0]))
            # print("Wind_low "+str(window_low))
            # print("WInd_high"+str(window_high))
            # print("num_pkts_sent "+str(num_pkts_sent))
            # print("total"+str(total_pkts))
            # print("sent"+str(num_pkts_sent))
            if data.ackField == "1010101010101010":# data[2] is ACK identifier data[0] should be ACK sequence number. Foo
                self.ACK = int(data.sequenceNumber)
                # print (ACK)
                if self.ACK:  # and ACK >= int(N):  # if ACK != null. Foo
                    # print("hello"+str(ACK))
                    # if ACK
                    self.lock.acquire()
                    if self.ACK >= self.window_low and self.ACK < self.total_pkts:
                        signal.alarm(0)
                        # signal.alarm(int(RTT))
                        signal.setitimer(signal.ITIMER_REAL, self.RTT)
                        # print(window_low)
                        temp_pckts_acked = self.ACK - self.window_low
                        old_window_high = self.window_high
                        self.window_high = min(self.window_high + self.ACK - self.window_low, self.total_pkts - 1)
                        self.window_low = self.ACK
                        self.num_pkts_acked += temp_pckts_acked  # Acked # of packages. Foo
                        # print("ACK "+str(data[0]))
                        # print("Wind_low "+str(window_low))
                        # print("WInd_high"+str(window_high))
                        # print("num_pkts_sent "+str(num_pkts_sent))
                        for i in range(int(self.window_high - old_window_high)):
                            self.socket_function(pkts[self.num_pkts_sent])
                            # print("pakage "+str(num_pkts_sent)+"sent")
                            if self.num_pkts_sent < self.total_pkts - 1:
                                self.num_pkts_sent += 1

                    elif self.ACK == self.total_pkts:
                        print("Done!")
                        self.done_transmitting = 1
                        self.stoptime = time.time()
                        print("Running Time:", str(self.stoptime - self.starttime))
                        exit()
                    #
                    #
                    #
                    #     if window_high <= total_pkts and int(total_pkts-ACK)>=int(N):  # Still have packages to be sent. Foo
                    #         print("state A")
                    #         for i in range(min(temp_pckts_acked, total_pkts - window_high)): # check how many pkts left to sent. Foo
                    #             #sock.sendto(pkts[8], (host, port))
                    #             signal.alarm(int(RTT))
                    #             socket_function(pkts[num_pkts_sent])
                    #             print("pakage "+str(num_pkts_sent)+"sent")
                    #             print ("state B")
                    #             #print( pkts[num_pkts_sent])
                    #             if num_pkts_sent < total_pkts-1:
                    #                 num_pkts_sent += 1
                    # elif ACK < total_pkts: # for the last windows.
                    #      print("state1")
                    #      while num_pkts_sent <total_pkts: # check how many pkts left to sent. Foo
                    #             #sock.sendto(pkts[8], (host, port))
                    #             print("state2")
                    #             signal.alarm(int(RTT))
                    #             socket_function(pkts[num_pkts_sent])
                    #             print("pakage "+str(num_pkts_sent)+"sent")
                    #             #print( pkts[num_pkts_sent])
                    #             if num_pkts_sent < total_pkts-1:
                    #                 print("state3")
                    #                 num_pkts_sent += 1
                    #         # continue  # for the last windows.
                    #
                    # elif ACK == total_pkts:
                    #     print("Done!")
                    #     done_transmitting = 1
                    #     exit()
                    self.lock.release()


##
#     # # add something to listen ACK from server.
#
#

c = Client("send.txt", 64, 100, 0)
c.starttime = time.time()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 7735
signal.signal(signal.SIGALRM, timer)
f = c.divideFile(100, "send.txt", 0)
c.rdt_send(0, f)
host = "127.0.0.1"
threading.Thread(target=c.ack_listen_thread, args=(s, host, port)).start()
"""
try:


    file_content = []
    #test_file = open(my_test_file, 'rb')

    with open("python.txt", 'rb') as f:
        while True:
            chunk = f.read(100)  # Read the file MSS bytes each time Foo
            if chunk:
                file_content.append(chunk)
            else:
                break
    #print(file_content)
    #test_file.close()
except:
    sys.exit("Failed to open file!")
# start_new_thread(ack_listen_thread, (s, host, port))
#timer()
send_file(file_content, s, host, port)
threading.Thread(target=ack_listen_thread, args=(s, host, port)).start()
#global threading_first_window
#threading_first_window = threading.Thread(target=send_file, args=(file_content, s, host, port))
#threading_first_window.start()
s.close()  # Close the socket when done
"""











