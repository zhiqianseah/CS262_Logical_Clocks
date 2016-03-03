import socket
import sched, time
import random
import thread

class VirtualMachine:

    def __init__(self, port, ticks):
        self._hostSocket = socket.socket()         # Create a socket object
        self._interval = 1.0/ticks
        self._clientSockets = {}
        self._clientports = []
        host = '0.0.0.0'            # Get local machine name
        self._threadcounter = 0

        print 'VM started!'


        self._hostSocket.bind((host, port))        # Bind to the port

    # Define a thread to receive messages for each client
    def receive_thread(self, threadName, ):
        print 'Waiting for clients...'
        self._hostSocket.listen(5)                 # Now wait for client connection.
        c, addr = self._hostSocket.accept()     # Establish connection with client.
        print 'Got connection from', addr
        while True:

            try:
                msg = c.recv(1024)
                print addr, ' >> ', msg
            except:
                print "Socket closed."
                break

    #Create a new thread to wait for a connection. This thread is used to service the receiving of messages
    def wait_for_connection(self):

        thread.start_new_thread( self.receive_thread, ("Thread-" + str(self._threadcounter), ) )
        self._threadcounter+=1

    def connect_to(self, port):
        s = socket.socket()         # Create a socket object to connect to other VMs
        host = socket.gethostname() # Get local machine name

        print 'Connecting to ', host, port


        while(s.connect_ex((host, port))):
            pass


        msg = "hi"
        s.send(msg)

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


