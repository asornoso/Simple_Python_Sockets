import socket

host = "0.0.0.0"
port = 9999

#socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    #Connect the client to the server
    client.connect( (host, port))

    #send data to server
    #client.send("GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n")
    client.send("Hello....")

    #receive data back from server:
    response = client.recv(4096)

    if len(response) == 0:
        print("Server has disconnect...")
    else:
        print(response)


except:
    print("Error connection/sending data/receiving data...")


client.close()
