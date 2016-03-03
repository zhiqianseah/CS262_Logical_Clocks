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


        print 'Server started!'


        self._hostSocket.bind((host, port))        # Bind to the port

    # Define a function for the thread
    def receive_thread(self, threadName, ):
        print 'Waiting for clients...'
        self._hostSocket.listen(5)                 # Now wait for client connection.
        self._c, self._addr = self._hostSocket.accept()     # Establish connection with client.
        print 'Got connection from', self._addr
        while True:
            msg = self._c.recv(1024)
            print self._addr, ' >> ', msg
            self._c.send(msg);

    def wait_for_connection(self):

        thread.start_new_thread( self.receive_thread, ("Thread-1", ) )
        print "sleep"
        time.sleep(10)
        print "waking"
          #c.close()                # Close the connection

    def connect_to(self, port):
        s = socket.socket()         # Create a socket object to connect to other VMs
        host = socket.gethostname() # Get local machine name

        print 'Connecting to ', host, port
        s.connect((host, port))

        msg = "hi"
        s.send(msg)
        msg = s.recv(1024)
        print '>> ', msg
        self._clientports.append(port)
        self._clientSockets[port] = s

    def send_msg(self, port, msg):
        print "Sending message"
        self._clientSockets[port].send(msg)

    def receive_msg(self, port, msg):
        pass

    def runVM(self, duration):
        start = time.time()
        while True:

            rand_num = random.randrange(1, 11)
            print "tick:", rand_num
            if (rand_num == 1):
                self.send_msg(self._clientports[0], "hi")

            if (time.time() - start) > duration:
                break
            time.sleep(self._interval - ((time.time() - start) % self._interval))


