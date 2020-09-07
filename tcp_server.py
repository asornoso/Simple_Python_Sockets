import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

#Create server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Assign ip and port
server.bind( (bind_ip, bind_port) )

#Begin listening
server.listen(5)

print("[*] Listening on %s:%d " % (bind_ip, bind_port))

#client-handling thread
def handle_client( client_socket ):

    #printout receiving data
    request = client_socket.recv(1024)
    print("[*] Received: %s" % request)

    #send back data to the client
    client_socket.send("TCP ACK!")
    client_socket.close()

while True:
    client, addr = server.accept()

    print("[*] Accepted connection from : %s:%d" % (addr[0], addr[1]))

    #start new thread to handle new client
    client_thread = threading.Thread(target=handle_client, args=(client,))
    client_thread.start()