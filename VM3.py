from VirtualMachine import VirtualMachine

#Create a VM with port number and the frequency of ticks
VM3 =VirtualMachine(2003, 1)

#connect to the other 2 VMs
VM3.connect_to(2001)
VM3.wait_for_connection()
VM3.connect_to(2002)
VM3.wait_for_connection()

VM3.runVM(60)