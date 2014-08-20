__author__ = 'Adam'

import sys
import zmq
import time
import datetime
import hashlib
import random
import multiprocessing


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
        self.messagesList = self.mgr.list()
        self.peers = self.mgr.dict()

    def printWelcome(self):
        print("Welcome to ShitChat v0.1 - %s" % self.uid)


    def server(self,port=5556):
        context = zmq.Context()
        self.serverSocket = context.socket(zmq.PUB)
        self.serverSocket.bind("tcp://*:%s" % port)
        print("Running server on port %d" % port)
        while True:
            topic = "#"+str(random.randrange(9999,10002))
            messagedata = input("> ")
            if len(messagedata) > 0 and messagedata[0] == '\\':
                if messagedata == '\\quit':
                    exit()
            else:
                self.send(topic,str(messagedata))
            #socket.send_string("%d %d" % (topic, messagedata))

    def client(self,host,port="5556"):
        context = zmq.Context()
        print ("Connecting to server with port %d" % port)
        self.clientSocket = context.socket(zmq.SUB)
        topicfilter = ""
        self.clientSocket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

        print("Connecting to server %s" %(port))
        self.connect("tcp://%s:%s" % (host,port))
        #for request in range(20):
            #print ("Sending request %d ..." % request)
            #socket.send_string("Hello")
        while True:
            data = self.clientSocket.recv_string()
            parts = data.split()
            message = " ".join(parts[1:])
            topic = data[0]
            if topic == 'HELLO':
                remoteUID = parts[1]
                remoteURL = parts[2]
                if (remoteUID not in self.peers.keys()):
                    self.peers[remoteUID] = remoteURL
                    self.connect(url)
            else:
                print("<<< %s" % (message))

    def connect(self,url):
        self.clientSocket.connect(url)

    def send(self, topic, msg):
        message = self.username + str(topic) + "> " + msg
        print(message)
        self.serverSocket.send_string("%s %s" % (topic, msg))



if __name__ == "__main__":

    c = Chat()

    # Start client
    c.clientProcess = multiprocessing.Process(target=c.client, args=(c.host,c.port,))
    c.clientProcess.daemon = True
    c.clientProcess.start()

    c.init()
    c.server()
    #multiprocessing.Process(target=server, args=(port,)).start()


