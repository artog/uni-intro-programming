__author__ = 'Adam'

import sys
import zmq
import time
import datetime
import hashlib
import random
import multiprocessing


def client(host,port="5556"):
    context = zmq.Context()
    clientSocket = context.socket(zmq.SUB)
    topicFilter = ""
    clientSocket.setsockopt_string(zmq.SUBSCRIBE, topicFilter)
    url = "tcp://%s:%s" % (host,port)
    print("Connecting to server: %s" % url )
    clientSocket.connect(url)
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
        print("Welcome to ShitChat v0.1 - %s" % self.uid)


    def server(self,port=5556):
        context = zmq.Context()
        self.serverSocket = context.socket(zmq.PUB)
        self.serverSocket.bind("tcp://*:%s" % port)
        print("Running server on port %d" % port)
        while True:
            topic = "#"+str(random.randrange(9999,10002))
            messageData = input("> ")
            if len(messageData) > 0 and messageData[0] == '\\':
                if messageData == '\\quit':
                    exit()
                if messageData[0:8] == '\\connect':
                    parts = messageData.split()
                    if len(parts) < 3:
                        print("Please use: \connect <host> <port>")
                    else:
                        self.connect(parts[1],parts[2])
            else:
                self.send(topic,str(messageData))


    def connect(self,host,port):
        peer = multiprocessing.Process(target=client, args=(host,port,))
        peer.daemon = True
        peer.start()

    def send(self, topic, msg):
        message = self.username + str(topic) + "> " + msg
        print(message)
        self.serverSocket.send_string("%s %s" % (topic, message))



if __name__ == "__main__":

    c = Chat()
    print(c.namespace)
    c.port = 5555

    # Start client
    #\connect localhost 5556

    c.init()
    c.server()


