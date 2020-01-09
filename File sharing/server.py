import socket
import sys

ports = {}
files = {}


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


# This function parses the massage of the client
def parse_msg(data):
    # check if the massage is by the rule
    try:
        task_num = int(data.split()[0])
    except:
        task_num = -1
    # and if there is a message after a number
    try:
        data_msg = data.split(None, 1)[1]
    except:
        data_msg = ''
    return task_num, data_msg


# This function connects a client to the files system
def connection(client_info, msg):
    port = msg.split(' ')[0]
    file_names = msg.split(' ')[1]
    file_list = [file for file in file_names.split(',')]
    # update the dictionaries with the client's port and the list of files
    ports.update({client_info: port})
    files.update({client_info: file_list})


# This function provides to the client the possible files and their location
def search(client_socket, data):
    sharing = []
    # search a file with the substring provided by the client
    if data:
        for client, file_list in files.items():
            for file in file_list:
                if file.find(data) != -1:
                    sharing.append(file + ' ' + str(client[0]) + ' ' + ports[client])
    # send to the client the list of files and their locations
    if sharing:
        msg = ','.join(sharing) + '\n'
    else:
        msg = '\n'
    client_socket.send(msg.encode())


if __name__ == "__main__":
    # create the socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = '0.0.0.0'
    server_port = int(sys.argv[1])
    server.bind((server_ip, server_port))
    server.listen(5)
    while True:
        # connect to a user and get his msg
        client_socket, client_address = server.accept()
        data = get_msg(client_socket)
        task, msg = parse_msg(data)
        # the user want to supply files
        if task == 1:
            client_socket.close()
            connection(client_address, msg)
        #  the user wants files
        elif task == 2:
            search(client_socket, msg)
            client_socket.close()
        # not an option
        else:
            client_socket.close()

