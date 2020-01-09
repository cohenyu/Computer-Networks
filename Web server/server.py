import socket
import sys
import os


# This function read from the socket until the msg end with \r\n\r\n
def get_msg(client_socket):
    total_data = ''
    # try to get the msg
    try:
        data = client_socket.recv(1024)
        # if the msg is not empty, keep receve the data
    except socket.timeout:
        return total_data

    while data:
        total_data += data.decode()
        # if the msg end with \r\n\r\n - stop
        if total_data.endswith('\r\n\r\n'):
            break
        data = client_socket.recv(1024)
        #  return the data
    return total_data


# This function parses the massage of the client
def parse_msg(data):
    try:
        total_data = data.split('\r\n')
        conn_state = ''
        # get the file name
        file_name = total_data[0].split()[1]
        if file_name == '/':
            file_name += 'index.html'
        # get the connection - close / keep-alive
        for line in total_data:
            if line.startswith("Connection:"):
                conn_state = line.split()[1]
                break
        file_path = './files' + file_name
    except:
        conn_state = ''
        file_path = ''

    return file_path, conn_state


# This function creates the answer to the client and send the answer to him
def server_answer(file_path, conn_state, client_socket):
    # redirect -> result
    if file_path == './files/redirect':
        client_socket.send(('HTTP/1.1 301 Move Permanently\r\nConnection: close\r\nLocation: /result.html\r\n\r\n').encode())
    # if it's not a file -> not found
    elif not os.path.isfile(file_path):
        client_socket.send('HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n'.encode())
    # if it is a file
    else:
        # get the content of the file end the length
        content, length = get_content(file_path)
        header = 'HTTP/1.1 200 OK\r\nConnection: ' + conn_state + '\r\nContent-Length: ' + str(length) + '\r\n\r\n'
        # send the answer to the client
        client_socket.send(header.encode() + content)


# This function read the file until EOF
def read_file(f):
    data = f.read()
    f.close()
    return data


# This function gets the content of the file
def get_content(file_path):
    # if the file is jpg or ico -> read in binary
    if file_path.endswith('jpg') or file_path.endswith('ico'):
        f = open(file_path, 'rb')
        data = read_file(f)
    # else just read in string
    else:
        f = open(file_path, 'r')
        data = read_file(f).encode()
    return data, len(data)


if __name__ == "__main__":
    # create the socket in tcp
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = '0.0.0.0'
    server_port = int(sys.argv[1])
    server.bind((server_ip, server_port))
    server.listen(1)
    conn_state = 'keep-alive'
    # accept a client
    client_socket, client_address = server.accept()
    close = False

    while True:
        # set the timeout to 1 sec
        client_socket.settimeout(1)
        # get the request from the client
        data = get_msg(client_socket)
        # if data is not empty
        if data:
            # print the request
            print(data)
            # get the file path and the connection value
            file_path, conn_state = parse_msg(data)
            # send the answer to the client
            server_answer(file_path, conn_state, client_socket)
        # if dat is empty close the connection
        else:
             close = True
        #   if the connection is close in one way -> close thr connection and accept new client
        if close or conn_state == "close":
            client_socket.close()
            client_socket, client_address = server.accept()
            close = False
