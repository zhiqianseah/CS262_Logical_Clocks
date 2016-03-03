from VirtualMachine import VirtualMachine

#Create a VM with port number and the frequency of ticks
VM1 =VirtualMachine(2001, 1)

#connect to the other 2 VMs
VM1.wait_for_connection()
VM1.connect_to(2002)
VM1.wait_for_connection()
VM1.connect_to(2003)

VM1.send_msg(2002, "Hello There from VM1")

VM1.runVM(60)