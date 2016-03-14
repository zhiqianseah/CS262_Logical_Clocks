import socket
import sched, time
import random
import errno
import struct
from collections import deque
import os
class VirtualMachine:

    def __init__(self, port, ticks, name):
        self._hostSocket = socket.socket()         # Create a socket object
        self._interval = 1.0/ticks
        self._clientSockets = {}
        self._clientReceive = {}
        self._clientports = []
        host = '0.0.0.0'            # Get local machine name
        self._threadcounter = 0
        self._name = name
        self._clock = 0
        self._maxR = 11 # Maximum for random number generator

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

        self._clientports.append(port)
        self._clientSockets[port] = s

    # Reference: http://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
    # ------------------------------------------
    def send_msg(self, msg, client, log_f = None):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        port = self._clientports[client]

        try:
            self._clientSockets[port].sendall(msg)
        except:
            print "Enable to send message. Socket may be closed"

        log_str = 'Message sent to client #{} (port {}): {}\tSys. time: {}\tLogical ' \
                          'clock: {}\n'.format(client, port, msg, time.time(), self._clock)
        if log_f:
            log_f.write(log_str)

        print log_str

    def recvall(self, n, client):
        # Helper function to recv n bytes or return None if EOF is hit
        data = ''
        while len(data) < n:
            packet = None
            try:
                packet = self._clientReceive[self._clientports[client]].recv(n - len(data))
            except socket.error, e:
                pass
            if not packet:
                return None
            data += packet
        return data

    def recv_msg(self, client):
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(4, client)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(msglen, client)

    # ------------------------------------------

    def addToMq(self, client, q):
        allM = []
        while True:
            msg = self.recv_msg(client)
            if msg is None:
                break
            _, _, l_clock = msg.split()
            allM.append( (l_clock, msg) )

        # Make sure we add earlier messages to the message queue first
        for _, msg in sorted(allM):
            q.append((client, msg))

    def runVM(self, duration):
        start = time.time()
        path, filename = os.path.split(os.path.realpath(__file__))
        f = open(path + '/' + str(self._name)+'.log', 'w')
        f.write('Tick interval (s): {}\n'.format(self._interval))
        q = deque()
        while True:
            # Add all messages from the socket into the message queue to be processed
            self.addToMq(0, q)
            self.addToMq(1, q)

            # Update logical clock time for this virtual machine
            self._clock += 1

            # Process messages in the queue first
            if q:
                client, msg = q.popleft()
                mqLen = len(q)
                # Update logical clocks
                cmd, targets, l_clock = msg.split()
                l_clock = int(l_clock)
                if self._clock < l_clock + 1:
                    log_str = '\tUpdating clock from {} to {}\n'.format(self._clock, l_clock + 1)
                    print log_str
                    f.write(log_str)
                    self._clock = l_clock + 1

                log_str = 'Message received from client #{} (port {}): {}\tQueue length: {}\tSys. time: {}\tLogical ' \
                          'clock: {' \
                          '}\n'.format(client, self._clientports[client], msg, mqLen, time.time(), self._clock)
                f.write(log_str)
                print log_str


            else:
                # Generate a random number to see next course of action
                rand_num = random.randrange(1, self._maxR)
                print "tick:", rand_num
                if rand_num == 1:
                    self.send_msg("Hello {} {}".format(rand_num, self._clock), 0, f)
                elif rand_num == 2:
                    self.send_msg("Hello {} {}".format(rand_num, self._clock), 1, f)
                elif rand_num == 3:
                    self.send_msg("Hello both {}".format(self._clock), 0, f)
                    self.send_msg("Hello both {}".format(self._clock), 1, f)
                else:
                    log_str = 'Internal event\tSys. time: {}\tLogical Clock: {}\n'.format(time.time(), self._clock)
                    f.write(log_str)
                    print log_str

            # Stop the VM when the duration is up
            if (time.time() - start) > duration:
                f.close()
                break

            # Pause for the remainder of a tick
            time.sleep(self._interval - ((time.time() - start) % self._interval))
