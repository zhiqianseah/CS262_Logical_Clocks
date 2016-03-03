from VirtualMachine import VirtualMachine

VM1 =VirtualMachine(2001, 1)
VM1.wait_for_connection()
VM1.connect_to(2002)

VM1.send_msg(2002, "Hello There from VM1")

VM1.runVM(60)