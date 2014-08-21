__author__ = 'Adam'

import sys
import zmq
import time
import socket
import hashlib
import random
import multiprocessing

if sys.version_info[0] >= 3:
    def raw_input():
        return input()

def client(host,port="5556"):
    context = zmq.Context()
    clientSocket = context.socket(zmq.SUB)
    topicFilter = ""
    clientSocket.setsockopt_string(zmq.SUBSCRIBE, topicFilter)

    # Connect to servers
    url = "tcp://%s:%s" % (host,port)
    print("Connecting to server: %s" % url )
    clientSocket.connect(url)

    # Recieve messages
    while True:
        data = clientSocket.recv_string()
        parts = data.split()
        message = " ".join(parts[1:])
        print("\n%s" % (message))


class Chat:
    username = "Anonymous"
    host = "localhost"
    port = 5556
    rand = str(random.random())+str(time.process_time())
    rand = rand.encode('utf-8')
    hash = hashlib.md5(rand)
    uid = hash.hexdigest()
    mgr = None
    clientSocket = None
    serverSocket = None
    clientProcess = None
    namespace = None
    lock = None
    peers = []

    def init(self):
        self.printWelcome()

        # Init args
        args = sys.argv

        if len(args) > 1:
            self.host = args[1]
        if len(args) > 2:
            self.port = int(args[2])
        if len(args) > 3:
            self.username = args[3]

        self.mgr = multiprocessing.Manager()
        self.peers = self.mgr.dict()

    def printWelcome(self):
        print("+------------------------------------------------------------")
        print("| Welcome to ShitChat v0.1 - %s" % self.uid)
        ip = socket.getbyhostname(socket.gethostname)
        print("| Your ip is %s" % ip)
        print("+------------------------------------------------------------")

    def server(self):

        context = zmq.Context()
        self.serverSocket = context.socket(zmq.PUB)
        self.serverSocket.bind("tcp://*:%s" % self.port)

        print("Running server on port %d" % self.port)

        while True:
            topic = "#"+str(random.randrange(9999,10002))
            messageData = input("> ")
            if len(messageData) > 0 and messageData[0] == '\\':
                parts = messageData.split()
                cmd = parts[0][1:]

                if cmd == 'quit':
                    exit()
                if cmd == 'connect':
                    if len(parts) < 3:
                        print("Please use: \connect <host> <port>")
                    else:
                        self.connect(parts[1],parts[2])
                if cmd == "help":
                    print("Ask your mother.")
            else:
                self.send(topic,str(messageData))


    def connect(self,host,port):
        self.peers.append(multiprocessing.Process(target=client, args=(host,port,)))
        self.peers[-1].daemon = True
        self.peers[-1].start()


    def send(self, topic, msg):
        message = self.username + str(topic) + "> " + msg
        print(message)
        self.serverSocket.send_string("%s %s" % (topic, message))



if __name__ == "__main__":

    c = Chat()

    c.port = 5555

    # Start client
    #\connect localhost 5556
    lock = multiprocessing.Lock()
    parent,child = multiprocessing.Pipe()

    c.init()
    c.server()


