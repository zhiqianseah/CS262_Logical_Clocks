import socket
import sched, time
import random
import errno

class VirtualMachine:

    def __init__(self, port, ticks):
        self._hostSocket = socket.socket()         # Create a socket object
        self._interval = 1.0/ticks
        self._clientSockets = {}
        self._clientReceive = {}
        self._clientports = []
        host = '0.0.0.0'            # Get local machine name
        self._threadcounter = 0

        print 'VM started!'


        self._hostSocket.bind((host, port))        # Bind to the port


    #This function waits for a connection from a given port
    def wait_for_connection(self, port):

        print 'Waiting for clients...'


        while True:
            try:
                self._hostSocket.listen(1)                 # Now wait for client connection.
                c, addr = self._hostSocket.accept()     # Establish connection with client.
                print 'Got connection from', addr


                #set the receive socket as non-blocking
                c.setblocking(False)
                self._clientReceive[port] = c

                #once connection is established, break out of while loop
                break;

            
            except socket.error, e:
                pass

        self._threadcounter+=1

    def connect_to(self, port):
        s = socket.socket()         # Create a socket object to connect to other VMs
        host = socket.gethostname() # Get local machine name

        print 'Connecting to ', host, port


        while(s.connect_ex((host, port))):
            pass


        #msg = "hi"
        #s.send(msg)

        self._clientports.append(port)
        self._clientSockets[port] = s

    def send_msg(self, port, msg):
        print "Sending message to:", port
        try:
            self._clientSockets[port].send(msg)
        except:
            print "Enable to send message. Socket may be closed"


    def runVM(self, duration):
        start = time.time()
        while True:


            #check for incoming messages in the socket
            #TODO: put this in a message queue..?
            try:
                msg = self._clientReceive[self._clientports[0]].recv(4096)
                print "message from", self._clientports[0], ":", msg
            except socket.error, e:
                pass
                #err = e.args[0]
                #if (err == errno.EAGAIN or err == errno.EWOULDBLOCK):
                #    pass

            try:
                msg = self._clientReceive[self._clientports[1]].recv(4096)
                print "message from", self._clientports[1], ":", msg
            except socket.error, e:
                pass
                #err = e.args[0]
                #if (err == errno.EAGAIN or err == errno.EWOULDBLOCK):
                #    pass




            #generate a random number to see next course of action
            rand_num = random.randrange(1, 11)
            print "tick:", rand_num
            if (rand_num == 1):
                self.send_msg(self._clientports[0], "hi")
            elif (rand_num == 2):
                self.send_msg(self._clientports[1], "hi")
            elif (rand_num == 3):
                self.send_msg(self._clientports[0], "hi")
                self.send_msg(self._clientports[1], "hi")

            #stop the VM when the duration is up
            if (time.time() - start) > duration:
                break

            #pause for the remainder of a tick
            time.sleep(self._interval - ((time.time() - start) % self._interval))
