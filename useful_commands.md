# Useful commands

`nmcli device status` (can also be `nmcli dev`) - quick overview of network devices

`ip link show` - show IP devices and their statuses

dd if=/dev/zero of=upload_test bs=1M count=size_in_megabytes

# Transceiver order
The bracket has an L shape, the transceiver closest to that bracket is 0.

# Reference Documents
https://askubuntu.com/questions/22835/how-to-network-two-ubuntu-computers-using-ethernet-without-a-router/

# How to Git

First, get the data from the repository
`git pull`

Next, add all your changes
`git add -A`

Then, commit your files with a message
`git commit -m "Relevant message"`

Now, push your changes, and pull again to syncronize
`git push`
`git pull`

# How to Link 
1. Open Advanced Network Communication
2. Go to the list of networks and click on them, check the name and make sure that it matches the name you want to set as receiver
3. Go to IPv4 Settings
4. Switch the Method to Manual and assign an IP address (such as 10.0.0.1 on receiver) and a Net Mask (such as 225.225.225.0)
5. Repeat on the other end and set the IP address to be similar the to receiver (such as 10.0.0.2 for sender)
6. 


