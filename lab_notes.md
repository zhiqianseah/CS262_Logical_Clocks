# Lab notes

## Starting out
First, we tried to find some examples on client-server sockets online. Played around with a simple client-server example taken
http://stackoverflow.com/questions/12993276/errno-10061-no-connection-could-be-made-because-the-target-machine-actively-re

Created VirtualMachine class, and two VM.py to simulate 2 machines.

Set up client and server connections in the VM. It works!

## Problem 1: How to get the third machine in?

Fixed Problem 1 trivially by creating a similar VM3.py. Got the 3 VMs to establish connection with each other in a round-table fashion. Also added a short delay at the beginning for the other VMs to startup, and created a script (for Mac) that launches all the VMs in separate terminal windows simultaneously.

## Problem 2: When/How to set the VM to receive the message during the run? --> figure out the interval runs first

So, try to get the VM to execute every X second. Found some help at: 
http://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python

Got the VM to run in ticks. The way is to pause for the time difference between VM_time_interval and elapsed_time

Next, moved the `receiving_msg` part to a separate thread, so that the VM can run independently of the receiving of messages. Help with multi-threading code is taken from http://www.tutorialspoint.com/python/python_multithreading.htm. This should fix Problem 2.

Since TCP/IP is a stream protocol, we create a basic message protocol by prepending messages with the message length. This way we can handled multiple messages in the socket. Reference: http://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data.

## Problem 3: handle exception when one of the VM stops running and closes the socket

Changed s.connect() to s.connect_ex() so that the VM will not crash/throw exception when the other VM has not booted up yet

Fixed Problem 3 by putting a try-exception block in the receive thread

## Problem 4: No multiprocessing code allowed within each VM

Feedback during class that python threads are not real threads since the GIL prohibits multi-threaded code from operating as it should with Python. Separate processes are also prohibited for this assignment. Put receive "thread" back to the main process, and listen on the socket in a non-blocking manner. This is done by 'socket.setblocking(False)' Help taken from
http://stackoverflow.com/questions/16745409/what-does-pythons-socket-recv-return-for-non-blocking-sockets-if-no-data-is-r 

We had to interleave socket reading into the rest of the execution. Specifically, on each clock tick we:

 - Get all messages from the 2 sockets that connect to the other VMs.
 - Add all messages into the message queue
 - Go ahead with the actual operation for the current tick
 - Pause for the remainder of the tick

## Problem 5 How do we get messages from the socket to the message queue?
At the start of each tick, we check both sockets for messages and add those messages to the message queue (implemented as a `deque` in Python to get FIFO behavior.)

We elected to check the first client socket for all messages, and then the second client socket for all messages. If there's a large number of messages in the socket, then it could mean that there are multiple messages from the first client which are going to all be ahead of the messages from the second client. There are two sub-problems that arise here:

 1. The actual ordering of messages from the first and second client was probably some interleaved combination.
 2. For two given messages `M1` and `M2`, sent in that order from the *same* client, it is not guaranteed with TCP/IP that `M1` will arrive before `M2`.

Issue 1 cannot be resolved only with the use of logical clocks; we would need physical clocks to determine the ordering of messages between multiple clients. Therefore, while we could have randomised the ordering, it should at least in theory be equally valid to simply append all messages from client 1 into the message queue, followed by all messages from client 2.

With issue 2, as the Lamport (1978) article points out, we can address this with the use of message numbers. Analogously, we can use the logical clock times in the message to determine the ordering.

## Problem 6: Structure of the messages
As pointed out earlier, we prepend the length of the message to the message in order to get it from the socket. However, we also need to send the logical clock time to the other process. To keep things simple, we use a message format `Hello <target(s)> <logical clock>`. The sender is known based on the socket from which the message was received. Then it is a simple matter of string splitting to get the logical clock value.

## Experiments
### Standard, 1 minute runs x 5 times
Examination of the logs make it clear that the jumps in the logical values occur when receiving a message which contains a higher logical clock value. The reason the sender of the message would have a higher logical clock value is because they have a higher tick rate (or lower interval between actions.) Since every clock cycle increases the local logical clock by 1, the faster the clock rate, the higher the logical clock value becomes.

Accordingly, the difference between the clock rate becomes a major factor in how much the logical clock jumps around. Specifically, if there are two machines with a big difference in clock rate, then a message from the faster machine will cause a jump in the logical clock rate, assuming an even faster machine has not already caused a jump recently.

In the 3 VM case where they are started simultaneously, suppose the speed of `P1` >= `P2` >= `P3` and `P3` receives a message:

 - `P3` will always have a jump in its logical clock after a message from `P3` if `P1` and `P2` > `P3` and the last event for `P3` was:
	 - an internal event, or
	 - the last event was receiving a message from `P2`, and the speed of `P1` > `P2`
 - Similarly, if `P2` sends a message to `P3`, then `P3`'s logical clock will be updated unless `P3` receives a message from `P1` recently enough to have `P3`'s logical clock to still be higher than `P2`.

If `P2` receives a message:

 - `P2` will have a jump in the logical clock if:
 	- It receives a message from `P3` and speed of`P3` > `P2`, or
 	- It receives a message from `P1` and `P1` was updated by a message from `P3` recently enough to have `P1`'s logical clock to still be higher than `P2`.

If `P3 receives a message:

	- There will be no jumps in its logical clock.

If speed of `P1` = `P2` = `P3` then there will be no jumps in the logical clock time.

The frequency of the clock rate will also affect the size of the message queue. The bigger the difference, the larger the message queue tends to get since the slower VM will have paused during the time the faster VM has been sending out messages.

### Smaller variation in clock rates and small probability of internal events

Some key observations when we make these changes:

- The frequency of the logical clock updates is not affected by the smaller variation in the clock rates, since it only depends on the relative relation between the clock rates. However, overall the updates are more frequent since the probability of external events are greater (and hence more updates to the logical clocks occur.)
- The magnitude of the logical clock updates is smaller since now there is less time for the difference in the logical clocks to grow large since all VMs tend to move at similar rates. In addition, the larger probability of external events means that the logical clock times are propagated more often to the other VMs, so update magnitude tends to shrink.
- The message queues sizes can be larger or smaller because:
	- There is less opportunity for the faster processes to send more messages since they all operate closer in speed, so this would tend to decrease the message queue size, but
	- Increasing the probability of external events has the effect of increasing the total number of messages being sent, so this would tend to increase the message queue size.
 
