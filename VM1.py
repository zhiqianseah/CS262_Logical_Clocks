from VirtualMachine import VirtualMachine
import time
import random

#Create a VM with port number and the frequency of ticks
VM1 =VirtualMachine(2001, random.randint(1, 6), 'VM1')

#connect to the other 2 VMs
time.sleep(5) # wait until other VMs have started
VM1.wait_for_connection(2003)
VM1.connect_to(2002)
time.sleep(2)
VM1.wait_for_connection(2002)
VM1.connect_to(2003)


VM1.runVM(60)