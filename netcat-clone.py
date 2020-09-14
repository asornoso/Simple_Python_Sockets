import sys
import socket
import getopt
import threading
import subprocess

#Global Variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

#print out usage legend
def usage():
    print("Netcat clone tool")
    print()
    print("Usage: netcat-clone.py -t target_host -p port")
    print("-l --listen                  - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run     - execute the given file upon receiving a connection")
    print("-c --command                 - initialize a command shell")
    print("-u --upload=destination      - upon receiving connection upload a file and write to [destination]")
    print()
    print()
    print("Exampels: ")
    print("netcat-clone.py -t 192.168.0.1 -p 5555 -l -c")
    print("netcat-clone.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("netcat-clone.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/psswd\"")
    print("echo 'ABCDEFGHI' | .netcat-clone.py -t 192.168.11.12 -p 135")
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    #read in command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
            ["help", "listen","execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "-help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"

    #Listen or send data from stdin
    if not listen and len(target) and port > 0:
        #read in from commandline
        #stdin is blocking, use ctrl+d to end
        buffer = sys.stdin.read()

        #send data
        client_sender(buffer)

    #listen and upload/execute
    if listen:
        server_loop()


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #connect to host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:
            #Wait for data back
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response)

            #wait for more input
            buffer = raw_input("")
            buffer += "\n"

            #send buffer
            client.send(buffer)

    except:
        print("[*] Exception! Exiting")
        client.close()


def server_loop():
    global target

    #if no target, listen on all
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    print("[*] Server listening on %s:%d" % (target, port))

    while True:
        client_socket, addr = server.accept()

        #new thread to handle client
        client_thread = threading.Thread(target = client_handler, args = (client_socket,))
        client_thread.start()


def run_command(command):
    #trim newline
    command = command.rstrip()

    #run command and get output
    try:
        output = subprocess.check_output(command, stderr = subprocess.STDOUT, shell = True)
    except:
        output = "Failed to execute command.\r\n"

    #send output to client
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    #check for upload
    if len(upload_destination):
        #read in file & write to destination
        file_buffer = ""

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        #write out file
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            #acknowledge that we wrote the file
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    #check for execution
    if len(execute):
        #run
        output = run_command(execute)

        client_socket.send(output)

    #loop if command shell requested
    if command:
        while True:
            #show prompt
            client_socket.send("<netcat-clone:#> ")

            #receive until a newline
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            #send back the output
            response = run_command(cmd_buffer)

            #send back response
            client_socket.send(response)


main()
