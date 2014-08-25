__author__ = 'Adam'

import sys
import zmq
import socket
import multiprocessing
from multiprocessing import Array
import time
import ctypes

if sys.version_info[0] >= 3:
    def raw_input(prompt=""):
        return input(prompt)

def client(blocked,host,port="5556"):
    context = zmq.Context()
    clientSocket = context.socket(zmq.SUB)
    topicFilter = "".encode('utf-8')
    clientSocket.setsockopt(zmq.SUBSCRIBE, topicFilter)

    # Connect to servers
    url = "tcp://%s:%s" % (host,port)
    print("Connecting to server: %s" % url )
    clientSocket.connect(url)

    # Recieve messages
    while True:
        data = clientSocket.recv()
        parts = data.split()
        message = " ".join(parts[1:])
        topic = parts[0]
        with blocked.get_lock():
            blockedTopicsString = blocked.value
            blockedTopics = blockedTopicsString.split(':')
        if topic not in blockedTopics:
            print("\r%s" % message)


class Chat:
    username = "Anonymous"
    host = "localhost"
    port = 5555
    topic = ""
    clientSocket = None
    serverSocket = None
    clientProcess = None
    peers = []
    connectedHosts = []
    blockedTopics = []
    numBlockedTopics = 0
    lock = None


    def init(self):
        self.host = socket.gethostbyname(socket.gethostname())
        self.printWelcome()

        # Init args
        args = sys.argv

        if len(args) > 1:
            self.port = args[1]
        if len(args) > 2:
            self.username = args[2]

    def printWelcome(self):
        print("+------------------------------------------------------------")
        print("| Welcome to ShitChat v0.1")
        print("| Your ip is %s" % self.host)
        print("+------------------------------------------------------------")

    def server(self):

        context = zmq.Context()
        self.serverSocket = context.socket(zmq.PUB)
        self.serverSocket.bind("tcp://*:%s" % self.port)

        print("Running server on port %s" % self.port)

        while True:
            try:
                messageData = raw_input("%s> "%self.topic)
            except KeyboardInterrupt:
                messageData = "\\quit"

            if len(messageData) > 0 and messageData[0] == '\\':
                parts = messageData.split()
                cmd = parts[0][1:]

                # Quit
                if cmd == 'quit':
                    print("Bye!")
                    exit()
                # Connect to new server
                if cmd == 'connect':
                    if len(parts) < 3:
                        print("Please use: \\connect <host> <port>")
                    else:
                        self.connect(
                            parts[1], # Host
                            parts[2]  # Port
                        )
                # Help
                if cmd == "help":
                    print("Ask your mother.")

                # Set channel
                if cmd == "chan":
                    if len(parts) < 2:
                        print("No channel specified. Use \\chan <channel>")
                    else:
                        chan = parts[1]
                        if chan[0] != "#":
                            chan = "#"+chan
                        self.topic = chan


                # Set global channel
                if cmd == "leave":
                    self.topic = ""

                # Set new username.
                if cmd == "name":
                    if len(parts) < 2:
                        print("No name specified. Use \\name <new name>")
                    else:
                        self.username = parts[1]
                if cmd == "disconnect":
                    if len(parts) < 2:
                        print("No channel specified to disconnect from. Use \\disconnect <channel>")
                    else:
                        with self.blockedTopics.get_lock():
                            string = self.blockedTopics.value.decode('utf-8')
                            stringParts = string.split(':')

                            chan = parts[1]
                            if chan[0] != "#":
                                chan = "#"+chan

                            stringParts.append(chan)
                            print("Now blocking:")
                            print(", ".join(stringParts))
                            self.blockedTopics.value = ":".join(list(set(stringParts))).encode('ascii')
            else:
                self.send(self.topic,str(messageData))


    def connect(self,host,port):
        p = multiprocessing.Process(target=client, args=(self.lock,self.blockedTopics,host,port,))
        p.daemon = True
        p.start()
        self.peers.append(p)
        self.connectedHosts.append("%s:%s"%(host,port))
        time.sleep(1)



    def send(self, topic, msg):
        message = self.username + str(topic) + "> " + msg
        print(message)
        self.serverSocket.send(("%s %s" % (topic, message)))



if __name__ == "__main__":
    c = Chat()
    c.lock = multiprocessing.Lock()
    c.blockedTopics = Array(ctypes.c_char, 5000)
    c.blockedTopics.value = "hello".encode('ascii')
    c.init()
    c.server()


