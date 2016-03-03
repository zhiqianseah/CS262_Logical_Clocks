from VirtualMachine import VirtualMachine
VM2 =VirtualMachine(2002, 2)
VM2.connect_to(2001)
VM2.wait_for_connection()

VM2.send_msg(2001, "Hello There from VM2")

VM2.runVM(60)