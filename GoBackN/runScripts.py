"""
This script is to run the three task assigned in the project and get the values output.
"""

import subprocess
import time
import sys

# Checking the correct output sequence is given or not at the command line
if len(sys.argv) != 4:
    print("python runScripts.py <server|client> <filename> <runtype: probability|mss|n>")
    exit(1)

# definining list for the tasks
mssList = [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]
windowSizeList = [1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]

print(windowSizeList)
probabilityList = [0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01]

def runServer(filename, dataTypes):
    if dataTypes == 'probability':
        for i in probabilityList:
            for j in range(0, 5):
                cmd1 = 'python Server/server.py 7735 ' + filename + ' ' + str(i)
                p = subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=True)
                p.communicate()
                time.sleep(1)
    elif dataTypes == 'mss':
        for i in mssList:
            for j in range(0, 5):
                cmd1 = 'python Server/server.py 7735 ' + filename + ' 0.05'
                p = subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=True)
                p.communicate()
                time.sleep(1)
    else:
        for i in windowSizeList:
            for j in range(0, 5):
                cmd1 = 'python Server/server.py 7735 ' + filename + ' 0.05'
                p = subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=True)
                p.communicate()
                time.sleep(1)

def runClient(filename, dataType):
    if dataType == 'probability':
        for i in probabilityList:
            timeaverage = float(0)
            for j in range(0, 5):
                cmd2 = 'python Client/client.py 127.0.0.1 7735 ' +  filename + ' 64 500'
                p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
                data = p2.communicate()[0].decode('utf-8').split('\n')[-2]
                print(data)
                timevalue = float(data.split(':')[-1])
                timeaverage += timevalue
                time.sleep(1)
            timeaverage = timeaverage/5
            print('Average Time for %s: %f'%(i,timeaverage))
    elif dataType == 'mss':
        for i in mssList:
            timeaverage = float(0)
            for j in range(0, 5):
                cmd2 = 'python Client/client.py 127.0.0.1 7735 ' +  filename + ' 64 ' + str(i)
                p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
                data = p2.communicate()[0].decode('utf-8').split('\n')[-2]
                print(data)
                timevalue = float(data.split(':')[-1])
                timeaverage += timevalue
                time.sleep(1)
            timeaverage = timeaverage/5
            print('Average Time for %s: %f'%(i,timeaverage))
    else:
        for i in windowSizeList:
            timeaverage = float(0)
            for j in range(0, 5):
                cmd2 = 'python Client/client.py 127.0.0.1 7735 ' +  filename +' '+ str(i) + ' 500'
                p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
                data = p2.communicate()[0].decode('utf-8').split('\n')[-2]
                print(data)
                timevalue = float(data.split(':')[-1])
                timeaverage += timevalue
                time.sleep(1)
            timeaverage = timeaverage/5
            print('Average Time for %s: %f'%(i,timeaverage))
def main():
    if sys.argv[1] == 'server':
        runServer(sys.argv[2], sys.argv[3])
    else:
        runClient(sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()