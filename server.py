import socket, sys, os


# checks if the port is in the legal interval (from the lecture)
def legal_port(port):
    return port > 0 and port <= 2 ** 16


def main():
    port = int(sys.argv[1])
    if not legal_port(port):
        print("illegal port")
        exit()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', port))
    server.listen(5)

    connection = 'close'

    while True:
        if connection == 'close':
            # set timeout to old timeout for accept
            client_socket, client_address = server.accept()

        # set a timeout for recv for 1 second - close client if time has expired
        try:
            client_socket.settimeout(1)
            data = client_socket.recv(1024)
        except:
            client_socket.close()
            connection = 'close'
            continue

        # extract name of file
        lines = data.decode().split('\r\n')
        file_name = "files" + lines[0].split(" ")[1]

        print(data.decode())

        # if the msg is empty
        if len(data.decode()) == 0:
            client_socket.close()
            connection = 'close'
            continue

        # if request is /
        if file_name == "files/":
            file_name = "files/index.html"

        # if request ifs /redirect
        if file_name == "files/redirect":
            connection = "close"
            client_socket.send(
                ("HTTP/1.1 301 Moved Permanently\r\nConnection: " + connection + "\r\nLocation: /result.html"
                 + "\r\n\r\n").encode())
            client_socket.close()

        # if file exists
        elif os.path.isfile(file_name):

            # get current connection request
            for line in lines:
                if line.split(" ")[0] == 'Connection:':
                    connection = line.split(" ")[1]

            # send msg to client
            size = os.path.getsize(file_name)
            client_socket.send(("HTTP/1.1 200 OK\r\nConnection: " + connection + "\r\nContent-Length: " + str(
                size) + "\r\n\r\n").encode())

            # read content of file and send to client
            file = open(file_name, "rb")
            content = file.read()
            client_socket.send(content)
            file.close()

            # close connection if needed
            if connection == 'close':
                client_socket.close()

        # if file does not exist
        else:
            connection = 'close'
            client_socket.send(("HTTP/1.1 404 Not Found\r\nConnection: " + connection + "\r\n\r\n").encode())
            client_socket.close()


if __name__ == "__main__":
    main()
