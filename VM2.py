from VirtualMachine import VirtualMachine
import time
#Create a VM with port number and the frequency of ticks
VM2 =VirtualMachine(2002, 0.1)

#connect to the other 2 VMs
time.sleep(5) # wait until other VMs have started
VM2.connect_to(2003)
VM2.wait_for_connection(2001)
time.sleep(2)
VM2.connect_to(2001)
VM2.wait_for_connection(2003)

VM2.runVM(60)