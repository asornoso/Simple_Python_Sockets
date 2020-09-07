import socket

#Server info
host = "0.0.0.0"
port = 9998

#create socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#send data to server
client.sendto("AAABBBCCC", (host, port) )

#receive data
data, addr = client.recvfrom(4096)
print("[*] Recieved %s from: %s:%d" %(data, addr[0], addr[1]))

