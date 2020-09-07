import random
import socket

bind_ip = "0.0.0.0"
bind_port = 9998

#create server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind( (bind_ip, bind_port) )

print("[*] Listening on %s:%d " % (bind_ip, bind_port))

while True:
    data, addr = server.recvfrom(1024)
    print("[*] Recieved %s from: %s:%d" %(data, addr[0], addr[1]))
    server.sendto("UDP ACK!", (addr[0], addr[1]) )
