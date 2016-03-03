from VirtualMachine import VirtualMachine

#Create a VM with port number and the frequency of ticks
VM2 =VirtualMachine(2002, 1)

#connect to the other 2 VMs
VM2.connect_to(2003)
VM2.wait_for_connection()
VM2.connect_to(2001)
VM2.wait_for_connection()

VM2.send_msg(2001, "Hello There from VM2")

VM2.runVM(60)