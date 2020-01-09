import socket
import sys
import os


# This function get string of files and make the string to be list of files
def parse_files(data):
    files_locations = []
    if data:
        for item in data.split(','):
            files_locations.append(item.split(' '))
    return files_locations


# This function read from the socket until the msg end with \n
def get_msg(client_socket):
    data = client_socket.recv(1024)
    total_data = ''
    while data:
        total_data += data.decode()
        if total_data.endswith('\n'):
            break
        data = client_socket.recv(1024)
    return total_data[:-1]


# In this function the user is like server and listen to users, end send them a file
def start_listen(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    while True:
        # get a user
        client_socket, client_address = server.accept()
        # get the file name that the user wants
        file_name = get_msg(client_socket)
        f = open(file_name, 'rb')
        # sending the file
        data = f.read(1024)
        while data:
            client_socket.send(data)
            data = f.read(1024)
        f.close()
        client_socket.close()


# In this case the user wants to supply file and to be like server
def listener(server_ip, server_port):
    port = sys.argv[4]
    # take all the file in the current directory
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    files_str = ','.join(files)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))
    # send to the server this data
    s.send(('1 ' + port + ' ' + files_str + '\n').encode())
    s.close()
    # start to be like a "server"
    start_listen(int(port))


# This function gets the file from other client
def file_query(info):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = info[1]
    port = int(info[2])
    file_name = info[0]
    # connect to the other client
    s.connect((ip, port))
    # send the file name
    s.send((file_name + '\n').encode())
    # receive the file
    file = s.recv(1024)
    with open(file_name, 'wb') as f:
        while file:
            f.write(bytes(file))
            file = s.recv(1024)
    f.close()
    s.close()


# In this case the user wants to get files
def user(server_ip, server_port):
    # ask the user which file
    msg = input('Search: ')
    while not msg == 'quit':
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, server_port))
        # send to the server the search key
        s.send(('2 ' + msg + '\n').encode())
        # get from the server the list of files that contains this key
        data = get_msg(s)
        s.close()
        dic = {}
        if data:
            files_locations = parse_files(data)
            files_locations.sort(key=lambda x: (str(x).split(' ')[0]))
            for index, file in enumerate(files_locations, 1):
                print(index, file[0])
                dic.update({index: file})
        # choose the file
        msg = input('Choose: ')
        try:
            file_query(dic[int(msg)])
        except:
            pass
        msg = input('Search: ')


if __name__ == "__main__":
    mode = int(sys.argv[1])
    dest_ip = sys.argv[2]
    dest_port = int(sys.argv[3])
    if mode == 0:
        listener(dest_ip, dest_port)
    elif mode == 1:
        user(dest_ip, dest_port)

