from VirtualMachine import VirtualMachine
import time
import random

#Create a VM with port number and the frequency of ticks
#TODO: change 0.1 to random time ticks
VM3 =VirtualMachine(2003, random.randint(1, 6), 'VM3')

#connect to the other 2 VMs
time.sleep(5) # wait until other VMs have started
VM3.connect_to(2001)
VM3.wait_for_connection(2002)
time.sleep(2)
VM3.connect_to(2002)
VM3.wait_for_connection(2001)

VM3.runVM(60)